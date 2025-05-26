#include "../include/MCTS.h"
#include <algorithm>
#include <iostream>

// MCTSNode (what's stored in the tree)
MCTSNode::MCTSNode() : total_games(0), wins(0), current_snake_idx(0), 
                    action('\0'), node_state(nullptr), parent(nullptr) {}



MCTSNode::~MCTSNode() {
    // delete node_state;
    for (MCTSNode* child : children) {
        delete child;
    }
}

double MCTSNode::ucb(int main_player, double constant) {
    if (total_games == 0) {
        return numeric_limits<double>::max();
    }
    
    if (parent == nullptr) {
        return static_cast<double>(wins) / total_games;
    }
    
    double exploitation;
    if (current_snake_idx == main_player) {
        exploitation = static_cast<double>(wins) / total_games;
    } else {
        exploitation = 1.0 - (static_cast<double>(wins) / total_games);
    }
    
    double exploration = constant * sqrt(log(parent->total_games) / total_games);
    return exploitation + exploration;
}


// MCTS (Tree structure and MCTS algorithm)
MCTS::MCTS() {
    root = new MCTSNode();
    random_device rd;
    gen.seed(rd());
}

MCTS::~MCTS() {
    delete root;
}

void MCTS::set_rollout_policy(function<char(const State&, int)> policy) {
    rollout_policy = policy;
}

void MCTS::initialize_tree(const State& state, int snake_idx) {
    root->parent = nullptr;
    root->current_snake_idx = snake_idx;
    root->node_state = state.deepCopy();
    root->total_games = 0;
    root->wins = 0;
    root->action = '\0';
    root->children.clear();
}

void MCTS::expand_node(MCTSNode* node) {
    if (node->node_state->is_game_over()) {
        return;
    }
    
    vector<char> possible_moves = node->node_state->get_all_possible_moves(node->current_snake_idx);
    
    for (char move : possible_moves) {

        

        // new state after the move
        State new_state(*node->node_state);
        new_state.move(move, node->current_snake_idx);
        
        // next snake index is +1 % number of snakes
        // this ensures that we cycle through the snakes
        int next_snake = (node->current_snake_idx + 1) % new_state.n_snakes;

        // child takes new state, next snake index, move and parent node
        MCTSNode* child = new MCTSNode();
        child->node_state = new_state.deepCopy();
        child->current_snake_idx = next_snake;
        child->action = move;
        child->parent = node;
        child->total_games = 0;
        child->wins = 0;
        
        node->children.push_back(child);
    }
}

int MCTS::rollout(const State& state, int current_snake) {
    cout << "ROLLOUT" << endl;
    // Perform a rollout from the given state using the rollout policy
    // returns the index of the winning snake or -1 if no winner
    if (!rollout_policy) {
        cerr << "Error: No rollout policy set!" << endl;
        return 0;
    }
    
    // copy the state
    State* rollout_state = state.deepCopy();
    State *prev_state = rollout_state->deepCopy();
    
    int snake_turn = current_snake;
    
    while (!rollout_state->is_game_over()
            && rollout_state->turn < 50 \
            && !rollout_state->apples.empty())
    
    {
        char move = rollout_policy(*rollout_state, snake_turn);

        // cout << "Rollout move: " << move << endl;
        // modify the state with the move
        rollout_state->move_without_apples_changed(move, snake_turn);

        // cout << rollout_state->turn << endl;

        // switch to the next snake
        snake_turn = (snake_turn + 1) % rollout_state->n_snakes;
        // cout << "Next snake index: " << snake_turn << endl;
    }

    int winner = rollout_state->get_winner(*prev_state);

    delete rollout_state; // clean up the allocated memory
    delete prev_state; // clean up the allocated memory

    return winner;
}

void MCTS::backpropagate(int rollout_result, MCTSNode* current) {
    cout << "BACKPROPAGATE" << endl;
    while (current != nullptr) {
        current->total_games++;
        
        // update wins only if the winning snake is the one, whose turn is in the current node
        if (rollout_result == current->current_snake_idx) {
            if (rollout_result == -1){
                // current->wins += 0.5; // tie case
            }else {
                current->wins += 1.0; // current snake won
            }
        }
        
        // climb up the tree
        current = current->parent;
    }
}

MCTSNode* MCTS::select_best_child(MCTSNode* node, int main_player) {
    
    // selected best child based on UCB value
    MCTSNode* best_child = nullptr;
    double best_ucb = -1.0;
    int max_played_games = -1;
    
   // choose node, maximalizing ucb
    for (auto child : node->children){
        double ucb_val = child->ucb(main_player, sqrt(2));
        if (ucb_val > best_ucb){
            best_ucb = ucb_val;
            best_child = child;
            max_played_games = child->total_games;
        }
        // in case two have the same ucb, choose the one visited more often
        // one that played more games
        else if (ucb_val == best_ucb && max_played_games < child->total_games){
            best_child = child;
            max_played_games = child->total_games;
        }
    }

    // return most visited and maximalizing ucb child
    return best_child;
}

void MCTS::perform_iteration(int main_player) {
    MCTSNode* current = root;
    
    cout << "SELECTION" << endl;
    // Selection - traverse down the tree using UCB
    while (!current->children.empty()) {
        current = select_best_child(current, main_player);
    }
    
    // Expansion - add children if node has been visited
    if (current->total_games > 0) {
        expand_node(current);
        if (!current->children.empty()) {
            // select the first child to continue the simulation
            current = current->children[0];
        }
    }
    
    // Rollout - simulate game till the end, using the rollout policy
    int result = rollout(*current->node_state, current->current_snake_idx);
    
    // Backpropagation - update statistics up the tree
    // increase nominator only for current snake idx
    // increase denominator for all snakes
    backpropagate(result, current);
}

char MCTS::find_best_move(const State& state, int snake_idx, int iterations) {
    initialize_tree(state, snake_idx);
    expand_node(root);
    
    if (root->children.empty()) {
        return 'U';
    }
    
    for (int i = 0; i < iterations; i++) {
        perform_iteration(snake_idx);
    }
    
    MCTSNode* best_child = select_best_child(root, snake_idx);
    
    return best_child ? best_child->action : 'U';
}