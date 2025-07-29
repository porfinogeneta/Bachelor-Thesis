"""
This training script can be run both on a single gpu in debug mode,
and also in a larger training run with distributed data parallel (ddp).

To run on a single GPU, example:
$ python train.py --batch_size=32 --compile=False

To run with DDP on 4 gpus on 1 node, example:
$ torchrun --standalone --nproc_per_node=4 train.py

To run with DDP on 4 gpus across 2 nodes, example:
- Run on the first (master) node with example IP 123.456.123.456:
$ torchrun --nproc_per_node=8 --nnodes=2 --node_rank=0 --master_addr=123.456.123.456 --master_port=1234 train.py
- Run on the worker node:
$ torchrun --nproc_per_node=8 --nnodes=2 --node_rank=1 --master_addr=123.456.123.456 --master_port=1234 train.py
(If your cluster does not have Infiniband interconnect prepend NCCL_IB_DISABLE=1)
"""

import os
import time
import math
import pickle
from contextlib import nullcontext

import numpy as np
import torch.nn.functional as F
import torch
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group

from model import GPTConfig, GPT, tokenizer

# -----------------------------------------------------------------------------
# default config values designed to train a gpt2 (124M) on OpenWebText
# I/O
out_dir = 'out'
eval_interval = 2000
log_interval = 1
eval_iters = 200
eval_only = False # if True, script exits right after the first eval
always_save_checkpoint = True # if True, always save a checkpoint after each eval
init_from = 'scratch' # 'scratch' or 'resume' or 'gpt2*'
# wandb logging
wandb_log = False # disabled by default
wandb_project = 'owt'
wandb_run_name = 'gpt2' # 'run' + str(time.time())
# data
dataset = 'openwebtext'
gradient_accumulation_steps = 5 * 8 # used to simulate larger batch sizes
batch_size = 12 # if gradient_accumulation_steps > 1, this is the micro-batch size
block_size = 1024
# model
n_layer = 12
n_head = 12
n_embd = 768
dropout = 0.0 # for pretraining 0 is good, for finetuning try 0.1+
bias = False # do we use bias inside LayerNorm and Linear layers?
# adamw optimizer
learning_rate = 6e-4 # max learning rate
max_iters = 600000 # total number of training iterations
weight_decay = 1e-1
beta1 = 0.9
beta2 = 0.95
grad_clip = 1.0 # clip gradients at this value, or disable if == 0.0
# learning rate decay settings
decay_lr = True # whether to decay the learning rate
warmup_iters = 2000 # how many steps to warm up for
lr_decay_iters = 600000 # should be ~= max_iters per Chinchilla
min_lr = 6e-5 # minimum learning rate, should be ~= learning_rate/10 per Chinchilla
# DDP settings
backend = 'nccl' # 'nccl', 'gloo', etc.
# system
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1' etc., or try 'mps' on macbooks
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32', 'bfloat16', or 'float16', the latter will auto implement a GradScaler
compile = True # use PyTorch 2.0 to compile the model to be faster

# MODIFICATION
SNAKE0_TOKEN = 3
SNAKE1_TOKEN = 4
SNAKE0_WINS_TOKEN = 200
SNAKE1_WINS_TOKEN = 201
TIE_TOKEN = 202
POSITION_TOKEN_MIN = 6
POSITION_TOKEN_MAX = 149

# Weighting parameters
winning_snake_weight = 2.0  # Weight multiplier for winning snake's position tokens
losing_snake_weight = 1.0   # Weight for losing snake's position tokens
tie_weight = 1.0           # Weight when game is a tie
non_position_weight = 1.0   # Weight for non-position tokens


# -----------------------------------------------------------------------------
config_keys = [k for k,v in globals().items() if not k.startswith('_') and isinstance(v, (int, float, bool, str))]
exec(open('configurator.py').read()) # overrides from command line or config file
config = {k: globals()[k] for k in config_keys} # will be useful for logging
# -----------------------------------------------------------------------------

