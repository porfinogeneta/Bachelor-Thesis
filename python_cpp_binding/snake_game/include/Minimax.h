#ifndef MINIMAX_H
#define MINIMAX_H


#include <vector>
#include <utility>
#include "../include/State.h"

using namespace std;




class Minimax {
public:
   
    double minimax(const State& initial_state, State& state, int depth, bool isMaximizingPlayer);

    char find_best_move(const State& state, int current_snake_idx, int depth);
};



#endif