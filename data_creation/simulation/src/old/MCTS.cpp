#include "MCTS.h"
#include <vector>
#include <unordered_map>
#include <cmath>
#include <ctime>
#include <random>
#include <algorithm>
#include <chrono>
#include <set>

MCTS::MCTS(SnakeState root_state,
           Node* root,
           double run_time,
           int node_count,
           int num_rollouts)
    : root_state(root_state),
      root(root),
      run_time(run_time),
      node_count(node_count),
      num_rollouts(num_rollouts) {}

MCTS::~MCTS() {
    delete root;
}

pair<Node*, SnakeState> MCTS::select_node() {
    Node* node = root;
    SnakeState state = SnakeState(root_state); // Copy constructor
    
    while (node->children.size() != 0) {
        vector<Node*> children;
        
        for (const auto& pair : node->children) {
            children.push_back(pair.second);
        }
        
        // Find max value out of node's children
        double max_value = -1;
        for (Node* child : children) {
            max_value = max(max_value, child->get_value());
        }
        
        // Get all nodes with max value
        vector<Node*> max_nodes;
        for (Node* child : children) {
            if (child->get_value() == max_value) {
                max_nodes.push_back(child);
            }
        }
        
        // Choose a random node among max_nodes
        random_device rd; // obtain a random number from hardware
        mt19937 gen(rd()); // seed the generator
        uniform_int_distribution<int> distr(0, max_nodes.size() - 1);

        node = max_nodes[distr(gen)];

        state.move(node->move);
        
        if (node->N == 0) {
            return {node, state};
        }
    }
    
    if (expand(node, state)) {
        vector<Node*> children;
        for (const auto& pair : node->children) {
            children.push_back(pair.second);
        }
        
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<int> distr(0, children.size() - 1);

        node = children[distr(gen)];
        state.move(node->move);
    }
    
    return {node, state};
}

bool MCTS::expand(Node* parent, SnakeState& state) {
    if (state.game_over()) {
        return false;
    }
    
    vector<char> legal_moves = state.get_legal_moves();
    vector<Node*> children;
    
    for (char move : legal_moves) {
        children.push_back(new Node(move, parent));
    }
    
    parent->add_children(children);
    return true;
}

int MCTS::roll_out(SnakeState state) {
    // as long as the game is not over, choose random move
    while (!state.game_over()) {
        vector<char> legal_moves = state.get_legal_moves();
        
        // Choose random move
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<int> distr(0, legal_moves.size() - 1);
        
        char move = legal_moves[distr(gen)];
        
        state.move(move);
    }
    // who won?
    return state.turn;
}

// propagate the result of the roll-out back up the tree
// outcome = -1 if there is a draw
void MCTS::back_propagate(Node* node, int turn, int outcome) {
    // For the current player, not the next player
    double reward = (outcome == turn) ? 0 : 1;
    
    while (node != nullptr) {
        node->N++;
        node->Q += reward;
        node = node->parent;
        
        if (outcome == -1) {
            reward = 0;
        } else {
            reward = 1 - reward;
        }
    }
}

void MCTS::search(int time_limit) {
    auto start_time = chrono::high_resolution_clock::now();
    
    int rollouts = 0;
    while (true) {
        auto current_time = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = current_time - start_time;
        
        if (elapsed.count() >= time_limit) {
            break;
        }
        
        auto [node, state] = select_node();
        int outcome = roll_out(state);
        back_propagate(node, state.turn, outcome);
        rollouts++;
    }
    
    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = end_time - start_time;
    
    run_time = elapsed.count();
    num_rollouts = rollouts;
}

char MCTS::best_move() {
    if (root_state.game_over()) {
        return '0';
    }
    
    if (root->children.empty()) {
        return '0';
    }
    
    int max_n = -1;
    vector<Node*> max_nodes;
    
    for (const auto& pair : root->children) {
        Node* child = pair.second;
        if (child->N > max_n) {
            max_n = child->N;
            max_nodes.clear();
            max_nodes.push_back(child);
        } else if (child->N == max_n) {
            max_nodes.push_back(child);
        }
    }
    
    // Choose a random node among max_nodes
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> distr(0, max_nodes.size() - 1);

    Node* best_child = max_nodes[distr(gen)];
    
    return best_child->move;
}