# various inits, derived attributes, I/O setup
ddp = int(os.environ.get('RANK', -1)) != -1 # is this a ddp run?
if ddp:
    init_process_group(backend=backend)
    ddp_rank = int(os.environ['RANK'])
    ddp_local_rank = int(os.environ['LOCAL_RANK'])
    ddp_world_size = int(os.environ['WORLD_SIZE'])
    device = f'cuda:{ddp_local_rank}'
    torch.cuda.set_device(device)
    master_process = ddp_rank == 0 # this process will do logging, checkpointing etc.
    seed_offset = ddp_rank # each process gets a different seed
    # world_size number of processes will be training simultaneously, so we can scale
    # down the desired gradient accumulation iterations per process proportionally
    assert gradient_accumulation_steps % ddp_world_size == 0
    gradient_accumulation_steps //= ddp_world_size
else:
    # if not ddp, we are running on a single gpu, and one process
    master_process = True
    seed_offset = 0
    ddp_world_size = 1
tokens_per_iter = gradient_accumulation_steps * ddp_world_size * batch_size * block_size
print(f"tokens per iteration will be: {tokens_per_iter:,}")

if master_process:
    os.makedirs(out_dir, exist_ok=True)
torch.manual_seed(1337 + seed_offset)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
# note: float16 data type will automatically use a GradScaler
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)



def create_winning_snake_weighted_mask(input_tokens, target_tokens):
    """
    Create a weighted mask that prioritizes position tokens from the winning snake.
    
    Args:
        input_tokens: tensor of shape (batch_size, seq_len) - input sequence
        target_tokens: tensor of shape (batch_size, seq_len) - target sequence
    
    Returns:
        weights: tensor of same shape with weights for each target token
        masked_targets: target tokens with non-position tokens set to -100
        metrics: dict with statistics about the weighting
    """
    batch_size, seq_len = target_tokens.shape
    weights = torch.ones_like(target_tokens, dtype=torch.float32, device=target_tokens.device)
    masked_targets = target_tokens.clone()
    
    # Statistics tracking
    total_position_tokens = 0
    winning_snake_position_tokens = 0
    losing_snake_position_tokens = 0
    tie_position_tokens = 0
    
    # Process each sequence in the batch
    for batch_idx in range(batch_size):
        input_seq = input_tokens[batch_idx]
        target_seq = target_tokens[batch_idx]
        
        # Find the winner for this game by looking for winner tokens in the input sequence
        # since batches start with the winner token we are interseted in first occurence
        winner = None

        for t in input_seq:
            if t == SNAKE0_WINS_TOKEN:
                winner = 0
                break
            elif t == SNAKE1_WINS_TOKEN:
                winner = 1
                break
            elif t == TIE_TOKEN:
                winner = 2
                break

        # if SNAKE0_WINS_TOKEN in input_seq:
        #     winner = 0  # Snake 0 wins
        # elif SNAKE1_WINS_TOKEN in input_seq:
        #     winner = 1  # Snake 1 wins
        # elif TIE_TOKEN in input_seq:
        #     winner = 2  # Tie
        
        # If we can't determine the winner, use default weights
        if winner is None:
            # Set non-position tokens to -100 (ignored)
            position_mask = (target_seq >= POSITION_TOKEN_MIN) & (target_seq <= POSITION_TOKEN_MAX)
            masked_targets[batch_idx][~position_mask] = -100
            continue
        
        # Process each token in the sequence
        for token_idx in range(seq_len):
            target_token = target_seq[token_idx].item()
            
            # Check if this is a position token
            if POSITION_TOKEN_MIN <= target_token <= POSITION_TOKEN_MAX:
                total_position_tokens += 1
                
                # Determine which snake this position token belongs to
                # Look at the previous token in the input sequence
                # and than apply weights based on the winnner
                if token_idx > 0:
                    prev_token = input_seq[token_idx - 1].item()
                    
                    if prev_token == SNAKE0_TOKEN:  # This position belongs to snake 0
                        if winner == 0:  # Snake 0 wins
                            weights[batch_idx, token_idx] = winning_snake_weight
                            winning_snake_position_tokens += 1
                        elif winner == 1:  # Snake 1 wins (snake 0 loses)
                            weights[batch_idx, token_idx] = losing_snake_weight
                            losing_snake_position_tokens += 1
                        else:  # Tie
                            weights[batch_idx, token_idx] = tie_weight
                            tie_position_tokens += 1
                            
                    elif prev_token == SNAKE1_TOKEN:  # This position belongs to snake 1
                        if winner == 1:  # Snake 1 wins
                            weights[batch_idx, token_idx] = winning_snake_weight
                            winning_snake_position_tokens += 1
                        elif winner == 0:  # Snake 0 wins (snake 1 loses)
                            weights[batch_idx, token_idx] = losing_snake_weight
                            losing_snake_position_tokens += 1
                        else:  # Tie
                            weights[batch_idx, token_idx] = tie_weight
                            tie_position_tokens += 1
                    else:
                        # Previous token is not a snake token, use default weight
                        weights[batch_idx, token_idx] = non_position_weight
                else:
                    # First token, use default weight
                    weights[batch_idx, token_idx] = non_position_weight
            else:
                # Non-position token - set to -100 (ignored by loss)
                masked_targets[batch_idx, token_idx] = -100
                weights[batch_idx, token_idx] = 0.0  # Will be ignored anyway
    
    metrics = {
        'total_position_tokens': total_position_tokens,
        'winning_snake_tokens': winning_snake_position_tokens,
        'losing_snake_tokens': losing_snake_position_tokens,
        'tie_tokens': tie_position_tokens,
        'avg_weight': weights[masked_targets != -100].mean().item() if (masked_targets != -100).any() else 0.0
    }
    
    return weights, masked_targets, metrics

