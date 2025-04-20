#include "Agent.h"
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

bool is_position_out_of_bounds(int x, int y, int board_width, int board_height){
    return x < 0 || x >= board_width || y < 0 || y >= board_height;
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
                if (is_position_in_set(current_position, visited) || is_position_out_of_bounds(current_position.first, current_position.second, state.board_width, state.board_height)){
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
            if (!is_position_in_set(make_pair(x - 1, y), snake_positions) && !is_position_out_of_bounds(x - 1, y, state.board_width, state.board_height)){
                viable_moves.push_back('U');
                // best_dir = 'U';
            }
            if (!is_position_in_set(make_pair(x + 1, y), snake_positions) && !is_position_out_of_bounds(x + 1, y, state.board_width, state.board_height)){
                // best_dir = 'D';
                viable_moves.push_back('D');
            }
            if (!is_position_in_set(make_pair(x, y - 1), snake_positions) && !is_position_out_of_bounds(x, y - 1, state.board_width, state.board_height)){
                viable_moves.push_back('L');
            //     best_dir = 'L';
            }
            if (!is_position_in_set(make_pair(x, y + 1), snake_positions) && !is_position_out_of_bounds(x, y + 1, state.board_width, state.board_height)){
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
    
    