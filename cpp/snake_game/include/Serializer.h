#ifndef SERIALIZER_H
#define SERIALIZER_H

#include <string>
#include <iostream>
#include <vector>
#include <utility>
#include <sstream>
#include "State.h"
#include "Snake.h"
#include "Apple.h"
#include <set>
#include <nlohmann/json.hpp>

using namespace std;

class Serializer {
public:

    string serialize_apple(Apple &apple);

    /*    JSON serialization format:
        {
            "id": 0,
            "head": [x, y],
            "tail": [
                [x1, y1],
                [x2, y2],
                ...
            ],
            "moves_history": [
                [x1, y1],
                [x2, y2],
                ...
            ]
        }
    */
    string serialize_snake(Snake &snake); 


    /**
      
        {
            "n_snakes": 2,
            "n_apples": 5,
            "board_width": 10,
            "board_height": 10,
            "turn":10,
            "snakes": [
                {
                    "id": 0,
                    "head": [x, y],
                    "tail": [
                        [x1, y1],
                        [x2, y2],
                        ...
                    ],
                    "moves_history": [
                        [x1, y1],
                        [x2, y2],
                        ...
                    ]
                    ...
                } 
            ],
            "apples": [
                {
                    "position": [x, y]
                },
                ...
            ],
            "eliminated_snakes": [0, 1, ...]
        }
     */
    string serialize_state(State& state);

    State deserialize_state(const string& serialized_state);
};

#endif