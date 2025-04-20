#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <random>
#include <set>
#include <sys/socket.h>
#include "../include/State.h"
#include "../include/Agent.h"




// game configs
int n_snakes = 2;
int n_apples = 5;
int board_width = 10;
int board_height = 10;

int main() {


    // if (argc < 2){
    //     cout << "Usage: " << argv[0] << " <log_file_name>" << endl;
    //     return 1;
    // }

    
    // string filename = argv[1];

    State state = State(n_snakes, n_apples, board_width, board_height);

    Agent agent = Agent();

    while (!state.is_game_over())
    {
        
        state.print_game_state();
        int snake_moving_idx = state.turn % n_snakes;
        // this is the place where agent will come and decide on move
        // char direction = random_agent.getRandomChar();
        // snake was eliminated, there is no need to move it
        if (state.eliminated_snakes.find(snake_moving_idx) != state.eliminated_snakes.end()){
            state.turn++;
            continue;
        }
        char direction = agent.bfs_based_agent(state, snake_moving_idx);

        state.move(direction, snake_moving_idx);
        
        state.turn++;
    }
    state.print_game_state();

    
    return 0;
}