# poor man's data loader
data_dir = os.path.join('data', dataset)
def get_batch(split):
    # We recreate np.memmap every batch to avoid a memory leak, as per
    # https://stackoverflow.com/questions/45132940/numpy-memmap-memory-usage-want-to-iterate-once/61472122#61472122
    if split == 'train':
        data = np.memmap(os.path.join(data_dir, 'train.bin'), dtype=np.uint16, mode='r')
    else:
        data = np.memmap(os.path.join(data_dir, 'val.bin'), dtype=np.uint16, mode='r')

    # gather all start tokens
    all_start_token_indices = np.where(data == 0)[0]
    # get games that that fit in the context window (for both x and y)
    valid_start_indices_np = all_start_token_indices[all_start_token_indices <= len(data) - 1 - block_size]
    start_tensor = torch.from_numpy(valid_start_indices_np)

    
    # sanity check if all positions that are divisible by 4362 are actually start positions
    assert np.all(data[valid_start_indices_np] == 0), "Not all positions extractet by numpy are 0"    
    

    # choose samples indices uniformly at random
    indices = torch.randperm(start_tensor.size(0))[:batch_size]
 
    ix = start_tensor[indices]
 
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])

    weights, y_masked, mask_metrics = create_winning_snake_weighted_mask(x, y)
    
    if device_type == 'cuda':
        # pin arrays x,y, which allows us to move them to GPU asynchronously (non_blocking=True)
        x = x.pin_memory().to(device, non_blocking=True)
        y_masked = y_masked.pin_memory().to(device, non_blocking=True)
        weights = weights.pin_memory().to(device, non_blocking=True)
    else:
        x, y_masked, weights = x.to(device), y_masked.to(device), weights.to(device)
    
    return x, y_masked, weights, mask_metrics

