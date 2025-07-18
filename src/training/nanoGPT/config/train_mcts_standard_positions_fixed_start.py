# train a miniature character-level shakespeare model
# good for debugging and playing on macbooks and such

out_dir = 'mcts_standard_positions/out_mcts_standard_positions_fixed_bs_2560'
eval_interval = 250 # keep frequent because we'll overfit
eval_iters = 200
log_interval = 10 # don't print too too often

# we expect to overfit on this small dataset, so only save when val improves
always_save_checkpoint = False


dataset = 'mcts_standard_positions'
gradient_accumulation_steps = 1
# 64 256
# batch_size = 320
# block_size = 1472
batch_size = 192
block_size = 2560


# baby GPT model :)
n_layer = 6
n_head = 6
n_embd = 384
dropout = 0.2

# n_layer = 12
# n_head = 12
# n_embd = 768
# dropout = 0.0

learning_rate = 1e-3 # with baby networks can afford to go a bit higher
max_iters = 5000
# max_iters = 7000
lr_decay_iters = 5000 # make equal to max_iters usually
# lr_decay_iters = 7000
min_lr = 1e-4 # learning_rate / 10 usually
beta2 = 0.99 # make a bit bigger because number of tokens per iter is small

warmup_iters = 100 # not super necessary potentially

# on macbook also add
# device = 'mps'  # run on cpu only
# compile = False # do not torch compile the model
