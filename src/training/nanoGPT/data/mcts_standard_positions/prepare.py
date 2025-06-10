import os
import requests
import tiktoken
import numpy as np
from src.training.nanoGPT.tokenizer.tokenizer import Tokenizer


# input_file_path = "/Users/szymon/Documents/Bachelor-Thesis/src/training/corpora/standard_positions/standard_positions20k.txt"
input_file_path = "/home/ubuntu/Bachelor-Thesis/src/training/corpora/mcts_standard_positions/mcts_standard_positions_20k.txt"
with open(input_file_path, 'r', encoding='utf-8') as f:
    data = f.read().replace("\n", " ")
n = len(data)
train_data = data[:int(n*0.9)]
val_data = data[int(n*0.9):]



def encode_large_file(tokenizer, file_path):
    encoded_tokens = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Process the file in chunks to avoid memory issues
        chunk_size = 1024 * 1024  # 1MB chunks
        prev_chunk = ""
        chunk_idx = 0
        while True:
            # print(chunk_idx)
            chunk = prev_chunk
            prev_chunk = ""
            chunk += f.read(chunk_size)
            if chunk == "":
                break
                
            # Replace newlines with spaces in this chunk
            chunk = chunk.replace("\n", " ")
            # Split and encode
            chunk_tokens = chunk.split()
            
            for token in chunk_tokens:
                try:
                    encoded_tokens.append(tokenizer.stoi[token])
                except KeyError:
                    # save token that was cut in middle
                    prev_chunk = token
                    # print(f"Unknown token: {token}")
            chunk_idx += 1
    
    return encoded_tokens



# # encode with tiktoken gpt2 bpe
# enc = tiktoken.get_encoding("gpt2")
# train_ids = enc.encode_ordinary(train_data)
# print(train_ids)
# val_ids = enc.encode_ordinary(val_data)

# print(train_data)

# input_file_path = "/Users/szymon/Documents/Bachelor-Thesis/src/training/corpora/standard_positions/standard_positions20k.txt"
tokenizer = Tokenizer()

# Encode the entire file
all_encoded_ids = encode_large_file(tokenizer, input_file_path)

# Calculate split point (90% train, 10% val)
split_point = int(len(all_encoded_ids) * 0.9)
train_ids = all_encoded_ids[:split_point]
val_ids = all_encoded_ids[split_point:]

print(f"tokens amount {tokenizer.get_tokens_size()}")
print(f"train has {len(train_ids):,} tokens")
print(f"val has {len(val_ids):,} tokens")

# export to bin files
train_ids = np.array(train_ids, dtype=np.uint16)
val_ids = np.array(val_ids, dtype=np.uint16)
train_ids.tofile(os.path.join(os.path.dirname(__file__), 'train.bin'))
val_ids.tofile(os.path.join(os.path.dirname(__file__), 'val.bin'))

# train.bin has 301,966 tokens
# val.bin has 36,059 tokens