# # poor man's data loader
# data_dir = os.path.join('data', dataset)
# def get_batch(split):
#     # We recreate np.memmap every batch to avoid a memory leak, as per
#     # https://stackoverflow.com/questions/45132940/numpy-memmap-memory-usage-want-to-iterate-once/61472122#61472122
#     if split == 'train':
#         data = np.memmap(os.path.join(data_dir, 'train.bin'), dtype=np.uint16, mode='r')
#     else:
#         data = np.memmap(os.path.join(data_dir, 'val.bin'), dtype=np.uint16, mode='r')
#     ix = torch.randint(len(data) - block_size, (batch_size,))
#     x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
#     y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])
#     if device_type == 'cuda':
#         # pin arrays x,y, which allows us to move them to GPU asynchronously (non_blocking=True)
#         x, y = x.pin_memory().to(device, non_blocking=True), y.pin_memory().to(device, non_blocking=True)
#     else:
#         x, y = x.to(device), y.to(device)
#     return x, y

# init these up here, can override if init_from='resume' (i.e. from a checkpoint)

def compute_weighted_loss_and_metrics(logits, targets, weights):
    """
    Compute weighted loss and additional metrics for winning snake prioritized training.
    
    Args:
        logits: model predictions of shape (batch_size, seq_len, vocab_size)
        targets: masked targets of shape (batch_size, seq_len) where -100 = ignore
        weights: weight tensor of shape (batch_size, seq_len)
    
    Returns:
        loss: weighted cross entropy loss
        metrics: dict with additional metrics
    """
    # Reshape for loss computation
    logits_flat = logits.view(-1, logits.size(-1))  # (batch_size * seq_len, vocab_size)
    targets_flat = targets.view(-1)  # (batch_size * seq_len,)
    weights_flat = weights.view(-1)  # (batch_size * seq_len,)
    
    # Compute per-token losses (without reduction)
    token_losses = F.cross_entropy(logits_flat, targets_flat, ignore_index=-100, reduction='none')
    
    # Apply weights only to non-ignored tokens
    valid_mask = targets_flat != -100
    weighted_losses = token_losses * weights_flat
    
    # Compute final weighted loss
    if valid_mask.sum() > 0:
        loss = weighted_losses[valid_mask].sum() / valid_mask.sum()
    else:
        loss = torch.tensor(0.0, device=logits.device)
    
    # Compute additional metrics
    with torch.no_grad():
        valid_targets = valid_mask.sum().item()
        total_targets = targets_flat.numel()
        
        # Compute accuracy on valid targets
        if valid_targets > 0:
            predictions = logits_flat.argmax(dim=-1)
            correct = ((predictions == targets_flat) & valid_mask).sum().item()
            accuracy = correct / valid_targets
            
            # Compute weighted accuracy
            correct_weights = weights_flat[(predictions == targets_flat) & valid_mask].sum().item()
            total_weights = weights_flat[valid_mask].sum().item()
            weighted_accuracy = correct_weights / total_weights if total_weights > 0 else 0.0
        else:
            accuracy = 0.0
            weighted_accuracy = 0.0
        
        metrics = {
            'valid_targets': valid_targets,
            'total_targets': total_targets,
            'target_ratio': valid_targets / total_targets if total_targets > 0 else 0.0,
            'accuracy': accuracy,
            'weighted_accuracy': weighted_accuracy,
            'avg_weight': weights_flat[valid_mask].mean().item() if valid_targets > 0 else 0.0
        }
    
    return loss, metrics


iter_num = 0
best_val_loss = 1e9

# attempt to derive vocab_size from the dataset
meta_path = os.path.join(data_dir, 'meta.pkl')
meta_vocab_size = None
if os.path.exists(meta_path):
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    meta_vocab_size = meta['vocab_size']
    print(f"found vocab_size = {meta_vocab_size} (inside {meta_path})")

# model init
model_args = dict(n_layer=n_layer, n_head=n_head, n_embd=n_embd, block_size=block_size,
                  bias=bias, vocab_size=None, dropout=dropout) # start with model_args from command line
