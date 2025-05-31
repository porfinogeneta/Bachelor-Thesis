#ifndef MCTS_H
#define MCTS_H

#include <vector>
#include <memory>
#include <random>
#include <functional>
#include <limits>
#include <cmath>
#include "../include/State.h"

using namespace std;


class MCTSNode {
public:
    double total_games;
    // wins for the current player
    double wins;
    int current_snake_idx;
    char action; // action, that got us to this state
    
    State* node_state;
    MCTSNode* parent;
    vector<MCTSNode*> children;
    
    MCTSNode();
    ~MCTSNode();
    
    double ucb(int main_player, double constant = sqrt(2.0));
};

class MCTS {
private:
    MCTSNode* root = nullptr;
    mt19937 gen;
    function<char(const State&, int)> rollout_policy;
    
    void expand_node(MCTSNode* node);
    int rollout(const State& state, int current_snake, int* passed_turns);
    void backpropagate(int rollout_winner, double score_for_winners, MCTSNode* current);
    MCTSNode* select_best_child(MCTSNode* node, int main_player);
    
public:
    MCTS();
    ~MCTS();
    
    void set_rollout_policy(function<char(const State&, int)> policy);
    void initialize_tree(const State& state, int snake_idx);
    void perform_iteration(int main_player);
    char find_best_move(const State& state, int snake_idx, int iterations = 1000);
};

#endif