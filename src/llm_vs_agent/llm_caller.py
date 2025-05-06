import subprocess
import os
import random
import re


# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

"""
    Class calls specific llm and returns direction
"""
class LLMCaller:


    def is_move_valid(self, prev_head, current_head: tuple[int, int]):
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



    def run_lm(self, prev_head: tuple[int, int], model: str, game_sequence: str, max_new_tokens: int, top_k: int):

        nanoGPT_dir = "/Users/szymon/Documents/Bachelor-Thesis/src/training/nanoGPT"

        
        os.chdir(nanoGPT_dir)
        result = subprocess.run(['python3', "sample.py", f'--out_dir={model}',
                            '--device=mps', f'--start={game_sequence}',
                            f'--max_new_tokens={max_new_tokens}', f'--top_k={top_k}'], capture_output=True, text=True)


        # print(result.stdout)
        generated_sequence = result.stdout.split("---------------")[1]

        if not generated_sequence:
            raise Exception("Unable to generate :(") 
        

        # logger.info(seq)
        # print(seq[len(game_sequence)+1:])
        generated_position = generated_sequence[len(game_sequence)+1:]

        # logger.info(generated_position)

        pattern = r"\d+"
        current_head = tuple([int(elem) for elem in re.findall(pattern, generated_position)])
        
        # return valid move
        if self.is_move_valid(prev_head, current_head):
            return current_head
        

        if not current_head:
            logger.error(game_sequence)
            logger.error(generated_position)
            
        return None


    def get_direction_based_on_heads(self, prev_head: tuple[int, int], current_head: tuple[int, int]) -> str:
        """
            Return WSAD move.
        """
        # up
        if (prev_head[0] - 1, prev_head[1]) == current_head:
            return "W"
        # down
        elif (prev_head[0] + 1, prev_head[1]) == current_head:
            return "S"
        # left
        elif (prev_head[0], prev_head[1] - 1) == current_head:
            return "A"
        # right
        elif (prev_head[0], prev_head[1] + 1) == current_head:
            return "D"
        
  

    def sample_next_move(self, prev_head: tuple[int, int], model: str, game_sequence: str, top_k: int = 1) -> str | None:
        """
            Function takes top 1 position returned by LLM if this position is valid,
            returns None in the case of invalid move is generated
        """

        try:
            new_head_pos = self.run_lm(prev_head=prev_head, model=model, game_sequence=f"{game_sequence}", max_new_tokens=1, top_k=top_k)
            if new_head_pos:
                return self.get_direction_based_on_heads(prev_head=prev_head, current_head=new_head_pos)
            else: 
                raise Exception("Generated improper move")
        except Exception as e:
            logger.error(e)
            return None


if __name__ == "__main__":
    lm_caller = LLMCaller()

    lm_caller.sample_next_move(prev_head=(4, 2), model="out-standard_pos", game_sequence="<START> S0 R3C6 L0 A54 A23 A35 A87 A12 S1 R4C2 L0 A54 A23 A35 A87 A12 S0 R3C5 L0 A54 A23 A87 A12 A01 S1")
