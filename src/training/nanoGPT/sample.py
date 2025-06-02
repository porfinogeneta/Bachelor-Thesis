












# """
# Sample from a trained model
# """
# import os
# import pickle
# from contextlib import nullcontext
# import torch
# from src.training.nanoGPT.model import GPTConfig, GPT
# from src.training.nanoGPT.tokenizer.tokenizer import Tokenizer

# # -----------------------------------------------------------------------------
# init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
# out_dir = 'out' # ignored if init_from is not 'resume'
# start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, use as: "FILE:prompt.txt"
# num_samples = 10 # number of samples to draw
# max_new_tokens = 500 # number of tokens generated in each sample
# temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
# top_k = 10 # retain only the top_k most likely tokens, clamp others to have 0 probability
# seed = 1337
# device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
# dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
# compile = False # use PyTorch 2.0 to compile the model to be faster
# exec(open('configurator.py').read()) # overrides from command line or config file
# # -----------------------------------------------------------------------------

# torch.manual_seed(seed)
# torch.cuda.manual_seed(seed)
# torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
# torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
# device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
# ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
# ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# # model
# if init_from == 'resume':
#     # init from a model saved in a specific directory
#     ckpt_path = os.path.join(out_dir, 'ckpt.pt')
#     checkpoint = torch.load(ckpt_path, map_location=device)
#     gptconf = GPTConfig(**checkpoint['model_args'])
#     model = GPT(gptconf)
#     state_dict = checkpoint['model']
#     unwanted_prefix = '_orig_mod.'
#     for k,v in list(state_dict.items()):
#         if k.startswith(unwanted_prefix):
#             state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
#     model.load_state_dict(state_dict)
# elif init_from.startswith('gpt2'):
#     # init from a given GPT-2 model
#     model = GPT.from_pretrained(init_from, dict(dropout=0.0))

# model.eval()
# model.to(device)
# if compile:
#     model = torch.compile(model) # requires PyTorch 2.0 (optional)

# # look for the meta pickle in case it is available in the dataset folder
# load_meta = False
# if init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']: # older checkpoints might not have these...
#     meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
#     load_meta = os.path.exists(meta_path)
# if load_meta:
#     print(f"Loading meta from {meta_path}...")
#     with open(meta_path, 'rb') as f:
#         meta = pickle.load(f)
#     # TODO want to make this more general to arbitrary encoder/decoder schemes
#     stoi, itos = meta['stoi'], meta['itos']
#     encode = lambda s: [stoi[c] for c in s]
#     decode = lambda l: ''.join([itos[i] for i in l])
# else:
#     # ok let's assume gpt-2 encodings by default
#     # print("No meta.pkl found, assuming GPT-2 encodings...")
#     # enc = tiktoken.get_encoding("gpt2")
#     # encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
#     # decode = lambda l: enc.decode(l)

#     # assume custom tokenizer encoding
#     print("No meta.pkl found, assuming custom encodings...")
#     tokenizer = Tokenizer(10, 10)
#     encode = lambda s: tokenizer.encode(s)
#     decode = lambda l: tokenizer.decode(l)


# # encode the beginning of the prompt
# if start.startswith('FILE:'):
#     with open(start[5:], 'r', encoding='utf-8') as f:
#         start = f.read()
# start_ids = encode(start)
# x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])



# #  python sample.py --out_dir=out-standard_pos --device=mps --start="<START> S0 R1C8 L0 A87 A12 A19 A44 A26 S1 R8C0 L0 A87 A12 A19 A44 A26 S0 R1C9 L0 A87 A12 A44 A26 A48 S1 " --max_new_tokens=1
# # run generation
# with torch.no_grad():
#     print('---------------')
#     with ctx:
#         y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
#         print(decode(y[0].tolist()))
#         print('---------------')

# # # run generation
# # with torch.no_grad():
# #     print('---------------')
# #     with ctx:
# #         for k in range(num_samples):
# #             y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
# #             print(decode(y[0].tolist()))
# #             print('---------------')









"""
Sample from a trained model
"""
import os
import pickle
from contextlib import nullcontext
import torch
from src.training.nanoGPT.model import GPTConfig, GPT
from src.training.nanoGPT.tokenizer.tokenizer import Tokenizer
from src.consts import NANOGPT_DIR
import pathlib
from typing import List

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

