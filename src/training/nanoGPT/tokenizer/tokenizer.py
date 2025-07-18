from typing import List

class Tokenizer:

    def __init__(self, board_width = 10, board_height= 10):

        head_position_tokens = [f"R{i}C{j}" for j in range(-1, board_width + 1) for i in range(-1, board_height + 1)]
        tail_lengths_tokens = [f"L{l}" for l in range(0, board_width * board_height)] # tail cannot be longer than all available fields - 1
        snake_tokens = ["S0", "S1"]
        apple_tokens = [f"A{i}{j}" for j in range(board_width) for i in range(board_height)]
        special_tokens = ["<START>", "<END>", "<DEAD>", "<HELPER_TAG>"]

        self.all_tokens = special_tokens + snake_tokens + head_position_tokens + tail_lengths_tokens + apple_tokens

        # add special tokens for 64 training padding
        current_len = len(self.all_tokens)
        to_add = 64 - (current_len % 64)

        CORPORA_EXTENSION_TOKENS = ["<APPLES_UNCHANGED>", "<TAIL_END>"] 

        to_add -= len(CORPORA_EXTENSION_TOKENS)

        assert to_add > 0

        for i in range(to_add):
            self.all_tokens.append(f"<padding_token_{i}>")

        # we don't want to retrain everything, so let's just include extension tokens 
        # as the last ones
        for ext_token in CORPORA_EXTENSION_TOKENS:
            self.all_tokens.append(ext_token)

        # encoding dictionary -> put number for a specific string
        self.stoi = {token_str: i for i, token_str in enumerate(self.all_tokens)}
        # decoding dictionary -> put string in place of a specific number
        self.itos = {i: token_str for i, token_str in enumerate(self.all_tokens)}

    def encode(self, text: str):
        text_lst = text.split()
        return [self.stoi[token] for token in text_lst]
    
    def decode(self, encoded_lst: List[int]):
        # print(self.itos.keys())
        return " ".join([self.itos[i] for i in encoded_lst])
    
    def get_tokens_size(self):
        return len(self.all_tokens)



