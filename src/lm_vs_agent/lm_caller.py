import subprocess
import os
import random
import re
from typing import List, Tuple
import copy

# logger
from src.logger.logger import setup_logger

# model sampling
from src.training.nanoGPT.sample import generate_sequences, configure_model

logger = setup_logger(__name__)

# BATCHED_DATA = "/Users/szymon/Documents/Bachelor-Thesis/src/llm_vs_agent/batched_data.txt"

"""
    Class calls specific llm and returns direction
"""
class LLMCaller:

    def __init__(self, model_name: str, device: str):
        # # self.model = model
        # self.MODEL, self.CTX = configure_model(model_name, device)
        self.device = device
        self.model_name = model_name
        # pass


    def is_move_valid(self, prev_head: Tuple[int, int], current_head: Tuple[int, int]):
        """
            Checks if move could be done from this head position
        """
        if prev_head == () or current_head == ():
            return False
        # up
        if (prev_head[0] - 1, prev_head[1]) == current_head:
            return True
        # down
        elif (prev_head[0] + 1, prev_head[1]) == current_head:
            return True
        # left
        elif (prev_head[0], prev_head[1] - 1) == current_head:
            return True
        # right
        elif (prev_head[0], prev_head[1] + 1) == current_head:
            return True
        else: return False


    def run_lm(self, prev_heads: List[Tuple[int, int]], game_sequences: List[str], legal_tokens:  List[List[str]] , top_k: int):
        """
            top_k=1 for token generation without legal_tokens constraint
            legal_tokens only != None if we want to provide legal tokens

            Runs standard generation but for each snake from the batch gives model valid directions
            that the snake could go. Valid direction is a move that don't cause the snake to die or
            to go out of game board bounds.

        """

        try: 
            # logger.info("="*20)
            # logger.info(f"Before gen: {game_sequences[0].split()}")
            generated_sequences = generate_sequences(model=None, ctx=None, device=self.device, model_name=self.model_name, starts=game_sequences, temperature=0.8, legal_tokens=legal_tokens, top_k=top_k)
            # logger.info(generated_sequences)
            # logger.info(f"After gen: {generated_sequences[0].split()}")
            # logger.info(f"After gen: {generated_sequences[0].split()[-1]}")
            # logger.info("="*20)
             # not possible to generate, return list of None, so random directions are generated
            if not generated_sequences:
                logger.error("Unable to generate :(")
                assert len(prev_heads) == len(game_sequences)
                return ["<gen_err>" for _ in range(len(prev_heads))]
            
            # get all new positions
            # generated_positions = [gen_sequence[len(game_sequences[0]):] for gen_sequence in generated_sequences]
            return [gen_sequence.split()[-1] for gen_sequence in generated_sequences]

        except Exception as e:
            
            # error occured return list of None, so random directions are generated
            logger.error(f"Generate sequences error {e}")
            return ["<gen_err>" for _ in range(len(prev_heads))]



    def get_direction_based_on_heads(self, prev_head: tuple[int, int], current_head: tuple[int, int]) -> str:
        """
            Return WSAD move.
        """
        # up
        if (prev_head[0] - 1, prev_head[1]) == current_head:
            return "U"
        # down
        elif (prev_head[0] + 1, prev_head[1]) == current_head:
            return "D"
        # left
        elif (prev_head[0], prev_head[1] - 1) == current_head:
            return "L"
        # right
        elif (prev_head[0], prev_head[1] + 1) == current_head:
            return "R"
        
    
    def parse_tokens(self, prev_heads: List[Tuple[int, int]], tokens: List[str]):
        """
        Parse position token, return direction, if it's not position token or position token is incorrect
        return unchanged token
        """

        result = []

        coords_extraction_pattern = r"-?\d+"
        valid_position_token_pattern = r'R-?\d+C-?\d+'

        for prev_head, token in zip(prev_heads, tokens):
    
            # detect invalid token
            if not re.search(valid_position_token_pattern, token):
                result.append(token)
                continue
            
            # token was a valid position token, check if the new position is actually valid
            # re.findall returns all numbers from a tuple
            new_head = tuple([int(elem) for elem in re.findall(coords_extraction_pattern, token)])
            
            if self.is_move_valid(prev_head, new_head):
                # move was valid, parse it to direction char
                d = self.get_direction_based_on_heads(prev_head=prev_head, current_head=new_head)
                result.append(d)
            else:
                # generated position token is not a valid position, just give position token
                result.append(token)

        return result
    

    def evaluate_sampling_statistics(self, generated_tokens, prev_heads):
        
        # EVALUATION STATISTICS
        batch_snakes_directions = []
        incorrect_tokens = []
        incorrect_generations = 0

        directions = self.parse_tokens(prev_heads, generated_tokens)
        for d in directions:
            # only invalid tokens don't get parsed as direction letters
            if d not in "UDLR":
                incorrect_generations += 1
                incorrect_tokens.append(d)
                batch_snakes_directions.append(random.choice(["U", "D", "L", "R"]))
            else:
                incorrect_tokens.append(None)
                batch_snakes_directions.append(d)

        return batch_snakes_directions, incorrect_tokens, incorrect_generations

       
    def sample_next_batch_moves(self, prev_heads: List[Tuple[int, int]], game_sequences: List[str], top_k: int = 1) -> str | None:
        """
            Function takes top 1 position returned by LLM for all provided game sequences,
            outputs
        """

        if not prev_heads:
            logger.error(game_sequences)
        
        generated_tokens = self.run_lm(prev_heads=prev_heads, game_sequences=game_sequences, legal_tokens=None, top_k=top_k)

        return self.evaluate_sampling_statistics(generated_tokens=generated_tokens, prev_heads=prev_heads)



    def sample_next_batch_moves_from_legal_tokens(self, prev_heads: List[Tuple[int, int]], game_sequences: List[str], states, language_model_snake_idx: int = 1) -> str | None:
        """
            Function returns most probable valid move token for each game in the batch.
            Which snake to analize will be provided in the argument.
        """
        
        assert(prev_heads)
        assert len(prev_heads) == len(game_sequences) == len(states)

        # get legal tokens for each state
        legal_tokens: List[List[str, str, str]] = []
        #  For a given head position, returns token that would result in
        #  moving in this very direction.
        dir_token_mapping = lambda dir, R, C: {
            "U": f"R{R-1}C{C}",
            "D": f"R{R+1}C{C}",
            "L": f"R{R}C{C-1}",
            "R": f"R{R}C{C+1}"
        }.get(dir)


        for state in states:
            snake = state.snakes[language_model_snake_idx]

            R, C = snake.head

            state_legal_tokens = []
            # opposite is an ad hoc solution, since compying cpp object is not that simple xd
            for direction in "UDLR":
        
                # if the direction is the right one
                if state.try_move(direction, snake):
                    state_legal_tokens.append(dir_token_mapping(direction, R, C))

            # concat legal tokens to all legal tokens
            # legal moves are a list of lists of legal move for each game
            legal_tokens.append(state_legal_tokens)
            
        # [logger.info(tk) for tk in legal_tokens if len(tk) == 1] 

        # top k is None in the case of legal tokens
        generated_tokens = self.run_lm(prev_heads=prev_heads, game_sequences=game_sequences, legal_tokens=legal_tokens, top_k=None)

        # sanity check, if legal_tokens == [], then model should generate <START> by default
        # if legal tokens were provided, then generated element should come from legal tokens
        for legal_tks, generated_tk in zip(legal_tokens, generated_tokens):
            if legal_tks == []:
                assert generated_tk == "<START>"
            
            else:
                assert generated_tk in legal_tks
            

        # logger.info(generated_tokens)

        return self.evaluate_sampling_statistics(generated_tokens=generated_tokens, prev_heads=prev_heads)




