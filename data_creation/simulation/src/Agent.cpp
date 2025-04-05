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

bool is_position_in_set(pair<int, int> position, set<pair <int, int> > positions){
    return positions.find({position.first, position.second}) != positions.end();
}

bool is_position_out_of_bounds(int x, int y, int board_width, int board_height){
    return x < 0 || x >= board_width || y < 0 || y >= board_height;

}

char Agent::bfs_based_agent(
                const vector<Snake>& snakes,
                const vector<pair<int, int> >& apples,
                int current_snake_idx,
                int board_width,
                int board_height
            )
        // heuristic is based on finding the shortest path to the apple, while knowing
        // about potential collisions
        // next best position is determined by the shortest distance needed to be taken
        // from current position to the apple, while avoiding any obstacles
        {

            int best_distance = INFINITY;
            char best_dir = 'U';

            // get current snake position
            int x = snakes[current_snake_idx].head.first;
            int y = snakes[current_snake_idx].head.second;

        
            set<pair <int, int> > apples_positions(apples.begin(), apples.end());
            set<pair <int, int> > snake_positions = get_positions_occupiend_by_snakes(current_snake_idx, snakes);

            // stores current position, distance, direction
            queue<tuple< pair<int, int>, int, char> > queue;
            set<pair<int, int> > visited;

            // initially try to go in every direction
            queue.push(make_tuple(make_pair(x - 1, y), 1, 'U'));
            queue.push(make_tuple(make_pair(x + 1, y), 1, 'D'));
            queue.push(make_tuple(make_pair(x, y - 1), 1, 'L'));
            queue.push(make_tuple(make_pair(x, y + 1), 1, 'R'));


            while (!queue.empty()){
                auto [current_position, distance, dir] = queue.front();
                queue.pop();

                // position already visited
                if (is_position_in_set(current_position, visited) || is_position_out_of_bounds(current_position.first, current_position.second, board_width, board_height)){
                    continue;
                }

                visited.insert(current_position);

                // run to the other snake
                if (is_position_in_set(current_position, snake_positions)){
                    continue;
                }
                
                // found an apple
                if (is_position_in_set(current_position, apples_positions)){
                    if (distance < best_distance){
                        best_distance = distance;
                        best_dir = dir;
                        continue;
                    }
                }

                queue.push(make_tuple(make_pair(current_position.first - 1, current_position.second), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first + 1, current_position.second), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first, current_position.second - 1), distance + 1, dir));
                queue.push(make_tuple(make_pair(current_position.first, current_position.second + 1), distance + 1, dir));

            }

        if (best_distance == INFINITY){
            // if no path to the apple is found, go in any free direction
            if (!is_position_in_set(make_pair(x - 1, y), snake_positions)){
                best_dir = 'U';
            }
            else if (!is_position_in_set(make_pair(x + 1, y), snake_positions)){
                best_dir = 'D';
            }
            else if (!is_position_in_set(make_pair(x, y - 1), snake_positions)){
                best_dir = 'L';
            }
            else if (!is_position_in_set(make_pair(x, y + 1), snake_positions)){
                best_dir = 'R';
            }
            else{
                // go in any random direction
                best_dir = getRandomChar();
            }
        }
        return best_dir;

        }
    
    