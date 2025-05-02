#include "Serializer.h"



string Serializer::serialize_apple(Apple &apple) {
    return "[" + to_string(apple.position.first) + ", " + to_string(apple.position.second) + "]";
}


string Serializer::serialize_snake(Snake &snake) {
    string json = "\"head\": [" + to_string(snake.head.first) + ", " + to_string(snake.head.second) + "], \"tail\": [";
    for (size_t i = 0; i < snake.tail.size(); ++i) {
        json += "[" + to_string(snake.tail[i].first) + ", " + to_string(snake.tail[i].second) + "]";
        if (i < snake.tail.size() - 1) {
            json += ", ";
        }
    }
    json += "]";

    // MAYBE HISTORY SERIALIZATION WOULD MAKE SENSE LATER ON, right now it's a waste of memory
    // add moves history
    json += ", \"moves_history\": [";
    for (size_t i = 0; i < snake.moves_history.size(); ++i) {
        json += "[" + to_string(snake.moves_history[i].first) + ", " + to_string(snake.moves_history[i].second) + "]";
        if (i < snake.moves_history.size() - 1) {
            json += ", ";
        }
    }
    json += "]";

    return json;
}


string Serializer::serialize_state(State& state){

    string json = "{ \"n_snakes\": " + to_string(state.n_snakes) + ", \"n_apples\": " + to_string(state.n_apples) + ", \"board_width\": " + to_string(state.board_width) + ", \"board_height\": " + to_string(state.board_height) + ", \"turn\": " + to_string(state.turn) + ", \"snakes\": [";
    
    for (size_t i = 0; i < state.snakes.size(); ++i) {
        json += "{ \"id\": " + to_string(i) + ", ";
        json += serialize_snake(state.snakes[i]);
        json += "}";
        if (i < state.snakes.size() - 1) {
            json += ", ";
        }
    }
    
    json += "], \"apples\": [";
    
    for (size_t i = 0; i < state.apples.size(); ++i) {
        json += serialize_apple(state.apples[i]);
        if (i < state.apples.size() - 1) {
            json += ", ";
        }
    }
    
    json += "], \"eliminated_snakes\": [";
    
    for (const auto& snake_idx : state.eliminated_snakes) {
        json += to_string(snake_idx);
        if (snake_idx != *state.eliminated_snakes.rbegin()) {
            json += ", ";
        }
    }
    
    json += "],";    
    json += "\"idx_prev_snake\":" + to_string(state.idx_prev_snake) + ",";
    json += "\"whoose_prev_turn\": \"cpp\"";
    json += "}";
    
    return json;
}


State Serializer::deserialize_state(const string& serialized_state){
    nlohmann::json jsonData = nlohmann::json::parse(serialized_state);
    int n_snakes = jsonData["n_snakes"];
    int n_apples = jsonData["n_apples"];
    int board_width = jsonData["board_width"];
    int board_height = jsonData["board_height"];
    int turn = jsonData["turn"];
    int idx_prev_snake = jsonData["idx_prev_snake"];
    string whoose_prev_turn = jsonData["whoose_prev_turn"];
    vector<Snake> snakes;
    
    for (const auto& snake_data : jsonData["snakes"]) {
        int id = snake_data["id"];
        int head_x = snake_data["head"][0];
        int head_y = snake_data["head"][1];
        Snake snake(head_x, head_y);
        
        for (const auto& tail_segment : snake_data["tail"]) {
            int tail_x = tail_segment[0];
            int tail_y = tail_segment[1];
            snake.tail.push_back(make_pair(tail_x, tail_y));
        }
        
        // MAYBE HISTORY SERIALIZATION WOULD MAKE SENSE LATER ON, right now it's a waste of memory
        for (const auto& move : snake_data["moves_history"]) {
            int move_x = move[0];
            int move_y = move[1];
            snake.moves_history.push_back(make_pair(move_x, move_y));
        }
        
        snakes.push_back(snake);
    }
    vector<Apple> apples;
    for (const auto& apple_data : jsonData["apples"]) {
        int apple_x = apple_data[0];
        int apple_y = apple_data[1];
        Apple apple(apple_x, apple_y);
        apples.push_back(apple);
    }
    set<int> eliminated_snakes;
    for (const auto& snake_idx : jsonData["eliminated_snakes"]) {
        eliminated_snakes.insert(snake_idx.get<int>());
    }
    State state(n_snakes, n_apples, board_width, board_height);
    state.turn = turn;
    state.snakes = snakes;
    state.apples = apples;
    state.eliminated_snakes = eliminated_snakes;
    state.idx_prev_snake = idx_prev_snake;
    state.whoose_prev_turn = whoose_prev_turn;
    return state;
}