if __name__ == "__main__":
    # lm_caller = LLMCaller(model_name="out_standard_positions_bs_64", device="cuda")

#     sequences =["<START> S0 R1C0 L0 A05 A00 A36 A96 A58 S1 R6C7 L0 A05 A00 A36 A96 A58 S0 R0C0 L1 A05 A36 A96 A58 A15 S1 R5C7 L0 A05 A36 A96 A58 A15 S0 R0C1 L1 A05 A36 A96 A58 A15 S1 R5C8 L1 A05 A36 A96 A15 A87 S0 R0C2 L1 A05 A36 A96 A15 A87 S1 R4C8 L1 A05 A36 A96 A15 A87 S0 R0C3 L1 A05 A36 A96 A15 A87 S1 R3C8 L1 A05 A36 A96 A15 A87 S0 R0C4 L1 A05 A36 A96 A15 A87 S1 R3C7 L1 A05 A36 A96 A15 A87 S0 R0C5 L2 A36 A96 A15 A87 A47 S1 R3C6 L2 A96 A15 A87 A47 A51 S0 R1C5 L3 A96 A87 A47 A51 A83 S1 R4C6 L2 A96 A87 A47 A51 A83 S0 R2C5 L3 A96 A87 A47 A51 A83 S1 R4C7 L3 A96 A87 A51 A83 A57 S0 R3C5 L3 A96 A87 A51 A83 A57 S1 R5C7 L4 A96 A87 A51 A83 A32 S0 R3C4 L3 A96 A87 A51 A83 A32 S1 R6C7 L4 A96 A87 A51 A83 A32 S0 R3C3 L3 A96 A87 A51 A83 A32 S1 R7C7 L4 A96 A87 A51 A83 A32 S0 R3C2 L4 A96 A87 A51 A83 A66 S1 R8C7 L5 A96 A51 A83 A66 A68 S0 R4C2 L4 A96 A51 A83 A66 A68 S1 R9C7 L5 A96 A51 A83 A66 A68 S0 R5C2 L4 A96 A51 A83 A66 A68 S1 R9C6 L6 A51 A83 A66 A68 A03 S0 R5C1 L5 A83 A66 A68 A03 A53 S1 R8C6 L6 A83 A66 A68 A03 A53 S0 R6C1 L5 A83 A66 A68 A03 A53 S1 R7C6 L6 A83 A66 A68 A03 A53 S0 R6C2 L5 A83 A66 A68 A03 A53 S1 R6C6 L7 A83 A68 A03 A53 A05 S0 R6C3 L5 A83 A68 A03 A53 A05 S1 R6C7 L7 A83 A68 A03 A53 A05 S0 R5C3 L6 A83 A68 A03 A05 A25 S1 R6C8 L8 A83 A03 A05 A25 A30 S0 R4C3 L6 A83 A03 A05 A25 A30 S1 R5C8 L8 A83 A03 A05 A25 A30 S0 R3C3 L6 A83 A03 A05 A25 A30 S1 R4C8 L8 A83 A03 A05 A25 A30 S0 R2C3 L6 A83 A03 A05 A25 A30 S1 R3C8 L8 A83 A03 A05 A25 A30 S0 R2C4 L6 A83 A03 A05 A25 A30 S1 R2C8 L8 A83 A03 A05 A25 A30 S0 R2C5 L7 A83 A03 A05 A30 A50 S1 R1C8 L8 A83 A03 A05 A30 A50 S0 R1C5 L7 A83 A03 A05 A30 A50 S1 R0C8 L8 A83 A03 A05 A30 A50 S0 R0C5 L8 A83 A03 A30 A50 A60 S1 R0C7 L8 A83 A03 A30 A50 A60 S0 R0C4 L8 A83 A03 A30 A50 A60 S1 R1C7 L8 A83 A03 A30 A50 A60 S0 R0C3 L9 A83 A30 A50 A60 A02 S1 R2C7 L8 A83 A30 A50 A60 A02 S0 R0C2 L10 A83 A30 A50 A60 A52 S1 R3C7 L8 A83 A30 A50 A60 A52 S0 R1C2 L10 A83 A30 A50 A60 A52 S1 R4C7 L8 A83 A30 A50 A60 A52 S0 R2C2 L10 A83 A30 A50 A60 A52 S1 R5C7 L8 A83 A30 A50 A60 A52 S0 R3C2 L10 A83 A30 A50 A60 A52 S1 R5C6 L8 A83 A30 A50 A60 A52 S0 R4C2 L10 A83 A30 A50 A60 A52 S1 R5C5 L8 A83 A30 A50 A60 A52 S0 R5C2 L11 A83 A30 A50 A60 A62 S1 R6C5 L8 A83 A30 A50 A60 A62 S0 R6C2 L12 A83 A30 A50 A60 A36 S1 R7C5 L8 A83 A30 A50 A60 A36 S0 R6C1 L12 A83 A30 A50 A60 A36 S1 R8C5 L8 A83 A30 A50 A60 A36 S0 R6C0 L13 A83 A30 A50 A36 A98 S1 R8C4 L8 A83 A30 A50 A36 A98 S0 R5C0 L14 A83 A30 A36 A98 A69 S1 R8C3 L9 A30 A36 A98 A69 A92 S0 R4C0 L14 A30 A36 A98 A69 A92 S1 R9C3 L9 A30 A36 A98 A69 A92 S0 R3C0 L15 A36 A98 A69 A92 A21 S1 R9C2 L10 A36 A98 A69 A21 A23 S0 R2C0 L15 A36 A98 A69 A21 A23 S1 R8C2 L10 A36 A98 A69 A21 A23 S0 R2C1 L16 A36 A98 A69 A23 A49 S1 R7C2 L10 A36 A98 A69 A23 A49 S0 R3C1 L16 A36 A98 A69 A23 A49 S1 R7C3 L10 A36 A98 A69 A23 A49 S0 R4C1 L16 A36 A98 A69 A23 A49 S1 R6C3 L10 A36 A98 A69 A23 A49 S0 R5C1 L16 A36 A98 A69 A23 A49 S1 R5C3 L10 A36 A98 A69 A23 A49 S0 R5C2 L16 A36 A98 A69 A23 A49 S1 R4C3 L10 A36 A98 A69 A23 A49 S0 <DEAD> L16 A36 A98 A69 A23 A49 S1",
# "<START> S0 R2C6 L0 A80 A98 A29 A92 A43 S1 R7C6 L0 A80 A98 A29 A92 A43 S0 R2C7 L0 A80 A98 A29 A92 A43 S1 R8C6 L0 A80 A98 A29 A92 A43 S0 R2C8 L0 A80 A98 A29 A92 A43 S1 R9C6 L0 A80 A98 A29 A92 A43 S0 R2C9 L1 A80 A98 A92 A43 A49 S1 R9C7 L0 A80 A98 A92 A43 A49 S0 R3C9 L1 A80 A98 A92 A43 A49 S1 R9C8 L1 A80 A92 A43 A49 A08 S0 R4C9 L2 A80 A92 A43 A08 A73 S1 R8C8 L1 A80 A92 A43 A08 A73 S0 R4C8 L2 A80 A92 A43 A08 A73 S1 R7C8 L1 A80 A92 A43 A08 A73 S0 R3C8 L2 A80 A92 A43 A08 A73 S1 R7C7 L1 A80 A92 A43 A08 A73 S0 R2C8 L2 A80 A92 A43 A08 A73 S1 R7C6 L1 A80 A92 A43 A08 A73 S0 R1C8 L2 A80 A92 A43 A08 A73 S1 R7C5 L1 A80 A92 A43 A08 A73 S0 R0C8 L3 A80 A92 A43 A73 A29 S1 R7C4 L1 A80 A92 A43 A73 A29 S0 R0C9 L3 A80 A92 A43 A73 A29 S1 R7C3 L2 A80 A92 A43 A29 A67 S0 R1C9 L3 A80 A92 A43 A29 A67 S1 R8C3 L2 A80 A92 A43 A29 A67 S0 R2C9 L4 A80 A92 A43 A67 A31 S1 R9C3 L2 A80 A92 A43 A67 A31 S0 R3C9 L4 A80 A92 A43 A67 A31 S1 R9C2 L3 A80 A43 A67 A31 A22 S0 R4C9 L4 A80 A43 A67 A31 A22 S1 R8C2 L3 A80 A43 A67 A31 A22 S0 R5C9 L4 A80 A43 A67 A31 A22 S1 R8C1 L3 A80 A43 A67 A31 A22 S0 R6C9 L4 A80 A43 A67 A31 A22 S1 R8C0 L4 A43 A67 A31 A22 A65 S0 R6C8 L4 A43 A67 A31 A22 A65 S1 R7C0 L4 A43 A67 A31 A22 A65 S0 R6C7 L5 A43 A31 A22 A65 A99 S1 R6C0 L4 A43 A31 A22 A65 A99 S0 R6C6 L5 A43 A31 A22 A65 A99 S1 R5C0 L4 A43 A31 A22 A65 A99 S0 R6C5 L6 A43 A31 A22 A99 A14 S1 R4C0 L4 A43 A31 A22 A99 A14 S0 R5C5 L6 A43 A31 A22 A99 A14 S1 R3C0 L4 A43 A31 A22 A99 A14 S0 R4C5 L6 A43 A31 A22 A99 A14 S1 R3C1 L5 A43 A22 A99 A14 A21 S0 R4C4 L6 A43 A22 A99 A14 A21 S1 R2C1 L6 A43 A22 A99 A14 A75 S0 R4C3 L7 A22 A99 A14 A75 A26 S1 R2C2 L7 A99 A14 A75 A26 A23 S0 R3C3 L7 A99 A14 A75 A26 A23 S1 R2C3 L8 A99 A14 A75 A26 A93 S0 R3C4 L7 A99 A14 A75 A26 A93 S1 R1C3 L8 A99 A14 A75 A26 A93 S0 R2C4 L7 A99 A14 A75 A26 A93 S1 R1C4 L9 A99 A75 A26 A93 A83 S0 R2C5 L7 A99 A75 A26 A93 A83 S1 R1C5 L9 A99 A75 A26 A93 A83 S0 R2C6 L8 A99 A75 A93 A83 A80 S1 R1C6 L9 A99 A75 A93 A83 A80 S0 R3C6 L8 A99 A75 A93 A83 A80 S1 R1C7 L9 A99 A75 A93 A83 A80 S0 R4C6 L8 A99 A75 A93 A83 A80 S1 R2C7 L9 A99 A75 A93 A83 A80 S0 R5C6 L8 A99 A75 A93 A83 A80 S1 R3C7 L9 A99 A75 A93 A83 A80 S0 R6C6 L8 A99 A75 A93 A83 A80 S1 R4C7 L9 A99 A75 A93 A83 A80 S0 R7C6 L8 A99 A75 A93 A83 A80 S1 R5C7 L9 A99 A75 A93 A83 A80 S0 R7C5 L9 A99 A93 A83 A80 A35 S1 R6C7 L9 A99 A93 A83 A80 A35 S0 R8C5 L9 A99 A93 A83 A80 A35 S1 R7C7 L9 A99 A93 A83 A80 A35 S0 R8C4 L9 A99 A93 A83 A80 A35 S1 R8C7 L9 A99 A93 A83 A80 A35 S0 R8C3 L10 A99 A93 A80 A35 A08 S1 R9C7 L9 A99 A93 A80 A35 A08 S0 R9C3 L11 A99 A80 A35 A08 A06 S1 R9C8 L9 A99 A80 A35 A08 A06 S0 R9C2 L11 A99 A80 A35 A08 A06 S1 R9C9 L10 A80 A35 A08 A06 A07 S0 R8C2 L11 A80 A35 A08 A06 A07 S1 R8C9 L10 A80 A35 A08 A06 A07 S0 R8C1 L11 A80 A35 A08 A06 A07 S1 R7C9 L10 A80 A35 A08 A06 A07 S0 R8C0 L12 A35 A08 A06 A07 A62 S1 R6C9 L10 A35 A08 A06 A07 A62 S0 R7C0 L12 A35 A08 A06 A07 A62 S1 R5C9 L10 A35 A08 A06 A07 A62 S0 R6C0 L12 A35 A08 A06 A07 A62 S1 R4C9 L10 A35 A08 A06 A07 A62 S0 R6C1 L12 A35 A08 A06 A07 A62 S1",
# "<START> S0 R0C6 L0 A29 A17 A21 A39 A13 S1 R3C5 L0 A29 A17 A21 A39 A13 S0 R1C6 L0 A29 A17 A21 A39 A13 S1 R2C5 L0 A29 A17 A21 A39 A13 S0 R1C7 L1 A29 A21 A39 A13 A78 S1 R2C4 L0 A29 A21 A39 A13 A78 S0 R2C7 L1 A29 A21 A39 A13 A78 S1 R1C4 L0 A29 A21 A39 A13 A78 S0 R2C8 L1 A29 A21 A39 A13 A78 S1 R1C3 L1 A29 A21 A39 A78 A12 S0 R2C9 L2 A21 A39 A78 A12 A31 S1 R1C2 L2 A21 A39 A78 A31 A00 S0 R3C9 L3 A21 A78 A31 A00 A54 S1 R2C2 L2 A21 A78 A31 A00 A54 S0 R4C9 L3 A21 A78 A31 A00 A54 S1 R2C1 L3 A78 A31 A00 A54 A64 S0 R5C9 L3 A78 A31 A00 A54 A64 S1 R3C1 L4 A78 A00 A54 A64 A08 S0 R6C9 L3 A78 A00 A54 A64 A08 S1 R3C0 L4 A78 A00 A54 A64 A08 S0 R7C9 L3 A78 A00 A54 A64 A08 S1 R2C0 L4 A78 A00 A54 A64 A08 S0 R7C8 L4 A00 A54 A64 A08 A68 S1 R1C0 L4 A00 A54 A64 A08 A68 S0 R6C8 L5 A00 A54 A64 A08 A23 S1 R0C0 L5 A54 A64 A08 A23 A36 S0 R6C7 L5 A54 A64 A08 A23 A36 S1 R0C1 L5 A54 A64 A08 A23 A36 S0 R6C6 L5 A54 A64 A08 A23 A36 S1 R1C1 L5 A54 A64 A08 A23 A36 S0 R6C5 L5 A54 A64 A08 A23 A36 S1 R2C1 L5 A54 A64 A08 A23 A36 S0 R6C4 L6 A54 A08 A23 A36 A81 S1 R2C2 L5 A54 A08 A23 A36 A81 S0 R5C4 L7 A08 A23 A36 A81 A70 S1 R2C3 L6 A08 A36 A81 A70 A72 S0 R5C3 L7 A08 A36 A81 A70 A72 S1 R3C3 L6 A08 A36 A81 A70 A72 S0 R6C3 L7 A08 A36 A81 A70 A72 S1 R3C4 L6 A08 A36 A81 A70 A72 S0 R7C3 L7 A08 A36 A81 A70 A72 S1 R3C5 L6 A08 A36 A81 A70 A72 S0 R7C2 L8 A08 A36 A81 A70 A58 S1 R3C6 L7 A08 A81 A70 A58 A87 S0 R7C1 L8 A08 A81 A70 A58 A87 S1 R4C6 L7 A08 A81 A70 A58 A87 S0 R8C1 L9 A08 A70 A58 A87 A93 S1 R5C6 L7 A08 A70 A58 A87 A93 S0 R8C0 L9 A08 A70 A58 A87 A93 S1 R5C7 L7 A08 A70 A58 A87 A93 S0 R7C0 L10 A08 A58 A87 A93 A37 S1 R5C8 L8 A08 A87 A93 A37 A07 S0 R6C0 L10 A08 A87 A93 A37 A07 S1 R4C8 L8 A08 A87 A93 A37 A07 S0 R5C0 L10 A08 A87 A93 A37 A07 S1 R3C8 L8 A08 A87 A93 A37 A07 S0 R4C0 L10 A08 A87 A93 A37 A07 S1 R3C7 L9 A08 A87 A93 A07 A59 S0 R4C1 L10 A08 A87 A93 A07 A59 S1 R2C7 L9 A08 A87 A93 A07 A59 S0 R5C1 L10 A08 A87 A93 A07 A59 S1 R1C7 L9 A08 A87 A93 A07 A59 S0 R6C1 L10 A08 A87 A93 A07 A59 S1 R0C7 L10 A08 A87 A93 A59 A39 S0 R6C2 L10 A08 A87 A93 A59 A39 S1 R0C8 L11 A87 A93 A59 A39 A64 S0 R6C3 L10 A87 A93 A59 A39 A64 S1 R1C8 L11 A87 A93 A59 A39 A64 S0 R6C4 L11 A87 A93 A59 A39 A13 S1 R2C8 L11 A87 A93 A59 A39 A13 S0 R7C4 L11 A87 A93 A59 A39 A13 S1 R2C9 L11 A87 A93 A59 A39 A13 S0 R8C4 L11 A87 A93 A59 A39 A13 S1 R3C9 L12 A87 A93 A59 A13 A90 S0 R9C4 L11 A87 A93 A59 A13 A90 S1 R4C9 L12 A87 A93 A59 A13 A90 S0 R9C3 L12 A87 A59 A13 A90 A06 S1 R5C9 L13 A87 A13 A90 A06 A04 S0 R9C2 L12 A87 A13 A90 A06 A04 S1 R6C9 L13 A87 A13 A90 A06 A04 S0 R9C1 L12 A87 A13 A90 A06 A04 S1 R7C9 L13 A87 A13 A90 A06 A04 S0 R9C0 L13 A87 A13 A06 A04 A31 S1 R8C9 L13 A87 A13 A06 A04 A31 S0 R8C0 L13 A87 A13 A06 A04 A31 S1 R8C8 L13 A87 A13 A06 A04 A31 S0 R7C0 L13 A87 A13 A06 A04 A31 S1 R8C7 L14 A13 A06 A04 A31 A40 S0 R6C0 L13 A13 A06 A04 A31 A40 S1 R7C7 L14 A13 A06 A04 A31 A40 S0 R5C0 L13 A13 A06 A04 A31 A40 S1 R6C7 L14 A13 A06 A04 A31 A40 S0 R4C0 L14 A13 A06 A04 A31 A25 S1 R5C7 L14 A13 A06 A04 A31 A25 S0 R3C0 L14 A13 A06 A04 A31 A25 S1"]
    
