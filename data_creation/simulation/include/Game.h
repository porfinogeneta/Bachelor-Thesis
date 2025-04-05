#ifndef GAME_H
#define GAME_H

#include <vector>
#include <utility>
#include <fstream>
#include "Snake.h"
#include "Agent.h"

using namespace std;

class Game {
protected:
    int n_snakes = 2;
    int n_apples = 5;
    int board_width = 10;
    int board_height = 10;
    string log_filename = "game_log.txt";
    ofstream log_file; 
    
    vector<std::pair<int, int>> generateDistinctPairs(size_t n);
    vector<vector<pair<int, int> > > all_snakes_moves;

public:

    Game();
    ~Game();

    void set_log_file(const std::string& filename);

    void get_beginning_snake_positions(std::vector<std::pair<int, int>>& snakes);
    void get_apples_positions(std::vector<std::pair<int, int>>& apples, std::vector<std::pair<int, int>>& occupied_positions);
    
    bool is_snake_colliding_snakes(Snake& snake_moving, std::vector<Snake>& snakes);
    bool is_snake_out_of_bounds(Snake& snake_moving);
    bool is_snake_apple_colliding(Snake& snake_moving, std::vector<std::pair<int, int>>& apples);
    
    void print_snake_game_state(std::vector<Snake>& snakes, std::vector<std::pair<int, int>>& apples, int turn, vector<vector<pair<int, int> > > all_snakes_moves);
    void run_game();
};

#endif