if init_from == 'scratch':
    # init a new model from scratch
    print("Initializing a new model from scratch")
    # determine the vocab size we'll use for from-scratch training
    if meta_vocab_size is None:
        print("defaulting to vocab_size of our transformer to 384")
    model_args['vocab_size'] = meta_vocab_size if meta_vocab_size is not None else tokenizer.get_tokens_size()
    gptconf = GPTConfig(**model_args)
    model = GPT(gptconf)
elif init_from == 'resume':
    print(f"Resuming training from {out_dir}")
    # resume training from a checkpoint.
    ckpt_path = os.path.join(out_dir, 'ckpt.pt')
    checkpoint = torch.load(ckpt_path, map_location=device)
    checkpoint_model_args = checkpoint['model_args']
    # force these config attributes to be equal otherwise we can't even resume training
    # the rest of the attributes (e.g. dropout) can stay as desired from command line
    for k in ['n_layer', 'n_head', 'n_embd', 'block_size', 'bias', 'vocab_size']:
        model_args[k] = checkpoint_model_args[k]
    # create the model
    gptconf = GPTConfig(**model_args)
    model = GPT(gptconf)
    state_dict = checkpoint['model']
    # fix the keys of the state dictionary :(
    # honestly no idea how checkpoints sometimes get this prefix, have to debug more
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
    model.load_state_dict(state_dict)
    iter_num = checkpoint['iter_num']
    best_val_loss = checkpoint['best_val_loss']
elif init_from.startswith('gpt2'):
    print(f"Initializing from OpenAI GPT-2 weights: {init_from}")
    # initialize from OpenAI GPT-2 weights
    override_args = dict(dropout=dropout)
    model = GPT.from_pretrained(init_from, override_args)
    # read off the created config params, so we can store them into checkpoint correctly
    for k in ['n_layer', 'n_head', 'n_embd', 'block_size', 'bias', 'vocab_size']:
        model_args[k] = getattr(model.config, k)
# crop down the model block size if desired, using model surgery
if block_size < model.config.block_size:
    model.crop_block_size(block_size)
    model_args['block_size'] = block_size # so that the checkpoint will have the right value
model.to(device)

# initialize a GradScaler. If enabled=False scaler is a no-op
scaler = torch.cuda.amp.GradScaler(enabled=(dtype == 'float16'))

# optimizer
optimizer = model.configure_optimizers(weight_decay, learning_rate, (beta1, beta2), device_type)
if init_from == 'resume':
    optimizer.load_state_dict(checkpoint['optimizer'])
checkpoint = None # free up memory

# compile the model
if compile:
    print("compiling the model... (takes a ~minute)")
    unoptimized_model = model
    model = torch.compile(model) # requires PyTorch 2.0

# wrap model into DDP container
if ddp:
    model = DDP(model, device_ids=[ddp_local_rank])

# # helps estimate an arbitrarily accurate loss over either split using many batches
# @torch.no_grad()
# def estimate_loss():
#     out = {}
#     model.eval()
#     for split in ['train', 'val']:
#         losses = torch.zeros(eval_iters)
#         for k in range(eval_iters):
#             X, Y = get_batch(split)
#             with ctx:
#                 logits, loss = model(X, Y)
#             losses[k] = loss.item()
#         out[split] = losses.mean()
#     model.train()
#     return out

