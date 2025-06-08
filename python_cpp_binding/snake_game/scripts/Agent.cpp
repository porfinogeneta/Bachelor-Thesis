#include "Agent.h"
#include "MCTS.h"
#include <random>
#include <queue>
#include <tuple>
#include <set>

    
char Agent::getRandomChar() {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distr(0, 3);

    return directions[distr(gen)];
};
// returns positions occupied by snakes and current snake's body
set<pair<int, int> > get_positions_occupiend_by_snakes(size_t current_snake_idx, const vector<Snake>& snakes){
    
    set<pair<int, int> > snake_occupied_positions;

    for (size_t i = 0; i < snakes.size(); i++){
        if (i != current_snake_idx){
            snake_occupied_positions.insert(snakes[i].head);
        }
        snake_occupied_positions.insert(snakes[i].tail.begin(), snakes[i].tail.end());
    }

    return snake_occupied_positions;
}


set<pair<int, int> > get_positions_occupied_by_apples(const vector<Apple>& apples){
    set<pair<int, int> > apple_occupied_positions;

    for (const auto& apple : apples){
        apple_occupied_positions.insert(apple.position);
    }

    return apple_occupied_positions;
}

bool is_position_in_set(pair<int, int> position, set<pair <int, int> > positions){
    return positions.find({position.first, position.second}) != positions.end();
}

bool is_position_out_of_bounds(pair<int, int> position, int board_width, int board_height){
    return position.first < 0 || position.first >= board_width || position.second < 0 || position.second >= board_height;
}

// returns random pair from vector
char chose_random_vector_element(const vector<char>& vec){
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distr(0, vec.size() - 1);

    return vec[distr(gen)];
}

char Agent::bfs_based_agent(
                const State &state,
                int current_snake_idx
            )
        // heuristic is based on finding the shortest path to the apple, while knowing
        // about potential collisions
        // next best position is determined by the shortest distance needed to be taken
        // from current position to the apple, while avoiding any obstacles
    {

            int best_distance = 10000;
            // char best_dir = 'U';

            // get current snake position
            int x = state.snakes[current_snake_idx].head.first;
            int y = state.snakes[current_snake_idx].head.second;

        
            set<pair <int, int> > apples_positions = get_positions_occupied_by_apples(state.apples);
            set<pair <int, int> > snake_positions = get_positions_occupiend_by_snakes(current_snake_idx, state.snakes);

            // stores current position, distance, direction
            queue<tuple< pair<int, int>, int, char> > queue;
            set<pair<int, int> > visited;

            // initially try to go in every direction
            queue.push(make_tuple(make_pair(x - 1, y), 1, 'U'));
            queue.push(make_tuple(make_pair(x + 1, y), 1, 'D'));
            queue.push(make_tuple(make_pair(x, y - 1), 1, 'L'));
            queue.push(make_tuple(make_pair(x, y + 1), 1, 'R'));

            // viable moves, vector of pairs, that would allow to choose random direction from
            // all best directions
            vector<char> viable_moves;

            while (!queue.empty()){
                auto [current_position, distance, dir] = queue.front();
                queue.pop();

                // position already visited
                if (is_position_in_set(current_position, visited) || is_position_out_of_bounds(current_position, state.board_width, state.board_height)){
                    continue;
                }

                visited.insert(current_position);

                // run to the other snake
                if (is_position_in_set(current_position, snake_positions)){
                    continue;
                }
                
                // found an apple
                if (is_position_in_set(current_position, apples_positions)){
                    // cout << "Found an apple at (" << current_position.first << ", " << current_position.second << ")" << endl;
                    if (distance < best_distance){
                        // update distance and direction
                        best_distance = distance;
                        // best_dir = dir;

                        // new best distance, clear viable moves
                        viable_moves.clear();
                        viable_moves.push_back(dir);
                        continue;
                    }else if (distance == best_distance){
                        // if the distance is the same, add to viable moves
                        viable_moves.push_back(dir);
                    }
                }

                queue.push(make_tuple(make_pair(current_position.first - 1, current_position.second), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first + 1, current_position.second), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first, current_position.second - 1), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first, current_position.second + 1), distance + 1, dir));

            }
        // cout << "Best distance to the apple: " << best_distance << endl;
        if (best_distance == 10000){
            // cout << "No path to the apple found" << endl;
            // if no path to the apple is found, go in any free direction (not in snake and not out of bounds)
            if (!is_position_in_set(make_pair(x - 1, y), snake_positions) && !is_position_out_of_bounds(make_pair(x - 1, y), state.board_width, state.board_height)){
                viable_moves.push_back('U');
                // best_dir = 'U';
            }
            if (!is_position_in_set(make_pair(x + 1, y), snake_positions) && !is_position_out_of_bounds(make_pair(x + 1, y), state.board_width, state.board_height)){
                // best_dir = 'D';
                viable_moves.push_back('D');
            }
            if (!is_position_in_set(make_pair(x, y - 1), snake_positions) && !is_position_out_of_bounds(make_pair(x, y - 1), state.board_width, state.board_height)){
                viable_moves.push_back('L');
            //     best_dir = 'L';
            }
            if (!is_position_in_set(make_pair(x, y + 1), snake_positions) && !is_position_out_of_bounds(make_pair(x, y + 1), state.board_width, state.board_height)){
                viable_moves.push_back('R');
                // best_dir = 'R';
            }
            
            if (viable_moves.size() == 0){
                // if no free direction is found, go in any direction
                // best_dir = getRandomChar();
                viable_moves.push_back(getRandomChar());
            }
        }
        return chose_random_vector_element(viable_moves);

    }


