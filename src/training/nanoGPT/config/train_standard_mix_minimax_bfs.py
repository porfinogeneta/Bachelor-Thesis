# train a miniature character-level shakespeare model
# good for debugging and playing on macbooks and such
out_dir = 'models/standard_mix_minimax_bfs/out_standard_mix_minimax_bfs_bs_1664'
eval_interval = 250 # keep frequent because we'll overfit
eval_iters = 200
log_interval = 10 # don't print too too often

# we expect to overfit on this small dataset, so only save when val improves
always_save_checkpoint = False

# wandb_log = False # override via command line if you like
# wandb_project = 'standard_positions'
# wandb_run_name = 'mini-gpt'

dataset = 'mix_minimax_bfs' # name of the training corpus
gradient_accumulation_steps = 1
# 64 256
# batch_size = 64
# block_size = 1984
batch_size = 16
block_size = 1664
# batch_size = 128
# block_size = 4352 # context of up to 2816 previous characters
# batch_size = 64
# block_size = 2866 # context of up to 2816 previous characters

# batch_size = 8
# block_size = 64

# baby GPT model :)
n_layer = 6
n_head = 6
n_embd = 384
dropout = 0.2

learning_rate = 1e-3 # with baby networks can afford to go a bit higher
max_iters = 10000
lr_decay_iters = 10000 # make equal to max_iters usually
min_lr = 1e-4 # learning_rate / 10 usually
beta2 = 0.99 # make a bit bigger because number of tokens per iter is small

warmup_iters = 100 # not super necessary potentially

# # on macbook also add
# device = 'mps'  # run on cpu only
# compile = False # do not torch compile the model
#step 10000: train loss 0.4371, val loss 0.4422