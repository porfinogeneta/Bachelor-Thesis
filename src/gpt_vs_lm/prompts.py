# Available models list to be used in the app
AVAILABLE_MODELS = [
    "openai gpt-3.5-turbo",
    "openai gpt-4-1106-preview (GPT-4 Turbo)",
    "openai gpt-4",
]


# # Default prompts for the initial layout 
# DEFAULT_PROMPT1 = [
# """You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
# You can eat food to grow. If you hit a wall or another snake, you die. The game ends when one of the snakes dies. You are compiting against another snake.""",

# """You are the snake1, which is the color green. Your opponent is the snake2 with color blue. This is the game board in emojis where heads are rounds, bodies are squares and food is an apple: 
# {emojis_board}

# and this is the board state in JSON, positions are in (x, y) format, the game board size is 15 by 15, x goes from 0 to 14 left to right and y goes 0 to 14 up to down: 
# {board_state_str}

# The snake dir parameter is the first letter of the previous chosen direction of the snake, if you chose an opposite direction you will die as you will collide with your own body.
# You have to shortly reason your next move in 1-3 lines and then always add one of the following emojis: ⬆️, ⬇️, ⬅️, ➡️ (for <up>, <down>, <left> and <right>) to chose the direction of your next move.
# Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.""",
# ]


DEFULATT_PROMPT1 = ["""



"""]


DEFAULT_PROMPT = ["""You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You have to eat food to grow. If you hit a wall, another snake or your tail, you die. The game ends when one of the snakes is dead and the alive one is longer. You are compiting against another snake.""",

"""You are the snake{snake_idx}, which is the letter G. Your opponent is the snake{opponent_idx} with letter L. This is the game board in characters where heads are 'G' and 'L', bodies are 'g' and 'l' and food is 'A'. Empty cells are marked with '_'. 
Every line starts also with its number which is at the same time the row coordinate for that line. The first line contains the column numbers. 
Characters board:
{chars_board}

and this is the board state in JSON, positions are in (row, col) format, the game board size is 10 by 10, row goes from 0 to 9 up to bottom and col goes 0 to 9 left to right: 
{board_state_str}

For instance if your head is at (0,0) and the nearest food is at (1,1):
- moving ⬅️ <left> to (0,-1) is not possible, you will die as you hit the wall
- moving ➡️ <right> to (0,1) is possible, you will be at (0,1)
- moving ⬆️ <up> to (-1,0) is not possible, you will die as you hit the wall
- moving ⬇️ <down> to (1,0) is possible, you will be at (1,0)


For instance if your head is at (9,8), the nearest food is at (6,7), you have a tail at (8,8), (7,8) and previously moved ⬇️ <down>:
- moving ⬅️ <left> to (9,7) is possible, you will be at (9,7)
- moving ➡️ <right> to (9,9) is possible, you will be at (9,9)
- moving ⬆️ <up> to (8,8) is not possible, you will be at (8,8) and you will die as you hit your own tail
- moving ⬇️ <down> to (10,8) is not possible, you will die as you hit the wall

As you can see moving ⬇️ <down> increases the row coordinate (+1,_) and moving ⬆️ <up> decreases it (-1,_) , while moving ➡️ <right> increases the column coordinate (_,+1) and moving ⬅️ <left> decreases it (_,-1).

The snake direction parameter is the first letter of the previously chosen direction of the snake, if you chose an opposite direction you will die as you will, because you collide with your own body.
So for previous direction 'U' (<up>) you cannot choose ⬇️ (<down>), for 'D' (<down>) you cannot choose ⬆️ (<up>), for 'L' (<left>) you cannot choose ➡️ (<right>) and for 'R' (<right>) you cannot choose ⬅️ (<left>).
You have to shortly reason your next move in 1-3 lines and then always add one of the following emojis: ⬆️, ⬇️, ⬅️, ➡️ (for <up>, <down>, <left> and <right>) to chose the direction of your next move.
Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.

Make the following Chain of Thought in few words:
1. Locate yourself and your head in the chars map (the <G> char) and the (x, y) coordinates from the board state (the head of Snake{snake_idx} in the JSON board state, the tail parts are ordered from the first added segment to the last one)
2. Locate the closest food
3. Chose the direction to move on cell closer to the food, check if you will die/lose there and if so chose another direction
4. Finally output the emoji for the direction you chose"""]
