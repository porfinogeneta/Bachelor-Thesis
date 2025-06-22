import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.chat_models import MiniMaxChat
import time
import random
import os

# logger
from src.logger.logger import setup_logger

logger = setup_logger(__name__)


# MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY')
MINIMAX_API_KEY = ""

llm = MiniMaxChat(
    api_key=MINIMAX_API_KEY,
    model='MiniMax-Text-01',
    # temperature=...,
    # other params...
)



class GPTCaller:
    def __init__(self, snake_idx: int):
        self.snake_idx = snake_idx

    
    def create_board_str(self, state):
        """
        Creates a board representation based on the current state of the game.
        """
        board = [["_" for _ in range(state.board_width)] for _ in range(state.board_height)]

        if state.is_snake_out_of_bounds(state.snakes[self.snake_idx]):
            return None
        
        # Place snakes
        # G snake is the snake controlled by the GPT model
        for i, snake in enumerate(state.snakes):
            if i == self.snake_idx:
                # out of bounds head should be drawn
                if not state.is_snake_out_of_bounds(snake):
                    board[snake.head[0]][snake.head[1]] = "G"
                for segment in snake.tail:
                    board[segment[0]][segment[1]] = "g"
            else:
                if not state.is_snake_out_of_bounds(snake):
                    board[snake.head[0]][snake.head[1]] = "L"
                for segment in snake.tail:
                    board[segment[0]][segment[1]] = "l"

        for apple in state.apples:
            board[apple.position[0]][apple.position[1]] = "A"

        # add rows and columns numbers
        for i in range(state.board_height):
            board[i].insert(0, str(i))
        board.insert(0, [" "] + [str(i) for i in range(state.board_width)])

        return "\n".join(" ".join(row) for row in board)
    
    # def reverse_tuple(self, tuple_):
    #     """
    #     Reverses a tuple (x, y) to (y, x).
    #     """
    #     x, y = tuple_
    #     return y, x

    def create_board_state_dict(self, state):

        # create dictionary state representation
        state_dict = {
            "snakes": [
                {
                    "snake": f"Snake{i}",
                    "head": snake.head,
                    "tail": snake.tail,
                    "length": len(snake.tail) + 1,
                    "is_alive": i in state.eliminated_snakes,
                    "direction": snake.get_last_direction(),
                } for i,snake in enumerate(state.snakes)
            ],
            "apples": [apple.position for apple in state.apples],
            "turn": state.turn,
        }

        return state_dict
    
    def get_gpt_action(self, prompt: dict, sample: bool, state):
        """
        Generates a move for the GPT model based on the current state of the game.
        """

        assert self.snake_idx not in state.eliminated_snakes, "Elliminated snake should be able to call GPT"

        board = self.create_board_state_dict(state)



        template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(prompt["sys_msg"]),
                HumanMessagePromptTemplate.from_template(prompt["human_msg"]),
            ]
        )

    
        board_str = self.create_board_str(state)

        # dirs to emojis
        emoji_dir = {
            "U": "⬆️",
            "D": "⬇️",
            "L": "⬅️",
            "R": "➡️"
        }
       

        messages = template.format_messages(
            snake_idx=self.snake_idx,
            opponent_idx=1 - self.snake_idx,
            chars_board={board_str},
            board_state_dict={json.dumps(board)}
            # apples=board["apples"],
            # head=board["snakes"][self.snake_idx]["head"],
            # tail=board["snakes"][self.snake_idx]["tail"],
            # enemy_head=board["snakes"][1 - self.snake_idx]["head"],
            # enemy_tail=board["snakes"][1 - self.snake_idx]["tail"],
            # game_board=board_str,
            # previous_move=emoji_dir.get(board["snakes"][self.snake_idx]["direction"], "⬆️")
        )


        logger.debug(messages)

        # logger.debug(f"GPT prompt: {messages}")
        # # OpenAI API call with the callback to get the response message but also the cost and tokens used in the callback
        # t0 = time()
        # with get_openai_callback() as cb:
        #     agent_response = llm(messages).content
        # llm_time = time() - t0

        model_response = llm.invoke(messages)
        # logger.debug(f"GPT response: {model_response}")


        # iterate through the end of the response, to get the final emoji
        emojis =  ["⬆️", "⬇️", "⬅️", "➡️"]
        last_index = -1
        for e in emojis:
            current_index = model_response.content.rfind(e)
            if current_index > last_index:
                last_index = current_index

        emoji = model_response.content[last_index:last_index+len("⬆️")].strip() if last_index != -1 else None
        # logger.debug(f"Emoji found in GPT response: {emoji}")
        # logger.debug(f"GPT response: {model_response.content}")

        # Getting the direction from the LLM response and the arrow emoji in it
        managed_to_gen = True
        if "⬆️" == emoji:
            dir = "U"
        elif "⬇️" == emoji:
            dir = "D"
        elif "⬅️" == emoji:
            dir = "L"
        elif "➡️" == emoji:
            dir = "R"
        else: 
            managed_to_gen = False
            dir = random.choice(["U", "D", "L", "R"])
            logger.error("GPT didn't return a valid direction")
            logger.error(f"GPT response: {model_response}")

        # if we sample, choose the legal move
        if sample and not state.try_move(dir, state.snakes[self.snake_idx]):
            possible_moves = state.get_all_possible_moves(self.snake_idx)
            if not possible_moves:
                dir = random.choice(["U", "D", "L", "R"])
            else:
                if not managed_to_gen:
                    dir = random.choice(["U", "D", "L", "R"])
                if dir not in possible_moves:
                    dir = random.choice(possible_moves)
        
        return dir, model_response

