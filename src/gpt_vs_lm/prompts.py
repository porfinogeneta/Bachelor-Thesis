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


# DEFAULT_PROMPT = ["""You are an expert snake playing agent. You are competing in a tournament with another snake. The rules
#                    of the tournament are to gather more apples than the enemy, so your main objective should be apples eating.
#                    The board size is 10x10. The coordinates used are row, column coordinates similar to the indexing
#                    in a 2d list. Coordinates range from (0,0) at top left to (9,9) at bottom right.
#                    """,
                   
#                    """


#                     Rules:
#                     1. If you eat an apple you grow 1 point.
#                     2. If you go out of bounds (outside the range of listed coordinates), another snake, or yourself (tail or you go backwards), you die.
#                     3. The goal is to have more apples eaten at the end of the game.

#                     You have the following moves allowed:
#                     -  ⬇️ -> increases the row coordinate (+1,_)
#                     -  ⬆️ -> decreases the row coordinate (-1,_) 
#                     -  ➡️ -> increases the column coordinate (_,+1)
#                     -  ⬅️ -> decreases the column coordinate (_,-1)

#                     You can think out loud first and reason, then respond with the move.

#                     You may create a proper strategy that you might want to tell yourself next turn.

#                     ALWAYS end your reasoning with a decision: ⬇️, ⬆️, ➡️, ⬅️ . You HAVE TO provide your DECISION!


#                     Apples at: [(1,2), (2,8), (5,4), (7,4), (9,0)]

#                     You are: Snake G
#                     Your head: (3,7)
#                     Your tail: [(3,8), (3,9), (4,9)]
                   

#                     Enemy is: Snake L
#                     Enemy's head: (0,5)
#                     Enemy's tail: [(0,6), (1,6), (2,6), (2,7)]

                    
#                     Game Board:
                    
#                       0 1 2 3 4 5 6 7 8 9
#                     0 _ _ _ _ _ L l _ _ _
#                     1 _ _ A _ _ _ l _ _ _
#                     2 _ _ _ _ _ _ l l A _
#                     3 _ _ _ _ _ _ _ G g g
#                     4 _ _ _ _ _ _ _ _ _ g
#                     5 _ _ _ _ A _ _ _ _ _
#                     6 _ _ _ _ _ _ _ _ _ _
#                     7 _ _ _ _ A _ _ _ _ _
#                     8 _ _ _ _ _ _ _ _ _ _
#                     9 A _ _ _ _ _ _ _ _ _

#                     Your previous move was: ⬅️

#                     Rationale: 
                    
#                     I notice that (5,4) is the closest apple from my head at (3,7) (it's 5 steps away in Manhattan distance),
#                     and it's away from the enemy snake at (0,5). The move options for my turn are as follows:
#                     -  ⬇️ -> goes to (3,8)
#                     -  ⬆️ -> goes to (4,7)
#                     -  ➡️ -> goes to (3,8)
#                     -  ⬅️ -> goes to (3,6)

#                     Moving ➡️  would bring me closer to an apple, but is certainly not an option because I would collide with my own tail, at position (3,8). Moving ⬆️ is also a bad idea
#                     as I would collide with my enemy's tail, at position (2,7). I can go ⬅️ or ⬇️. Both directions move me closer to the apple at position
#                     (5,4). I choose ⬇️ because it takes me further from the enemy. 
#                     I always need to end my Rationale with a decision, this time I decide to go: ⬅️
                    
#                     DECISION: ⬅️

                    
#                     Apples at: {apples}

#                     You are: Snake G
#                     Your head: {head}
#                     Your tail: {tail}
                   

#                     Enemy is: Snake L
#                     Enemy's head: {enemy_head}
#                     Enemy's tail: {enemy_tail}

                    
#                     Game Board:
                    
#                     {game_board}

#                     Your previous move was: {previous_move}    

#                     Rationale:

#                     """
#                    ]