# # -----------------------------------------------------------------------------
# init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
# out_dir = 'out' # ignored if init_from is not 'resume'
# start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, use as: "FILE:prompt.txt"
# num_samples = 10 # number of samples to draw
# max_new_tokens = 500 # number of tokens generated in each sample
# temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
# top_k = 10 # retain only the top_k most likely tokens, clamp others to have 0 probability
# seed = 1337
# device = 'cpu' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
# dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
# compile = False # use PyTorch 2.0 to compile the model to be faster
# # exec(open('/Users/szymon/Documents/Bachelor-Thesis/src/training/nanoGPT/configurator.py').read()) # overrides from command line or config file
# # -----------------------------------------------------------------------------


# import sys
# from ast import literal_eval

# for arg in sys.argv[1:]:
#     if '=' not in arg:
#         # assume it's the name of a config file
#         assert not arg.startswith('--')
#         config_file = arg
#         print(f"Overriding config with {config_file}:")
#         with open(config_file) as f:
#             print(f.read())
#         exec(open(config_file).read())
#     else:
#         # assume it's a --key=value argument
#         assert arg.startswith('--')
#         key, val = arg.split('=')
#         key = key[2:]
#         if key in globals():
#             try:
#                 # attempt to eval it it (e.g. if bool, number, or etc)
#                 attempt = literal_eval(val)
#             except (SyntaxError, ValueError):
#                 # if that goes wrong, just use the string
#                 attempt = val
#             # ensure the types match ok
#             assert type(attempt) == type(globals()[key])
#             # cross fingers
#             print(f"Overriding: {key} = {attempt}")
#             globals()[key] = attempt
#         else:
#             raise ValueError(f"Unknown config key: {key}")




# torch.manual_seed(seed)
# torch.cuda.manual_seed(seed)
# torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
# torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
# device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
# ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
# ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# # model
# if init_from == 'resume':
#     # init from a model saved in a specific directory
#     ckpt_path = os.path.join(out_dir, 'ckpt.pt')
#     checkpoint = torch.load(ckpt_path, map_location=device)
#     gptconf = GPTConfig(**checkpoint['model_args'])
#     model = GPT(gptconf)
#     state_dict = checkpoint['model']
#     unwanted_prefix = '_orig_mod.'
#     for k,v in list(state_dict.items()):
#         if k.startswith(unwanted_prefix):
#             state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
#     model.load_state_dict(state_dict)
# elif init_from.startswith('gpt2'):
#     # init from a given GPT-2 model
#     model = GPT.from_pretrained(init_from, dict(dropout=0.0))

# model.eval()
# model.to(device)
# if compile:
#     model = torch.compile(model) # requires PyTorch 2.0 (optional)

# # look for the meta pickle in case it is available in the dataset folder
# load_meta = False
# if init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']: # older checkpoints might not have these...
#     meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
#     load_meta = os.path.exists(meta_path)
# if load_meta:
#     print(f"Loading meta from {meta_path}...")
#     with open(meta_path, 'rb') as f:
#         meta = pickle.load(f)
#     # TODO want to make this more general to arbitrary encoder/decoder schemes
#     stoi, itos = meta['stoi'], meta['itos']
#     encode = lambda s: [stoi[c] for c in s]
#     decode = lambda l: ''.join([itos[i] for i in l])
# else:
#     # ok let's assume gpt-2 encodings by default
#     # print("No meta.pkl found, assuming GPT-2 encodings...")
#     # enc = tiktoken.get_encoding("gpt2")
#     # encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
#     # decode = lambda l: enc.decode(l)

#     # assume custom tokenizer encoding
#     print("No meta.pkl found, assuming custom encodings...")
#     tokenizer = Tokenizer(10, 10)
#     encode = lambda s: tokenizer.encode(s)
#     decode = lambda l: tokenizer.decode(l)