char Agent::random_based_agent(const State &state, int current_snake_idx) {

        // this agent is based on choosing a position that is either empty or contains an apple
        // whenever possible we choose position that won't cause the snake's suicide, i.e. is not
        // in any of the snakes bodies and is not out of bounds, we favour positions with apples,
        // we increase probability of a position being chosen by giving viable moves apple moves only
        // if there are any nearby

        // get current snake position
        int x = state.snakes[current_snake_idx].head.first;
        int y = state.snakes[current_snake_idx].head.second;


        set<pair <int, int> > apples_positions = get_positions_occupied_by_apples(state.apples);
        set<pair <int, int> > snake_positions = get_positions_occupiend_by_snakes(current_snake_idx, state.snakes);

        // possible positions, from them we sample
        vector<char> viable_normal_moves;
        vector<char> viable_apple_moves;

        // create viable moves, greedy approach of always choosing position with an apple and free position
        // if nothing is available, greedy approach ensures shorter games, since snakes grow quicker
        pair<int, int> current_snake_head = state.snakes[current_snake_idx].head;
        // UP
        pair<int, int> up_pair = make_pair(current_snake_head.first - 1, current_snake_head.second);
        if (!is_position_in_set(up_pair, snake_positions) && !is_position_out_of_bounds(up_pair, state.board_width, state.board_height)){
            if (is_position_in_set(up_pair, apples_positions)){
                viable_apple_moves.push_back('U');
            }else
                viable_normal_moves.push_back('U');
        }

        // DOWN
        pair<int, int> down_pair = make_pair(current_snake_head.first + 1, current_snake_head.second);
        if (!is_position_in_set(down_pair, snake_positions) && !is_position_out_of_bounds(down_pair, state.board_width, state.board_height)){
            if (is_position_in_set(down_pair, apples_positions)){
                viable_apple_moves.push_back('D');
            }else
                viable_normal_moves.push_back('D');
        }

        // LEFT
        pair<int, int> left_pair = make_pair(current_snake_head.first, current_snake_head.second - 1);
        if (!is_position_in_set(left_pair, snake_positions) && !is_position_out_of_bounds(left_pair, state.board_width, state.board_height)){
            if (is_position_in_set(left_pair, apples_positions)){
                viable_apple_moves.push_back('L');
            }else
                viable_normal_moves.push_back('L');
        }

        // RIGHT
        pair<int, int> right_pair = make_pair(current_snake_head.first, current_snake_head.second + 1);
        if (!is_position_in_set(right_pair, snake_positions) && !is_position_out_of_bounds(right_pair, state.board_width, state.board_height)){
            if (is_position_in_set(right_pair, apples_positions)){
                viable_apple_moves.push_back('R');
            }else
                viable_normal_moves.push_back('R');
        }


        // leave only apple positions if present, otherwise leave only free positions
        // otherwise return random move
        vector<char> viable_moves;

        if (viable_apple_moves.empty()){
            if (viable_normal_moves.empty()){
                viable_moves.push_back(getRandomChar());
            }else {
                viable_moves = viable_normal_moves;
            }
        }else {
            viable_moves = viable_apple_moves;
        }



    // randomy sample move
    return chose_random_vector_element(viable_moves);

}

