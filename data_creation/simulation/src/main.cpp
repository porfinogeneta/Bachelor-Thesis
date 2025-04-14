#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <random>
#include <set>
#include "State.h"
#include "Agent.h"


int main(int argc, char* argv[]) {

    // game configs
    int n_snakes = 2;
    int n_apples = 5;
    int board_width = 10;
    int board_height = 10;

    if (argc < 2){
        cout << "Usage: " << argv[0] << " <log_file_name>" << endl;
        return 1;
    }

    string filename = argv[1];

    int turn = 0;

    State state = State(n_snakes, n_apples, board_width, board_height, filename);

    Agent agent = Agent();

    while (!state.is_game_over())
    {
        
        state.print_game_state(turn);
        int snake_moving_idx = turn % n_snakes;
        // this is the place where agent will come and decide on move
        // char direction = random_agent.getRandomChar();
        // snake was eliminated, there is no need to move it
        if (state.eliminated_snakes.find(snake_moving_idx) != state.eliminated_snakes.end()){
            turn++;
            continue;
        }
        char direction = agent.bfs_based_agent(state, snake_moving_idx);

        state.move(direction, snake_moving_idx);
        
        turn++;
    }
    state.print_game_state(turn);

    
    return 0;
}