
from state import State
from snake import Snake
from apple import Apple
import json

class Serializer:
     #  {
    #         "n_snakes": 2,
    #         "n_apples": 5,
    #         "board_width": 10,
    #         "board_height": 10,
    #         "turn":10,
    #         "snakes": [
    #             {
    #                 "id": 0,
    #                 "head": [x, y],
    #                 "tail": [
    #                     [x1, y1],
    #                     [x2, y2],
    #                     ...
    #                 ],
    #                 "moves_history": [
    #                     [x1, y1],
    #                     [x2, y2],
    #                     ...
    #                 ]
    #             },
    #             ...
    #         ],
    #         "apples": [
    #             {
    #                 "position": [x, y]
    #             },
    #             ...
    #         ],
    #         "eliminated_snakes": [0, 1, ...]
    #     }

    @staticmethod
    def serialize_state(state: State) -> str:
        jsonState = {
            "n_snakes": state.n_snakes,
            "n_apples": state.n_apples,
            "board_width": state.board_width,
            "board_height": state.board_height,
            "turn": state.turn,
            "snakes": [],
            "apples": [],
            "eliminated_snakes": list(state.eliminated_snakes),
            "idx_prev_snake": state.idx_prev_snake,
            "whoose_prev_turn": "py"
        }

        for i, snake in enumerate(state.snakes):
            snake_json = {
                "id": i,
                "head": [snake.head[0], snake.head[1]],
                "tail": [[x[0], x[1]] for x in snake.tail],
                "moves_history": [[x[0], x[1]] for x in snake.moves_history]
            }
            jsonState["snakes"].append(snake_json)

        jsonState["apples"] = [[apple.position[0], apple.position[1]] for apple in state.apples]

        return json.dumps(jsonState)
    
    @staticmethod
    def deserialize_state(jsonState: str) -> State:
        # print(jsonState)
        try:
            stateJson = json.loads(jsonState)
            n_snakes = stateJson["n_snakes"]
            n_apples = stateJson["n_apples"]
            board_width = stateJson["board_width"]
            board_height = stateJson["board_height"]
            turn = stateJson["turn"]

            # deserialization
            idx_prev_snake = stateJson["idx_prev_snake"]
            whoose_prev_turn = stateJson["whoose_prev_turn"]

            snakes = []
            apples = []

            for i in range(n_snakes):
                snake_json = stateJson["snakes"][i]
                snake = Snake(snake_json["head"][0], snake_json["head"][1])
                snake.tail = snake_json["tail"]
                snake.moves_history = snake_json["moves_history"]
                snakes.append(snake)

            for apple_position in stateJson["apples"]:
                x, y = apple_position
                apple = Apple(x, y)
                apples.append(apple)

            eliminated_snakes = set(stateJson["eliminated_snakes"])

            state = State(n_snakes, n_apples, board_width, board_height)
            state.turn = turn
            state.snakes = snakes
            state.apples = apples
            state.eliminated_snakes = eliminated_snakes
            state.idx_prev_snake = idx_prev_snake
            state.whoose_prev_turn = whoose_prev_turn
            return state
        except Exception as e:
            print(e)