#     sequences =["<START> S0 R1C0 L0 A05 A00 A36 A96 A58 S1 R6C7 L0 A05 A00 A36 A96 A58 S0 R0C0 L1 A05 A36 A96 A58 A15 S1 R5C7 L0 A05 A36 A96 A58 A15 S0 R0C1 L1 A05 A36 A96 A58 A15 S1 R5C8 L1 A05 A36 A96 A15 A87 S0 R0C2 L1 A05 A36 A96 A15 A87 S1 R4C8 L1 A05 A36 A96 A15 A87 S0 R0C3 L1 A05 A36 A96 A15 A87 S1 R3C8 L1 A05 A36 A96 A15 A87 S0 R0C4 L1 A05 A36 A96 A15 A87 S1 R3C7 L1 A05 A36 A96 A15 A87 S0 R0C5 L2 A36 A96 A15 A87 A47 S1 R3C6 L2 A96 A15 A87 A47 A51 S0 R1C5 L3 A96 A87 A47 A51 A83 S1 R4C6 L2 A96 A87 A47 A51 A83 S0 R2C5 L3 A96 A87 A47 A51 A83 S1 R4C7 L3 A96 A87 A51 A83 A57 S0 R3C5 L3 A96 A87 A51 A83 A57 S1 R5C7 L4 A96 A87 A51 A83 A32 S0 R3C4 L3 A96 A87 A51 A83 A32 S1 R6C7 L4 A96 A87 A51 A83 A32 S0 R3C3 L3 A96 A87 A51 A83 A32 S1 R7C7 L4 A96 A87 A51 A83 A32 S0 R3C2 L4 A96 A87 A51 A83 A66 S1 R8C7 L5 A96 A51 A83 A66 A68 S0 R4C2 L4 A96 A51 A83 A66 A68 S1 R9C7 L5 A96 A51 A83 A66 A68 S0 R5C2 L4 A96 A51 A83 A66 A68 S1 R9C6 L6 A51 A83 A66 A68 A03 S0 R5C1 L5 A83 A66 A68 A03 A53 S1 R8C6 L6 A83 A66 A68 A03 A53 S0 R6C1 L5 A83 A66 A68 A03 A53 S1 R7C6 L6 A83 A66 A68 A03 A53 S0 R6C2 L5 A83 A66 A68 A03 A53 S1 R6C6 L7 A83 A68 A03 A53 A05 S0 R6C3 L5 A83 A68 A03 A53 A05 S1 R6C7 L7 A83 A68 A03 A53 A05 S0 R5C3 L6 A83 A68 A03 A05 A25 S1 R6C8 L8 A83 A03 A05 A25 A30 S0 R4C3 L6 A83 A03 A05 A25 A30 S1 R5C8 L8 A83 A03 A05 A25 A30 S0 R3C3 L6 A83 A03 A05 A25 A30 S1 R4C8 L8 A83 A03 A05 A25 A30 S0 R2C3 L6 A83 A03 A05 A25 A30 S1 R3C8 L8 A83 A03 A05 A25 A30 S0 R2C4 L6 A83 A03 A05 A25 A30 S1 R2C8 L8 A83 A03 A05 A25 A30 S0 R2C5 L7 A83 A03 A05 A30 A50 S1 R1C8 L8 A83 A03 A05 A30 A50 S0 R1C5 L7 A83 A03 A05 A30 A50 S1 R0C8 L8 A83 A03 A05 A30 A50 S0 R0C5 L8 A83 A03 A30 A50 A60 S1 R0C7 L8 A83 A03 A30 A50 A60 S0 R0C4 L8 A83 A03 A30 A50 A60 S1 R1C7 L8 A83 A03 A30 A50 A60 S0 R0C3 L9 A83 A30 A50 A60 A02 S1 R2C7 L8 A83 A30 A50 A60 A02 S0 R0C2 L10 A83 A30 A50 A60 A52 S1 R3C7 L8 A83 A30 A50 A60 A52 S0 R1C2 L10 A83 A30 A50 A60 A52 S1 R4C7 L8 A83 A30 A50 A60 A52 S0 R2C2 L10 A83 A30 A50 A60 A52 S1 R5C7 L8 A83 A30 A50 A60 A52 S0 R3C2 L10 A83 A30 A50 A60 A52 S1 R5C6 L8 A83 A30 A50 A60 A52 S0 R4C2 L10 A83 A30 A50 A60 A52 S1 R5C5 L8 A83 A30 A50 A60 A52 S0 R5C2 L11 A83 A30 A50 A60 A62 S1 R6C5 L8 A83 A30 A50 A60 A62 S0 R6C2 L12 A83 A30 A50 A60 A36 S1 R7C5 L8 A83 A30 A50 A60 A36 S0 R6C1 L12 A83 A30 A50 A60 A36 S1 R8C5 L8 A83 A30 A50 A60 A36 S0 R6C0 L13 A83 A30 A50 A36 A98 S1 R8C4 L8 A83 A30 A50 A36 A98 S0 R5C0 L14 A83 A30 A36 A98 A69 S1 R8C3 L9 A30 A36 A98 A69 A92 S0 R4C0 L14 A30 A36 A98 A69 A92 S1 R9C3 L9 A30 A36 A98 A69 A92 S0 R3C0 L15 A36 A98 A69 A92 A21 S1 R9C2 L10 A36 A98 A69 A21 A23 S0 R2C0 L15 A36 A98 A69 A21 A23 S1 R8C2 L10 A36 A98 A69 A21 A23 S0 R2C1 L16 A36 A98 A69 A23 A49 S1 R7C2 L10 A36 A98 A69 A23 A49 S0 R3C1 L16 A36 A98 A69 A23 A49 S1 R7C3 L10 A36 A98 A69 A23 A49 S0 R4C1 L16 A36 A98 A69 A23 A49 S1 R6C3 L10 A36 A98 A69 A23 A49 S0 R5C1 L16 A36 A98 A69 A23 A49 S1 R5C3 L10 A36 A98 A69 A23 A49 S0 R5C2 L16 A36 A98 A69 A23 A49 S1 R4C3 L10 A36 A98 A69 A23 A49 S0",
# "<START> S0 R2C6 L0 A80 A98 A29 A92 A43 S1 R7C6 L0 A80 A98 A29 A92 A43 S0 R2C7 L0 A80 A98 A29 A92 A43 S1 R8C6 L0 A80 A98 A29 A92 A43 S0 R2C8 L0 A80 A98 A29 A92 A43 S1 R9C6 L0 A80 A98 A29 A92 A43 S0 R2C9 L1 A80 A98 A92 A43 A49 S1 R9C7 L0 A80 A98 A92 A43 A49 S0 R3C9 L1 A80 A98 A92 A43 A49 S1 R9C8 L1 A80 A92 A43 A49 A08 S0 R4C9 L2 A80 A92 A43 A08 A73 S1 R8C8 L1 A80 A92 A43 A08 A73 S0 R4C8 L2 A80 A92 A43 A08 A73 S1 R7C8 L1 A80 A92 A43 A08 A73 S0 R3C8 L2 A80 A92 A43 A08 A73 S1 R7C7 L1 A80 A92 A43 A08 A73 S0 R2C8 L2 A80 A92 A43 A08 A73 S1 R7C6 L1 A80 A92 A43 A08 A73 S0 R1C8 L2 A80 A92 A43 A08 A73 S1 R7C5 L1 A80 A92 A43 A08 A73 S0 R0C8 L3 A80 A92 A43 A73 A29 S1 R7C4 L1 A80 A92 A43 A73 A29 S0 R0C9 L3 A80 A92 A43 A73 A29 S1 R7C3 L2 A80 A92 A43 A29 A67 S0 R1C9 L3 A80 A92 A43 A29 A67 S1 R8C3 L2 A80 A92 A43 A29 A67 S0 R2C9 L4 A80 A92 A43 A67 A31 S1 R9C3 L2 A80 A92 A43 A67 A31 S0 R3C9 L4 A80 A92 A43 A67 A31 S1 R9C2 L3 A80 A43 A67 A31 A22 S0 R4C9 L4 A80 A43 A67 A31 A22 S1 R8C2 L3 A80 A43 A67 A31 A22 S0 R5C9 L4 A80 A43 A67 A31 A22 S1 R8C1 L3 A80 A43 A67 A31 A22 S0 R6C9 L4 A80 A43 A67 A31 A22 S1 R8C0 L4 A43 A67 A31 A22 A65 S0 R6C8 L4 A43 A67 A31 A22 A65 S1 R7C0 L4 A43 A67 A31 A22 A65 S0 R6C7 L5 A43 A31 A22 A65 A99 S1 R6C0 L4 A43 A31 A22 A65 A99 S0 R6C6 L5 A43 A31 A22 A65 A99 S1 R5C0 L4 A43 A31 A22 A65 A99 S0 R6C5 L6 A43 A31 A22 A99 A14 S1 R4C0 L4 A43 A31 A22 A99 A14 S0 R5C5 L6 A43 A31 A22 A99 A14 S1 R3C0 L4 A43 A31 A22 A99 A14 S0 R4C5 L6 A43 A31 A22 A99 A14 S1 R3C1 L5 A43 A22 A99 A14 A21 S0 R4C4 L6 A43 A22 A99 A14 A21 S1 R2C1 L6 A43 A22 A99 A14 A75 S0 R4C3 L7 A22 A99 A14 A75 A26 S1 R2C2 L7 A99 A14 A75 A26 A23 S0 R3C3 L7 A99 A14 A75 A26 A23 S1 R2C3 L8 A99 A14 A75 A26 A93 S0 R3C4 L7 A99 A14 A75 A26 A93 S1 R1C3 L8 A99 A14 A75 A26 A93 S0 R2C4 L7 A99 A14 A75 A26 A93 S1 R1C4 L9 A99 A75 A26 A93 A83 S0 R2C5 L7 A99 A75 A26 A93 A83 S1 R1C5 L9 A99 A75 A26 A93 A83 S0 R2C6 L8 A99 A75 A93 A83 A80 S1 R1C6 L9 A99 A75 A93 A83 A80 S0 R3C6 L8 A99 A75 A93 A83 A80 S1 R1C7 L9 A99 A75 A93 A83 A80 S0 R4C6 L8 A99 A75 A93 A83 A80 S1 R2C7 L9 A99 A75 A93 A83 A80 S0 R5C6 L8 A99 A75 A93 A83 A80 S1 R3C7 L9 A99 A75 A93 A83 A80 S0 R6C6 L8 A99 A75 A93 A83 A80 S1 R4C7 L9 A99 A75 A93 A83 A80 S0 R7C6 L8 A99 A75 A93 A83 A80 S1 R5C7 L9 A99 A75 A93 A83 A80 S0 R7C5 L9 A99 A93 A83 A80 A35 S1 R6C7 L9 A99 A93 A83 A80 A35 S0 R8C5 L9 A99 A93 A83 A80 A35 S1 R7C7 L9 A99 A93 A83 A80 A35 S0 R8C4 L9 A99 A93 A83 A80 A35 S1 R8C7 L9 A99 A93 A83 A80 A35 S0 R8C3 L10 A99 A93 A80 A35 A08 S1 R9C7 L9 A99 A93 A80 A35 A08 S0 R9C3 L11 A99 A80 A35 A08 A06 S1 R9C8 L9 A99 A80 A35 A08 A06 S0 R9C2 L11 A99 A80 A35 A08 A06 S1 R9C9 L10 A80 A35 A08 A06 A07 S0 R8C2 L11 A80 A35 A08 A06 A07 S1 R8C9 L10 A80 A35 A08 A06 A07 S0 R8C1 L11 A80 A35 A08 A06 A07 S1 R7C9 L10 A80 A35 A08 A06 A07 S0 R8C0 L12 A35 A08 A06 A07 A62 S1 R6C9 L10 A35 A08 A06 A07 A62 S0 R7C0 L12 A35 A08 A06 A07 A62 S1 R5C9 L10 A35 A08 A06 A07 A62 S0 R6C0 L12 A35 A08 A06 A07 A62 S1 R4C9 L10 A35 A08 A06 A07 A62 S0",
# "<START> S0 R0C6 L0 A29 A17 A21 A39 A13 S1 R3C5 L0 A29 A17 A21 A39 A13 S0 R1C6 L0 A29 A17 A21 A39 A13 S1 R2C5 L0 A29 A17 A21 A39 A13 S0 R1C7 L1 A29 A21 A39 A13 A78 S1 R2C4 L0 A29 A21 A39 A13 A78 S0 R2C7 L1 A29 A21 A39 A13 A78 S1 R1C4 L0 A29 A21 A39 A13 A78 S0 R2C8 L1 A29 A21 A39 A13 A78 S1 R1C3 L1 A29 A21 A39 A78 A12 S0 R2C9 L2 A21 A39 A78 A12 A31 S1 R1C2 L2 A21 A39 A78 A31 A00 S0 R3C9 L3 A21 A78 A31 A00 A54 S1 R2C2 L2 A21 A78 A31 A00 A54 S0 R4C9 L3 A21 A78 A31 A00 A54 S1 R2C1 L3 A78 A31 A00 A54 A64 S0 R5C9 L3 A78 A31 A00 A54 A64 S1 R3C1 L4 A78 A00 A54 A64 A08 S0 R6C9 L3 A78 A00 A54 A64 A08 S1 R3C0 L4 A78 A00 A54 A64 A08 S0 R7C9 L3 A78 A00 A54 A64 A08 S1 R2C0 L4 A78 A00 A54 A64 A08 S0 R7C8 L4 A00 A54 A64 A08 A68 S1 R1C0 L4 A00 A54 A64 A08 A68 S0 R6C8 L5 A00 A54 A64 A08 A23 S1 R0C0 L5 A54 A64 A08 A23 A36 S0 R6C7 L5 A54 A64 A08 A23 A36 S1 R0C1 L5 A54 A64 A08 A23 A36 S0 R6C6 L5 A54 A64 A08 A23 A36 S1 R1C1 L5 A54 A64 A08 A23 A36 S0 R6C5 L5 A54 A64 A08 A23 A36 S1 R2C1 L5 A54 A64 A08 A23 A36 S0 R6C4 L6 A54 A08 A23 A36 A81 S1 R2C2 L5 A54 A08 A23 A36 A81 S0 R5C4 L7 A08 A23 A36 A81 A70 S1 R2C3 L6 A08 A36 A81 A70 A72 S0 R5C3 L7 A08 A36 A81 A70 A72 S1 R3C3 L6 A08 A36 A81 A70 A72 S0 R6C3 L7 A08 A36 A81 A70 A72 S1 R3C4 L6 A08 A36 A81 A70 A72 S0 R7C3 L7 A08 A36 A81 A70 A72 S1 R3C5 L6 A08 A36 A81 A70 A72 S0 R7C2 L8 A08 A36 A81 A70 A58 S1 R3C6 L7 A08 A81 A70 A58 A87 S0 R7C1 L8 A08 A81 A70 A58 A87 S1 R4C6 L7 A08 A81 A70 A58 A87 S0 R8C1 L9 A08 A70 A58 A87 A93 S1 R5C6 L7 A08 A70 A58 A87 A93 S0 R8C0 L9 A08 A70 A58 A87 A93 S1 R5C7 L7 A08 A70 A58 A87 A93 S0 R7C0 L10 A08 A58 A87 A93 A37 S1 R5C8 L8 A08 A87 A93 A37 A07 S0 R6C0 L10 A08 A87 A93 A37 A07 S1 R4C8 L8 A08 A87 A93 A37 A07 S0 R5C0 L10 A08 A87 A93 A37 A07 S1 R3C8 L8 A08 A87 A93 A37 A07 S0 R4C0 L10 A08 A87 A93 A37 A07 S1 R3C7 L9 A08 A87 A93 A07 A59 S0 R4C1 L10 A08 A87 A93 A07 A59 S1 R2C7 L9 A08 A87 A93 A07 A59 S0 R5C1 L10 A08 A87 A93 A07 A59 S1 R1C7 L9 A08 A87 A93 A07 A59 S0 R6C1 L10 A08 A87 A93 A07 A59 S1 R0C7 L10 A08 A87 A93 A59 A39 S0 R6C2 L10 A08 A87 A93 A59 A39 S1 R0C8 L11 A87 A93 A59 A39 A64 S0 R6C3 L10 A87 A93 A59 A39 A64 S1 R1C8 L11 A87 A93 A59 A39 A64 S0 R6C4 L11 A87 A93 A59 A39 A13 S1 R2C8 L11 A87 A93 A59 A39 A13 S0 R7C4 L11 A87 A93 A59 A39 A13 S1 R2C9 L11 A87 A93 A59 A39 A13 S0 R8C4 L11 A87 A93 A59 A39 A13 S1 R3C9 L12 A87 A93 A59 A13 A90 S0 R9C4 L11 A87 A93 A59 A13 A90 S1 R4C9 L12 A87 A93 A59 A13 A90 S0 R9C3 L12 A87 A59 A13 A90 A06 S1 R5C9 L13 A87 A13 A90 A06 A04 S0 R9C2 L12 A87 A13 A90 A06 A04 S1 R6C9 L13 A87 A13 A90 A06 A04 S0 R9C1 L12 A87 A13 A90 A06 A04 S1 R7C9 L13 A87 A13 A90 A06 A04 S0 R9C0 L13 A87 A13 A06 A04 A31 S1 R8C9 L13 A87 A13 A06 A04 A31 S0 R8C0 L13 A87 A13 A06 A04 A31 S1 R8C8 L13 A87 A13 A06 A04 A31 S0 R7C0 L13 A87 A13 A06 A04 A31 S1 R8C7 L14 A13 A06 A04 A31 A40 S0 R6C0 L13 A13 A06 A04 A31 A40 S1 R7C7 L14 A13 A06 A04 A31 A40 S0 R5C0 L13 A13 A06 A04 A31 A40 S1 R6C7 L14 A13 A06 A04 A31 A40 S0 R4C0 L14 A13 A06 A04 A31 A25 S1 R5C7 L14 A13 A06 A04 A31 A25 S0"]
   
    # r,it,i = lm_caller.sample_next_batch_moves(prev_heads=[(4,3), (4,9), (5,7)], game_sequences=sequences)

    # logger.info(f"{r} {it} {i}")
    # visible positions: ["R3C3", "R4C2", "R5C3", "R4C4"], ["R4C8", "R3C9", "R5C9"], ["R5C6", "R6C7", "R4C7", "R5C8"]
    #[[], ["R4C8", "R3C9", "R5C9"], ["R5C6", "R6C7", "R4C7", "R5C8"]]
    # out = lm_caller.run_lm(prev_heads=[(4,3), (4,9), (5,7)], game_sequences=sequences, legal_tokens=None, top_k=1)
    # logger.info(out)
    # r,it,i = lm_caller.run_lm_legal_tokens(prev_heads=[(4,3), (4,9), (5,7)], game_sequences=sequences)

    # logger.info(f"{r} {it} {i}")


    # INCORRECT SAMPLING VS NO SAMPLING

    lm_caller_sample = LLMCaller(model_name="standard_positions/out_standard_positions_bs_8", device="mps")
    llm_caller_no_sample = LLMCaller(model_name="standard_positions/out_standard_positions_bs_8", device="mps")

    sequences = ["<START> S0 R3C2 L0 A50 A67 A54 A82 A88 S1 R7C2 L0 A50 A67 A54 A82 A88"]
    sequences[0] += " S0 "

    # run sample
    sampled = lm_caller_sample.run_lm(prev_heads=[(3,2)], game_sequences=sequences, legal_tokens=[ ["R4C2", "R2C2", "R3C1", "R3C3"]], top_k=None)

    # run no-sample
    not_sampled = lm_caller_sample.run_lm(prev_heads=[(3,2)], game_sequences=sequences, legal_tokens=None, top_k=1)

    # logger.debug(f"sampled {sampled}")
    # logger.debug(f"not sampled {not_sampled}")