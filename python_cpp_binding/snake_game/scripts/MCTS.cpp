#include "../include/MCTS.h"
#include <algorithm>
#include <iostream>
#include <iostream>
#include <iomanip>
#include <string>

// MCTSNode (what's stored in the tree)
MCTSNode::MCTSNode() : total_games(0), wins(0), current_snake_idx(0), 
                    action('\0'), node_state(nullptr), parent(nullptr) {}



MCTSNode::~MCTSNode() {
    delete node_state;
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
    
    double win_rate = static_cast<double>(wins) / total_games;
    double exploration = constant * sqrt(log(parent->total_games) / total_games);
    return win_rate + exploration;
    // if (parent->current_snake_idx == main_player) {
    //     return win_rate + exploration;
    // } else {
    //     return (1.0 - win_rate) + exploration;
    // }    
    
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

double MCTS::rollout(const State& state, int current_snake, int* passed_turns) {
    // cout << "ROLLOUT" << endl;
    // Perform a rollout from the given state using the rollout policy
    // returns the index of the winning snake or -1 if no winner
    if (!rollout_policy) {
        cerr << "Error: No rollout policy set!" << endl;
        return 0;
    }

    // premiować w stanie szybsze zjedzenie jabłka, gamma factor
    
    // copy the state
    State* rollout_state = state.deepCopy();
    State *prev_state = rollout_state->deepCopy();
    
    int snake_turn = current_snake;
    
    while (!rollout_state->is_game_over()
            && (rollout_state->turn - prev_state->turn) < 10 
            // && !rollout_state->apples.empty()
        )
    
    {
        char move = rollout_policy(*rollout_state, snake_turn);

        // cout << "Rollout move: " << move << endl;
        // modify the state with the move
        rollout_state->move(move, snake_turn);

        // switch to the next snake
        snake_turn = (snake_turn + 1) % rollout_state->n_snakes;
        // cout << "Next snake index: " << snake_turn << endl;
    }

    // returns 0 on S0 winning
    // 1 on S1 winning
    // -1 on tie
    int winner = rollout_state->get_winner(*prev_state);
    *passed_turns = rollout_state->turn - prev_state->turn;


    // *passed_turns = rollout_state->turn - prev_state->turn;

    delete rollout_state;
    delete prev_state; 

    return winner;

   
}


// // In MCTS.cpp

// // Change the return type from int to double
// double MCTS::rollout(const State& state, int main_player, int* passed_turns) {
//     State* rollout_state = state.deepCopy();
//     int snake_turn = main_player;

//     // This will be the score from the main_player's perspective
//     double cumulative_score = 0.0; 

//     // Define your rewards
//     const double EAT_APPLE_REWARD = 10.0;
//     const double DEATH_PENALTY = -100.0;
//     const double SURVIVAL_REWARD = 0.1; // Small reward for each turn survived

//     while (!rollout_state->is_game_over() /* && other conditions */) {
        
//         // Store state before the move
//         State *prev_move_state = rollout_state->deepCopy();
        
//         char move = rollout_policy(*rollout_state, snake_turn);
//         rollout_state->move(move, snake_turn);

//         // --- INCREMENTAL REWARD CALCULATION ---
//         // Check if the current player (snake_turn) just did something good/bad
        
//         double move_score = 0.0;
        
//         // 1. Did it eat an apple? (Check by comparing length)
//         if (rollout_state->snakes[snake_turn].tail.size() > prev_move_state->snakes[snake_turn].tail.size()) {
//             move_score += EAT_APPLE_REWARD;
//         }

//         // 2. Did it die?
//         bool died_this_turn = (prev_move_state->eliminated_snakes.find(snake_turn) == prev_move_state->eliminated_snakes.end()) &&
//                                (rollout_state->eliminated_snakes.find(snake_turn) != rollout_state->eliminated_snakes.end());
//         if (died_this_turn) {
//             move_score += DEATH_PENALTY;
//         } else {
//             // 3. If it didn't die, give a small reward for surviving the turn
//             move_score += SURVIVAL_REWARD;
//         }

//         // --- UPDATE CUMULATIVE SCORE ---
//         // If the current player is the main_player, add the score.
//         // If it's the opponent, subtract the score (minimax logic).
//         if (snake_turn == main_player) {
//             cumulative_score += move_score;
//         } else {
//             cumulative_score -= move_score;
//         }

//         snake_turn = (snake_turn + 1) % rollout_state->n_snakes;

//         delete prev_move_state; // Clean up the previous state to avoid memory leaks
//     }

//     delete rollout_state;
//     // The final score is normalized or returned as is. 
//     // It's often good to scale it to a predictable range, like 0 to 1, if possible.
//     // For now, returning the raw score is fine.
//     return cumulative_score; 
// }



void MCTS::backpropagate(double rollout_winner, int main_player, double score_for_winners, MCTSNode* current) {
    // cout << "BACKPROPAGATE" << endl;
    while (current != nullptr) {
        current->total_games++;
        
        // update wins only if the winning snake is the one, whose turn is in the current node
        if ((int) rollout_winner == main_player) {
            // increase by a given score, assosiated with how quicly the win was achived
            current->wins += 1.0; // current snake won
        }

        // if (rollout_winner == -1) {
        //     // tie, no wins for anyone
        //     // current->wins += 0.5; // tie, both snakes get half a win
        // }

        // current->wins += rollout_score;
       
        
        // climb up the tree
        current = current->parent;
    }
}

MCTSNode* MCTS::select_best_child(MCTSNode* node, int main_player) {
    
    // selected best child based on UCB value
    MCTSNode* best_child = nullptr;
    double best_ucb = -1.0;
    int max_played_games = -1;

    // // if there wasn't enough games played, choose randomly
    // if (node->total_games < 10){
    //     // randomly choose one of the children
    //     if (node->children.empty()) {
    //         return nullptr; // no children to select from
    //     }
    //     uniform_int_distribution<int> dist(0, node->children.size() - 1);
    //     int random_index = dist(gen);
    //     return node->children[random_index];
    // }
    
   // choose node, maximalizing ucb
    for (auto child : node->children){
        // można robić tak, że będziemy aplikować UCB dopiero jak wierzchołek był odwiedzony T razy
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
    
    // cout << "SELECTION" << endl;
    // Selection - traverse down the tree using UCB
    while (!current->children.empty()) {
        current = select_best_child(current, main_player);
    }
    
    // Expansion - add children if node has been visited
    if (current->total_games > 0) {
        expand_node(current);
        // select a random child to continue the simulation
        if (!current->children.empty()) {
            // std::uniform_int_distribution<int> dist(0, current->children.size() - 1);
            current = current->children[0];
        }
    }
    
    // Rollout - simulate game till the end, using the rollout policy
    int passed_turns;
    // double rollout_score = rollout(*current->node_state, current->current_snake_idx, &passed_turns);
    int rollout_winner = rollout(*current->node_state, current->current_snake_idx, &passed_turns);

    // Backpropagation - update statistics up the tree
    // increase nominator only for current snake idx
    // increase denominator for all snakes

    // give higher score for the snake that won faster, made more greedy moves toward winning
    double score_for_winners = 1.0 * exp(-(passed_turns));


    backpropagate(rollout_winner, main_player, score_for_winners, current);
}

char MCTS::find_best_move(const State& state, int main_snake, int iterations) {
    initialize_tree(state, main_snake);
    expand_node(root);
    
    if (root->children.empty()) {
        return 'U';
    }
    
    for (int i = 0; i < iterations; i++) {
        perform_iteration(main_snake);
    }
    

    print_tree(2);

    MCTSNode* best_move_node = nullptr;
    double max_win_rate = -1.0;
    
    for (MCTSNode* child : root->children) {
        if (child->total_games > 0) {
            double win_rate = (static_cast<double>(child->wins) / child->total_games);
            if (win_rate > max_win_rate) {
                max_win_rate = win_rate;
                best_move_node = child;
            }
        }
    }

    if (!best_move_node) {
        cout << "No valid moves found after MCTS iterations." << endl;
        // return 'U'; // Up as a default move
    }
    
    return best_move_node ? best_move_node->action : 'R';
}



void MCTS::print_tree(int max_depth) const {
    if (!root) {
        std::cout << "Tree is empty (root is null)" << std::endl;
        return;
    }
    
    std::cout << "=== MCTS Tree Structure ===" << std::endl;
    std::cout << "Root (Snake " << root->current_snake_idx << ")" << std::endl;
    std::cout << "Games: " << root->total_games << ", Wins: " << std::fixed << std::setprecision(2) 
              << root->wins << ", Win Rate: ";
    
    if (root->total_games > 0) {
        std::cout << (root->wins / root->total_games * 100) << "%";
    } else {
        std::cout << "N/A";
    }
    std::cout << std::endl;
    
    if (root->children.empty()) {
        std::cout << "└── No children (leaf node)" << std::endl;
    } else {
        for (size_t i = 0; i < root->children.size(); ++i) {
            bool is_last = (i == root->children.size() - 1);
            print_node(root->children[i], 1, "", is_last, max_depth);
        }
    }
    std::cout << "=========================" << std::endl;
}

void MCTS::print_node(MCTSNode* node, int depth, const std::string& prefix, bool is_last, int max_depth) const {
    if (!node || depth > max_depth) {
        return;
    }
    
    // Print current node
    std::cout << prefix;
    std::cout << (is_last ? "└── " : "├── ");
    
    // Action and snake info
    std::cout << "Action: " << (node->action ? node->action : '?') 
              << " (Snake " << node->current_snake_idx << ") ";
    
    // Statistics
    std::cout << "[Games: " << node->total_games << ", Wins: " << std::fixed << std::setprecision(2) 
              << node->wins;
    
    if (node->total_games > 0) {
        double win_rate = node->wins / node->total_games;
        std::cout << ", WR: " << (win_rate * 100) << "%";
        
        // Show UCB value if it has a parent
        if (node->parent) {
            double ucb_val = node->ucb(0, sqrt(2.0)); // Using player 0 as default
            if (ucb_val == std::numeric_limits<double>::max()) {
                std::cout << ", UCB: ∞";
            } else {
                std::cout << ", UCB: " << std::setprecision(3) << ucb_val;
            }
        }
    } else {
        std::cout << ", WR: N/A, UCB: ∞";
    }
    std::cout << "]";
    
    // Game state info (optional - might be too verbose)
    if (node->node_state) {
        std::cout << " Turn: " << node->node_state->turn;
        if (node->node_state->is_game_over()) {
            std::cout << " [GAME OVER]";
        }
    }
    
    std::cout << std::endl;
    
    // Print children
    if (!node->children.empty() && depth < max_depth) {
        std::string new_prefix = prefix + (is_last ? "    " : "│   ");
        
        for (size_t i = 0; i < node->children.size(); ++i) {
            bool child_is_last = (i == node->children.size() - 1);
            print_node(node->children[i], depth + 1, new_prefix, child_is_last, max_depth);
        }
    } else if (!node->children.empty() && depth >= max_depth) {
        std::cout << prefix << (is_last ? "    " : "│   ") << "... (" << node->children.size() << " children - max depth reached)" << std::endl;
    }
}

// Alternative compact version that shows only the most promising paths
void MCTS::print_best_path(int max_depth) const {
    if (!root) {
        std::cout << "Tree is empty" << std::endl;
        return;
    }
    
    std::cout << "=== Best Path (Highest Win Rate) ===" << std::endl;
    MCTSNode* current = root;
    int depth = 0;
    
    while (current && depth < max_depth) {
        // Print current node info
        std::string indent(depth * 2, ' ');
        std::cout << indent;
        
        if (depth == 0) {
            std::cout << "ROOT";
        } else {
            std::cout << "→ " << current->action;
        }
        
        std::cout << " (Snake " << current->current_snake_idx << ") ";
        std::cout << "[" << current->total_games << " games, ";
        
        if (current->total_games > 0) {
            double win_rate = current->wins / current->total_games;
            std::cout << std::fixed << std::setprecision(1) << (win_rate * 100) << "% WR]";
        } else {
            std::cout << "0% WR]";
        }
        std::cout << std::endl;
        
        // Find best child (highest win rate)
        MCTSNode* best_child = nullptr;
        double best_win_rate = -1.0;
        
        for (MCTSNode* child : current->children) {
            if (child->total_games > 0) {
                double win_rate = child->wins / child->total_games;
                if (win_rate > best_win_rate) {
                    best_win_rate = win_rate;
                    best_child = child;
                }
            }
        }
        
        current = best_child;
        depth++;
    }
    std::cout << "=================================" << std::endl;
}

// Utility function to print tree statistics
void MCTS::print_tree_stats() const {
    if (!root) {
        std::cout << "Tree is empty" << std::endl;
        return;
    }
    
    // Count nodes at each level
    std::vector<int> level_counts;
    std::vector<MCTSNode*> current_level = {root};
    
    while (!current_level.empty()) {
        level_counts.push_back(current_level.size());
        std::vector<MCTSNode*> next_level;
        
        for (MCTSNode* node : current_level) {
            for (MCTSNode* child : node->children) {
                next_level.push_back(child);
            }
        }
        current_level = next_level;
    }
    
    std::cout << "=== Tree Statistics ===" << std::endl;
    std::cout << "Tree depth: " << (level_counts.size() - 1) << std::endl;
    std::cout << "Total root games: " << root->total_games << std::endl;
    
    for (size_t i = 0; i < level_counts.size(); ++i) {
        std::cout << "Level " << i << ": " << level_counts[i] << " nodes" << std::endl;
    }
    
    // Print action distribution for root's children
    if (!root->children.empty()) {
        std::cout << "\nRoot children action distribution:" << std::endl;
        for (MCTSNode* child : root->children) {
            std::cout << "  " << child->action << ": " << child->total_games << " games";
            if (child->total_games > 0) {
                double win_rate = child->wins / child->total_games;
                std::cout << " (" << std::fixed << std::setprecision(1) << (win_rate * 100) << "% WR)";
            }
            std::cout << std::endl;
        }
    }
    std::cout << "======================" << std::endl;
}