DEFAULT_PROMPT = ["""You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You have to eat food to grow. If you hit a wall, another snake or your tail, you die. The game ends when one of the snakes is dead and the alive one is longer. You are compiting against another snake.""",

"""You are the snake{snake_idx}, which is the letter G. Your opponent is the snake{opponent_idx} with letter L. This is the game board in characters where heads are 'G' and 'L', bodies are 'g' and 'l' and food is 'A'. Empty cells are marked with '_'. 
Every line starts also with its number which is at the same time the row coordinate for that line. The first line contains the column numbers. 
Characters board:
{chars_board}

and this is the board state in JSON, positions are in (row, col) format, the game board size is 10 by 10, row goes from 0 to 9 up to bottom and col goes 0 to 9 left to right: 
{board_state_dict}

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


# DEFAULT_PROMPT = ["""You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
# You have to eat food to grow. If you hit a wall, another snake or your tail, you die. The game ends when one of the snakes is dead and the alive one is longer. You are compiting against another snake.""",

# """You are the snake represented with a letter G. Your opponent is the snake represented with a letter L. This is the game board in characters where heads are 'G' and 'L', bodies are 'g' and 'l' and food is 'A'. Empty cells are marked with '_'. 
# Every line starts also with its number which is at the same time the row coordinate for that line. The first line contains the column numbers. 

# Rules:
# 1. If you eat an apple you grow 1 point.
# 2. If you go out of bounds, (either of you coordinates is < 0 or > 9), another snake, or yourself (tail or you go backwards), you die.
# 3. The goal is to have more apples eaten at the end of the game.

# You have the following moves allowed:
# -  ⬇️ -> increases the row coordinate (+1,_)
# -  ⬆️ -> decreases the row coordinate (-1,_) 
# -  ➡️ -> increases the column coordinate (_,+1)
# -  ⬅️ -> decreases the column coordinate (_,-1)


# Game Board:

#   0 1 2 3 4 5 6 7 8 9
# 0 _ _ _ _ _ L l _ _ _
# 1 _ _ A _ _ _ l _ _ _
# 2 _ _ _ _ _ _ l l A _
# 3 _ _ _ _ _ _ _ G g g
# 4 _ _ _ _ _ _ _ _ _ g
# 5 _ _ _ _ A _ _ _ _ _
# 6 _ _ _ _ _ _ _ _ _ _
# 7 _ _ _ _ A _ _ _ _ _
# 8 _ _ _ _ _ _ _ _ _ _
# 9 A _ _ _ _ _ _ _ _ _

# Your previous move was: ⬅️

# Apples at: [(1,2), (2,8), (5,4), (7,4), (9,0)]

# You are: Snake G
# Your head: (3,7)
# Your tail: [(3,8), (3,9), (4,9)]


# Enemy is: Snake L
# Enemy's head: (0,5)
# Enemy's tail: [(0,6), (1,6), (2,6), (2,7)]

# 1. My head is in a field (3,7).
# 2. Closest food is in a field (2,8) and (5,4).
# 3. Even though the closest food is at (2,8) I cannot move there right now, because if I move ➡️ I would collide with my own tail at (3,8), it's an oppositte move to my current direction ,
# I also cannot move ⬆️ because I would collide with my enemy at (2,7). So my only option is to move ⬅️ or ⬇️.
# 4. Decision ⬅️ .


# Game Board:

# {game_board}

# Your previous move was: {previous_move}  

# Apples at: {apples}

# You are: Snake G
# Your head: {head}
# Your tail: {tail}


# Enemy is: Snake L
# Enemy's head: {enemy_head}
# Enemy's tail: {enemy_tail}

# Make the following Chain of Thought in few words:
# 1. Locate yourself and your head in the chars map (the <G> char).
# 2. Locate the closest food
# 3. Chose the direction to move on cell closer to the food, check if you will die/lose there and if so chose another direction
# 4. Finally output the emoji for the direction you chose"""]