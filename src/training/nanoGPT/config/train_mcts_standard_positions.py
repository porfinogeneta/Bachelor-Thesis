# train a miniature character-level shakespeare model
# good for debugging and playing on macbooks and such


# python3 train.py --out_dir="out_standard_positions_bs_1600" --dataset="standard_positions" --compile=True --device="cuda"  config/train_standard_positions.py | tee "/home/ubuntu/Bachelor-Thesis/src/training/train_configs/standard_positions/out_standard_positions_bs_1600.txt"

out_dir = 'mcts_standard_positions/out_mcts_standard_positions_bs_2560v2'
eval_interval = 250 # keep frequent because we'll overfit
eval_iters = 200
log_interval = 10 # don't print too too often

# we expect to overfit on this small dataset, so only save when val improves
always_save_checkpoint = False

# wandb_log = False # override via command line if you like
# wandb_project = 'standard_positions'
# wandb_run_name = 'mini-gpt'

dataset = 'mcts_standard_positions'
gradient_accumulation_steps = 1
# 64 256
batch_size = 192
block_size = 2560 # context of up to 2816 previous characters
# batch_size = 64
# block_size = 2866 # context of up to 2816 previous characters

# batch_size = 16
# block_size = 128 # context of up to 2816 previous characters

# baby GPT model :)
n_layer = 6
n_head = 6
n_embd = 384
dropout = 0.2

learning_rate = 1e-3 # with baby networks can afford to go a bit higher
max_iters = 5000
lr_decay_iters = 5000 # make equal to max_iters usually
min_lr = 1e-4 # learning_rate / 10 usually
beta2 = 0.99 # make a bit bigger because number of tokens per iter is small

warmup_iters = 100 # not super necessary potentially

# on macbook also add
# device = 'mps'  # run on cpu only
# compile = False # do not torch compile the model