@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        total_metrics = {
            'valid_targets': 0, 'total_targets': 0, 'correct': 0, 'weighted_correct': 0,
            'total_weights': 0, 'winning_snake_tokens': 0, 'losing_snake_tokens': 0, 'tie_tokens': 0
        }
        
        for k in range(eval_iters):
            X, Y, weights, mask_metrics = get_batch(split)
            with ctx:
                logits, _ = model(X, Y)  # We'll compute loss ourselves
                loss, metrics = compute_weighted_loss_and_metrics(logits, Y, weights)
            
            losses[k] = loss.item()
            # Accumulate metrics
            total_metrics['valid_targets'] += metrics['valid_targets']
            total_metrics['total_targets'] += metrics['total_targets']
            if metrics['valid_targets'] > 0:
                total_metrics['correct'] += metrics['accuracy'] * metrics['valid_targets']
                total_metrics['weighted_correct'] += metrics['weighted_accuracy'] * metrics['avg_weight'] * metrics['valid_targets']
                total_metrics['total_weights'] += metrics['avg_weight'] * metrics['valid_targets']
            
            # Accumulate mask metrics
            total_metrics['winning_snake_tokens'] += mask_metrics['winning_snake_tokens']
            total_metrics['losing_snake_tokens'] += mask_metrics['losing_snake_tokens']
            total_metrics['tie_tokens'] += mask_metrics['tie_tokens']
        
        avg_loss = losses.mean()
        avg_accuracy = total_metrics['correct'] / total_metrics['valid_targets'] if total_metrics['valid_targets'] > 0 else 0.0
        avg_weighted_accuracy = total_metrics['weighted_correct'] / total_metrics['total_weights'] if total_metrics['total_weights'] > 0 else 0.0
        avg_target_ratio = total_metrics['valid_targets'] / total_metrics['total_targets'] if total_metrics['total_targets'] > 0 else 0.0
        
        out[split] = {
            'loss': avg_loss,
            'accuracy': avg_accuracy,
            'weighted_accuracy': avg_weighted_accuracy,
            'target_ratio': avg_target_ratio,
            'winning_snake_tokens': total_metrics['winning_snake_tokens'],
            'losing_snake_tokens': total_metrics['losing_snake_tokens'],
            'tie_tokens': total_metrics['tie_tokens']
        }
    
    model.train()
    return out





# learning rate decay scheduler (cosine with warmup)
def get_lr(it):
    # 1) linear warmup for warmup_iters steps
    if it < warmup_iters:
        return learning_rate * (it + 1) / (warmup_iters + 1)
    # 2) if it > lr_decay_iters, return min learning rate
    if it > lr_decay_iters:
        return min_lr
    # 3) in between, use cosine decay down to min learning rate
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    assert 0 <= decay_ratio <= 1
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio)) # coeff ranges 0..1
    return min_lr + coeff * (learning_rate - min_lr)

# logging
if wandb_log and master_process:
    import wandb
    wandb.init(project=wandb_project, name=wandb_run_name, config=config)