def configure_model(model_name, device):
    init_from = 'resume'
    seed = 1337
    dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
    

    # CONFIGURE GPT
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
    torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
    device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
    ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
    ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)


    out_dir = NANOGPT_DIR / pathlib.Path(model_name)

    # logger.debug(model_name)

    # model
    if init_from == 'resume':
        # init from a model saved in a specific directory
        ckpt_path = os.path.join(out_dir, 'ckpt.pt')
        checkpoint = torch.load(ckpt_path, map_location=device)
        gptconf = GPTConfig(**checkpoint['model_args'])
        model = GPT(gptconf)
        state_dict = checkpoint['model']
        unwanted_prefix = '_orig_mod.'
        for k,v in list(state_dict.items()):
            if k.startswith(unwanted_prefix):
                state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
        model.load_state_dict(state_dict)

    model.eval()
    model.to(device)
    if compile:
        model = torch.compile(model) # requires PyTorch 2.0 (optional)

    # look for the meta pickle in case it is available in the dataset folder
    load_meta = False
    if init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']: # older checkpoints might not have these...
        meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
        load_meta = os.path.exists(meta_path)
    if load_meta:
        print(f"Loading meta from {meta_path}...")
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
    else:
        # ok let's assume gpt-2 encodings by default
        # print("No meta.pkl found, assuming GPT-2 encodings...")
        pass


    return model, ctx
   

def generate_sequences(model, ctx, device, model_name: str, starts, temperature, legal_tokens:  List[List[str]], top_k):

    """
        This function is overloaded, if legal tokens are provided, legal token generation is used;
        if top_k is provided, then legal tokens should be None and normal generation is used.
    """

    # assertion for proper overloading
    assert((legal_tokens == None and top_k == 1) or (legal_tokens != None and top_k == None))

    # on each generation configure model anew
    model, ctx = configure_model(model_name=model_name, device=device)

    max_new_tokens = 1

    tokenizer = Tokenizer(10, 10)
    encode = lambda s: tokenizer.encode(s)
    decode = lambda l: tokenizer.decode(l)



    start_ids = [encode(start) for start in starts]
    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...].reshape(len(starts), -1))


    if legal_tokens == None:
        assert top_k >= 1
        # print("NORMAL GENERATION\n\n")
        # run standard generation
        with torch.no_grad():
            with ctx:
                y = model.generate(x, max_new_tokens, temperature=temperature, top_k=1)
    else:
        
        assert top_k == None
        # for pos_token in legal_tokens:

        #     print(t)
        # enode legal tokens, [0] since encode returns a list
        encoded_legal_tokens = [[encode(t)[0] for t in token_tuple] for token_tuple in legal_tokens]
        # logger.info(encoded_legal_tokens)
        # print(encoded_legal_tokens)
        # run generation that excludes tokens
       
        with torch.no_grad():
            with ctx:
                y = model.generate_from_legal_tokens(x, max_new_tokens, temperature=temperature, legal_tokens=encoded_legal_tokens)

    return [decode(y_resp) for y_resp in y.tolist()]

# # # encode the beginning of the prompt
# if start.startswith('FILE:'):
#     with open(start[5:], 'r', encoding='utf-8') as f:
#         starts = [line.strip() for line in f]
# # starts = ["<START> <START> <START> S0 R1C8 L0 A87 A12 A19 A44 A26 S1 R8C0 L0 A87 A12 A19 A44 A26 S0 R1C9 L0 A87 A12 A44 A26 A48 S1 ",
# #           "<START> <START> <START> S0 R3C6 L0 A54 A23 A35 A87 A12 S1 R4C2 L0 A54 A23 A35 A87 A12 S0 R3C5 L0 A54 A23 A87 A12 A01 S1",
# #           "<START> S0 R7C4 L0 A81 A60 A85 A66 A45 S1 R8C4 L0 A81 A60 A85 A66 A45 S0 R7C5 L0 A81 A60 A85 A66 A45 S1 R8C5 L0"]

# start_ids = [encode(start) for start in starts]
# # start_ids = encode(start) * 10

# # print("=" * 10)
# # print(start_ids)

# x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...].reshape(len(starts), -1))




#  python sample.py --out_dir=out-standard_pos_1774_ctx_bs_64_baby --device=mps --start="<START> S0 R1C8 L0 A87 A12 A19 A44 A26 S1 R8C0 L0 A87 A12 A19 A44 A26 S0 R1C9 L0 A87 A12 A44 A26 A48 S1 " --max_new_tokens=1
# # run generation
# with torch.no_grad():
#     print('---------------')
#     with ctx:
#         y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
#         # print(decode(y[0].tolist()))
#         for y_resp in y.tolist():
#             print(decode(y_resp))
#             print('---------------')

    

# # # run generation
# # with torch.no_grad():
# #     print('---------------')
# #     with ctx:
# #         for k in range(num_samples):
# #             y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
# #             print(decode(y[0].tolist()))
# #             print('---------------')
