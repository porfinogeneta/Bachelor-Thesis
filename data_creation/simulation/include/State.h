#ifndef STATE_H
#define STATE_H

#include <vector>
#include <utility>
#include <fstream>
#include <set>
#include "Snake.h"
#include "Apple.h"

using namespace std;

class State {
public:

    // passed game parameters
    int n_snakes;
    int n_apples;
    int board_width;
    int board_height;
    

    // state memory
    vector<Snake> snakes;
    vector<Apple> apples;
    set<int> eliminated_snakes;


    string log_filename = "game_log.txt";
    ofstream log_file; 

    vector<pair<int, int>> generate_distinct_pairs(size_t n);
    vector<vector<pair<int, int> > > all_snakes_moves;

    State(int n_snakes, int n_apples, int board_width, int board_height, string log_filename = "game_log.txt");
    ~State();

    void set_log_file(const string& filename);
    bool move(char direction, int snake_moving_idx);
    void get_beginning_snake_heads_positions(vector<pair<int, int>>& snakes);
    void get_apples_positions(vector<Apple>& apples);
    bool is_game_over();
    
    bool is_snake_colliding_snakes(Snake& snake_moving, vector<Snake>& snakes);
    bool is_snake_out_of_bounds(Snake& snake_moving);
    bool is_snake_apple_colliding(Snake& snake_moving, vector<Apple>& apples);
    
    void print_game_state(int turn);
    void run_game();
};

#endif