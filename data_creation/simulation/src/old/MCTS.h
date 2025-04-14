#ifndef MCTS_H
#define MCTS_H

#include "SnakeState.h"
#include "NodeMCTS.h"
#include <utility>

class MCTS {
private:
    SnakeState root_state;
    Node* root;
    double run_time;
    int node_count;
    int num_rollouts;

public:
    // Constructor
    MCTS(SnakeState root_state,
         Node* root,
         double run_time,
         int node_count,
         int num_rollouts);

    // Destructor
    ~MCTS();

    // Methods
    std::pair<Node*, SnakeState> select_node();
    bool expand(Node* parent, SnakeState& state);
    int roll_out(SnakeState state);
    void back_propagate(Node* node, int turn, int outcome);
    void search(int time_limit);
    char best_move();
};

#endif // MCTS_H