if __name__ == "__main__":
    tokenizer = Tokenizer(10, 10)
    # print(len(tokenizer.all_tokens))
    # encoded = tokenizer.encode("<START> S0 R1C8 L0 A87 A12 A19 A44 A26 S1 R8C0 L0 A87 A12 A19 A44 A26 S0 R1C9 L0 A87 A12 A44 A26 A48 S1 R8C1 L0 A87 A12 A44 A26 A48 S0 R2C9 L1 A87 A12 A44 A26 A48 S1 R8C2 L0 A87 A12 A44 A26 A48 S0 R2C8 L1 A87 A12 A44 A26 A48 S1 R8C3 L0 A87 A12 A44 A26 A48 S0 R3C8 L1 A87 A12 A44 A26 A48 S1 R8C4 L0 A87 A12 A44 A26 A48 S0 R4C8 L1 A87 A12 A44 A26 A39 S1 R8C5 L0 A87 A12 A44 A26 A39 S0 R4C9 L2 A87 A12 A44 A26 A39 S1 R8C6 L0 A87 A12 A44 A26 A39 S0 R3C9 L2 A87 A12 A44 A26 A10 S1 R8C7 L0 A12 A44 A26 A10 A94 S0 R2C9 L3 A12 A44 A26 A10 A94 S1 R9C7 L1 A12 A44 A26 A10 A94 S0 R2C8 L3 A12 A44 A26 A10 A94 S1 R9C6 L1 A12 A44 A26 A10 A94 S0 R2C7 L3 A12 A44 A26 A10 A94 S1 R9C5 L1 A12 A44 A26 A10 A94 S0 R2C6 L3 A12 A44 A10 A94 A22 S1 R9C4 L1 A12 A44 A10 A22 A82 S0 R3C6 L4 A12 A44 A10 A22 A82 S1 R8C4 L2 A12 A44 A10 A22 A82 S0 R4C6 L4 A12 A44 A10 A22 A82 S1 R8C3 L2 A12 A44 A10 A22 A82 S0 R4C5 L4 A12 A44 A10 A22 A82 S1 R8C2 L2 A12 A44 A10 A22 A03 S0 R4C4 L4 A12 A10 A22 A03 A49 S1 R7C2 L3 A12 A10 A22 A03 A49 S0 R3C4 L5 A12 A10 A22 A03 A49 S1 R6C2 L3 A12 A10 A22 A03 A49 S0 R2C4 L5 A12 A10 A22 A03 A49 S1 R5C2 L3 A12 A10 A22 A03 A49 S0 R2C3 L5 A12 A10 A22 A03 A49 S1 R4C2 L3 A12 A10 A22 A03 A49 S0 R2C2 L5 A12 A10 A03 A49 A08 S1 R3C2 L3 A12 A10 A03 A49 A08 S0 R1C2 L6 A10 A03 A49 A08 A85 S1 R3C1 L3 A10 A03 A49 A08 A85 S0 R1C1 L7 A10 A03 A49 A08 A85 S1 R2C1 L3 A10 A03 A49 A08 A85 S0 R1C0 L7 A03 A49 A08 A85 A71 S1 R2C0 L3 A03 A49 A08 A85 A71 S0 R0C0 L8 A03 A49 A08 A85 A71 S1 R3C0 L3 A03 A49 A08 A85 A71 S0 R0C1 L8 A03 A49 A08 A85 A71 S1 R4C0 L3 A03 A49 A08 A85 A71 S0 R0C2 L8 A03 A49 A08 A85 A71 S1 R5C0 L3 A03 A49 A08 A85 A71 S0 R0C3 L8 A49 A08 A85 A71 A48 S1 R6C0 L3 A49 A08 A85 A71 A48 S0 R0C4 L9 A49 A08 A85 A71 A48 S1 R7C0 L3 A49 A08 A85 A71 A48 S0 R0C5 L9 A49 A08 A85 A71 A48 S1 R7C1 L3 A49 A08 A85 A48 A67 S0 R0C6 L9 A49 A08 A85 A48 A67 S1 R8C1 L4 A49 A08 A85 A48 A67 S0 R0C7 L9 A49 A08 A85 A48 A67 S1 R8C2 L4 A49 A08 A85 A48 A67 S0 R0C8 L9 A49 A85 A48 A67 A43 S1 R8C3 L4 A49 A85 A48 A67 A43 S0 R1C8 L10 A49 A85 A48 A67 A43 S1 R8C4 L4 A49 A85 A48 A67 A43 S0 R2C8 L10 A49 A85 A48 A67 A43 S1 R8C5 L4 A49 A48 A67 A43 A70 S0 R3C8 L10 A49 A48 A67 A43 A70 S1 R7C5 L5 A49 A48 A67 A43 A70 S0 R4C8 L10 A49 A67 A43 A70 A45 S1 R6C5 L5 A49 A67 A43 A70 A45 S0 R4C9 L11 A67 A43 A70 A45 A60 S1 R6C6 L5 A67 A43 A70 A45 A60 S0 R5C9 L12 A67 A43 A70 A45 A60 S1 R6C7 L5 A43 A70 A45 A60 A46 S0 R5C8 L12 A43 A70 A45 A60 A46 S1 R5C7 L6 A43 A70 A45 A60 A46 S0 R6C8 L12 A43 A70 A45 A60 A46 S1 R4C7 L6 A43 A70 A45 A60 A46 S0 R7C8 L12 A43 A70 A45 A60 A46 S1 R4C6 L6 A43 A70 A45 A60 A11 S0 R8C8 L12 A43 A70 A45 A60 A11 S1 R4C5 L7 A43 A70 A60 A11 A93 S0 R9C8 L12 A43 A70 A60 A11 A93 S1 R4C4 L8 A43 A70 A60 A11 A93 S0 R9C7 L12 A43 A70 A60 A11 A93 S1 R4C3 L8 A70 A60 A11 A93 A54 S0 R9C6 L12 A70 A60 A11 A93 A54 S1 R5C3 L9 A70 A60 A11 A93 A54 S0 R9C5 L12 A70 A60 A11 A93 A54 S1 R5C4 L9 A70 A60 A11 A93 A31 S0 R9C4 L12 A70 A60 A11 A93 A31 S1 R6C4 L10 A70 A60 A11 A93 A31 S0 R9C3 L12 A70 A60 A11 A31 A99 S1 R6C3 L10 A70 A60 A11 A31 A99 S0 R8C3 L13 A70 A60 A11 A31 A99 S1 R6C2 L10 A70 A60 A11 A31 A99 S0 R7C3 L13 A70 A60 A11 A31 A99 S1 R6C1 L10 A70 A60 A11 A31 A99 S0 R7C2 L13 A70 A60 A11 A31 A99 S1 R6C0 L10 A70 A11 A31 A99 A29 S0 R7C1 L13 A70 A11 A31 A99 A29 S1 R7C0 L11 A11 A31 A99 A29 A28 S0 R8C1 L13 A11 A31 A99 A29 A28 S1 R8C0 L12 A11 A31 A99 A29 A28 S0 R9C1 L13 A11 A31 A99 A29 A28 S1 R9C0 L12 A11 A31 A99 A29 A28 S0 R9C2 L13 A11 A31 A99 A29 A28 S1 R10C0 L12 A11 A31 A99 A29 A28 S0 R8C2 L13 A11 A31 A99 A29 A28 S1 <DEAD> S0 R8C3 L13 A11 A31 A99 A29 A28 <END>")
    # print(encoded)
    # print(tokenizer.decode(encoded))

    print(tokenizer.encode("<START>"))