# training loop
X, Y, weights, _ = get_batch('train') # fetch the very first batch
t0 = time.time()
local_iter_num = 0 # number of iterations in the lifetime of this process
raw_model = model.module if ddp else model # unwrap DDP container if needed
running_mfu = -1.0
while True:

    # determine and set the learning rate for this iteration
    lr = get_lr(iter_num) if decay_lr else learning_rate
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    # evaluate the loss on train/val sets and write checkpoints
    if iter_num % eval_interval == 0 and master_process:
        losses = estimate_loss()
        print(f"step {iter_num}: train loss {losses['train']['loss']:.4f}, val loss {losses['val']['loss']:.4f}")
        print(f"train acc {losses['train']['accuracy']:.4f}, val acc {losses['val']['accuracy']:.4f}")
        print(f"train weighted acc {losses['train']['weighted_accuracy']:.4f}, val weighted acc {losses['val']['weighted_accuracy']:.4f}")
        print(f"train target ratio {losses['train']['target_ratio']:.4f}, val target ratio {losses['val']['target_ratio']:.4f}")
        print(f"winning snake tokens: train {losses['train']['winning_snake_tokens']}, val {losses['val']['winning_snake_tokens']}")
        print(f"losing snake tokens: train {losses['train']['losing_snake_tokens']}, val {losses['val']['losing_snake_tokens']}")
        
        if wandb_log:
            wandb.log({
                "iter": iter_num,
                "train/loss": losses['train']['loss'],
                "val/loss": losses['val']['loss'],
                "train/accuracy": losses['train']['accuracy'],
                "val/accuracy": losses['val']['accuracy'],
                "train/weighted_accuracy": losses['train']['weighted_accuracy'],
                "val/weighted_accuracy": losses['val']['weighted_accuracy'],
                "train/target_ratio": losses['train']['target_ratio'],
                "val/target_ratio": losses['val']['target_ratio'],
                "train/winning_snake_tokens": losses['train']['winning_snake_tokens'],
                "val/winning_snake_tokens": losses['val']['winning_snake_tokens'],
                "train/losing_snake_tokens": losses['train']['losing_snake_tokens'],
                "val/losing_snake_tokens": losses['val']['losing_snake_tokens'],
                "lr": lr,
                "mfu": running_mfu*100,
            })
            
        if losses['val']['loss'] < best_val_loss or always_save_checkpoint:
            best_val_loss = losses['val']['loss']
            if iter_num > 0:
                checkpoint = {
                    'model': raw_model.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'model_args': model_args,
                    'iter_num': iter_num,
                    'best_val_loss': best_val_loss,
                    'config': config,
                }
                print(f"saving checkpoint to {out_dir}")
                torch.save(checkpoint, os.path.join(out_dir, 'ckpt.pt'))

    
    if iter_num == 0 and eval_only:
        break

    # forward backward update, with optional gradient accumulation to simulate larger batch size
    # and using the GradScaler if data type is float16
    for micro_step in range(gradient_accumulation_steps):
        if ddp:
            # in DDP training we only need to sync gradients at the last micro step.
            # the official way to do this is with model.no_sync() context manager, but
            # I really dislike that this bloats the code and forces us to repeat code
            # looking at the source of that context manager, it just toggles this variable
            model.require_backward_grad_sync = (micro_step == gradient_accumulation_steps - 1)
        # with ctx:
        #     logits, loss = model(X, Y)
        #     loss = loss / gradient_accumulation_steps # scale the loss to account for gradient accumulation

        with ctx:
            # Get model predictions
            logits, _ = model(X, Y)  # We'll compute loss ourselves
            # Compute weighted loss
            loss, _ = compute_weighted_loss_and_metrics(logits, Y, weights)
            loss = loss / gradient_accumulation_steps # scale the loss to account for gradient accumulation
        
        # immediately async prefetch next batch while model is doing the forward pass on the GPU
        X, Y, weights, _ = get_batch('train')
        # backward pass, with gradient scaling if training in fp16
        scaler.scale(loss).backward()
    # clip the gradient
    if grad_clip != 0.0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
    # step the optimizer and scaler if training in fp16
    scaler.step(optimizer)
    scaler.update()
    # flush the gradients as soon as we can, no need for this memory anymore
    optimizer.zero_grad(set_to_none=True)

    # timing and logging
    t1 = time.time()
    dt = t1 - t0
    t0 = t1
    if iter_num % log_interval == 0 and master_process:
        # get loss as float. note: this is a CPU-GPU sync point
        # scale up to undo the division above, approximating the true total loss (exact would have been a sum)
        lossf = loss.item() * gradient_accumulation_steps
        if local_iter_num >= 5: # let the training loop settle a bit
            mfu = raw_model.estimate_mfu(batch_size * gradient_accumulation_steps, dt)
            running_mfu = mfu if running_mfu == -1.0 else 0.9*running_mfu + 0.1*mfu
        print(f"iter {iter_num}: loss {lossf:.4f}, time {dt*1000:.2f}ms, mfu {running_mfu*100:.2f}%")
    iter_num += 1
    local_iter_num += 1

    # termination conditions
    if iter_num > max_iters:
        break
# python train.py config/train_standard_positions.py --device=mps
if ddp:
    destroy_process_group()