// char Agent::manhattan_distance(
//                 const pair<int, int> &a,
//                 const pair<int, int> &b
//             ){
//         // calculate manhattan distance between two points
//         return abs(a.first - b.first) + abs(a.second - b.second);
//     }


// char Agent::greedy_based_agent(
//                 const State &state,
//                 int current_snake_idx
//             ){
//         // this agent is based on choosing a position that is would lead to be closer to the apple
//         // whenever possible we choose position that won't cause the death of the snake
        
//         // get current snake position
//         int x = state.snakes[current_snake_idx].head.first;
//         int y = state.snakes[current_snake_idx].head.second;


//         set<pair <int, int> > apples_positions = get_positions_occupied_by_apples(state.apples);
//         set<pair <int, int> > snake_positions = get_positions_occupiend_by_snakes(current_snake_idx, state.snakes);

//         int min_dist = std::numeric_limits<int>::max();

//         pair<int, int> closest_apple = make_pair(x, y);

//         if (!state.apples.empty()) {
//             for (const auto& apple : state.apples) {
//                 int dist = manhattan_distance(head, apple);
//                 if (dist < min_dist) {
//                     min_dist = dist;
//                     closest_apple = apple.position;
//                 }
//             }
//         }

//         vector<char> possible_moves = state.get_all_possible_moves(snake_turn);

//         if (possible_moves.empty()) {
//             return 'U';
//         }

//         // Score moves: positive is good, negative is bad
//         map<char, int> move_scores;

//         for (char move : possible_moves) {
//             state.move(move, snake_turn);
//             int score = 0;

//             // is the head after the move in apples
//             if (state.is_apple_at(next_pos)) {
//                 score += 1000;
//             }

//             // Rule 2: Medium priority - does this move get closer to the nearest apple?
//             if (closest_apple.x != -1) {
//                 int dist_after_move = manhattan_distance(next_pos, closest_apple);
//                 if (dist_after_move < min_dist) {
//                     score += 100; // Reward for getting closer
//                 }
//             }
            
//             // Rule 3: Low priority - try to move towards the center to have more space
//             // (Assuming you have board_width and board_height in your state)
//             // int center_x = state.board_width / 2;
//             // int center_y = state.board_height / 2;
//             // int dist_from_center_now = manhattan_distance(head, {center_x, center_y});
//             // int dist_from_center_next = manhattan_distance(next_pos, {center_x, center_y});
//             // if(dist_from_center_next < dist_from_center_now){
//             //     score += 10;
//             // }

//             move_scores[move] = score;
//         }

//         // Find the move with the best score
//         char best_move = possible_moves[0];
//         int max_score = -1;

//         for (const auto& pair : move_scores) {
//             if (pair.second > max_score) {
//                 max_score = pair.second;
//                 best_move = pair.first;
//             }
//         }

//         return best_move;
// }


char Agent::mcts_based_agent(
                const State &state,
                int current_snake_idx,
                int iterations = 1000
            )
        {
            MCTS mcts;
            mcts.set_rollout_policy([this](const State& s, int idx) { return random_based_agent(s, idx); });
            return mcts.find_best_move(state, current_snake_idx, iterations);
        }
    