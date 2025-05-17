#ifndef STATE_H
#define STATE_H

#include <vector>
#include <utility>
#include <fstream>
#include <set>
#include <string.h>
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
    int turn = 0;

    // state memory
    vector<Snake> snakes;
    vector<Apple> apples;
    set<int> eliminated_snakes;
    // apples state after i-th turn (0th element in the vector is the initial position at the beginning)
    vector<vector<Apple> > apples_history;
    int idx_prev_snake;
    string whoose_prev_turn;

    // string log_filename = "game_log.txt";
    // ofstream log_file; 

    vector<pair<int, int>> generate_distinct_pairs(size_t n);
    vector<vector<pair<int, int> > > all_snakes_moves;

    State(int n_snakes, int n_apples, int board_width, int board_height);
    // ~State();

    // void set_log_file(const string& filename);
    bool move(char direction, int snake_moving_idx);
    void get_beginning_snake_heads_positions(vector<pair<int, int>>& snakes);
    void get_apples_positions(vector<Apple>& apples);
    bool is_game_over();
    
    bool is_snake_colliding_snakes(Snake& snake_moving, vector<Snake>& snakes);
    bool is_snake_out_of_bounds(Snake& snake_moving);
    int is_snake_apple_colliding(Snake& snake_moving, vector<Apple>& apples);

    bool try_move(char direction, Snake& tested_snake);
    bool is_snake_colliding_snakes_no_state_change(Snake& tried_snake, Snake& snake_in_state_moving, vector<Snake>& snakes);
    
    // void print_game_state();
    string get_game_state();
    string get_full_history();
};

#endif