#include "../include/Minimax.h"


// let snake 0 be minimazing snake and snake 1 be maximizing snake
// isMaximizingPlayer = true <=> snake_idx = 1
// isMaximizingPlayer = false <=> snake_idx = 0

// accepts root state, state after the move, depth, and whether the player is maximizing or minimizing
double Minimax::minimax(const State& initial_state, State& state, int depth, bool isMaximizingPlayer, double alpha, double beta) {

    // miximized player is the snake that is about to move in the initial state
    int maximized_player = (initial_state.turn % initial_state.n_snakes);
    int minimized_player = ((initial_state.turn + 1) % initial_state.n_snakes);


    if (depth == 0 || state.is_game_over() || !state.is_snake_alive(maximized_player) || !state.is_snake_alive(minimized_player)) {
        // scoring heuristic scores the end state from the perspective of the snake that is about to move in the initial state
        // cout << "Reached depth 0 or game over, returning score" << endl;
        return state.score_state(initial_state);
    }

    // cout << "Current turn " << (initial_state.turn % initial_state.n_snakes) << endl;

    if (isMaximizingPlayer){

        double maxEval = -10000;


        // vector<char> possible_moves = state.get_all_possible_moves(maximized_player);

        vector<char> possible_moves = {'R', 'L', 'U', 'D'};

        for (auto dir : possible_moves){

            State state_cpy = *state.deepCopy();

            state_cpy.move(dir, maximized_player);

            double eval = minimax(initial_state, state_cpy, depth - 1, false, alpha, beta);

            maxEval = max(maxEval, eval);

            alpha = max(alpha, eval);
            if (beta <= alpha) {
                break; // Beta cut-off
            }
        }

        return maxEval;
    } 
    // minimazing player
    else {
        double minEval = 10000;

        // vector<char> possible_moves = state.get_all_possible_moves(minimized_player);

        vector<char> possible_moves = {'R', 'L', 'U', 'D'};

        for (auto dir : possible_moves){

            State state_cpy = *state.deepCopy();

            state_cpy.move(dir, minimized_player);

            // eval should be negative for minimaxing player, and the scoring function returns positive values
            double eval = minimax(initial_state, state_cpy, depth - 1, true, alpha, beta);

            minEval = min(minEval, eval);

            beta = min(beta, eval);
        }

        return minEval;
    }
}



char Minimax::find_best_move(const State& state, int current_snake_idx, int depth){

    State state_cpy = *state.deepCopy();
    vector<char> possible_moves = state_cpy.get_all_possible_moves(current_snake_idx);

    // root is always a maximizing player

    double wanted_score = -10000;

     // pair of maximizing value and the best direction
    pair<double, char> eval_dir = make_pair(wanted_score, 'U');


     for (auto dir : possible_moves){

        State state_cpy = *state.deepCopy();

        state_cpy.move(dir, current_snake_idx);

        double eval = minimax(state, state_cpy, depth - 1, false, -10000, 10000);

        if (eval_dir.first < eval){
            eval_dir.first = eval;
            eval_dir.second = dir;
        }
    }

    // cout << "Best move for snake " << current_snake_idx << ": " << eval_dir.second << " with score: " << eval_dir.first << endl;

    return eval_dir.second;


    // bool isMaximizingPlayer = (current_snake_idx == 1);


    // double wanted_score = isMaximizingPlayer ? -10000 : 10000;

    // // pair of maximizing/minimazing value and the best direction
    // pair<double, char> eval_dir = make_pair(wanted_score, 'U');

    // // // print possible moves
    // // cout << "Possible moves for snake " << current_snake_idx << ": ";
    // // for (char move : possible_moves) {
    // //     cout << move << " ";
    // // }
    // // cout << endl;

    // for (auto dir : possible_moves){

    //     State state_cpy = *state.deepCopy();

       

    //     state_cpy.move(dir, current_snake_idx);

    //     double eval = minimax(state, state_cpy, depth - 1, !isMaximizingPlayer);

    //     if (isMaximizingPlayer && eval_dir.first < eval){
    //         eval_dir.first = eval;
    //         eval_dir.second = dir;
    //     }else if (!isMaximizingPlayer && eval_dir.first > eval){
    //         eval_dir.first = eval;
    //         eval_dir.second = dir;
    //     }
    // }

    // cout << "Best move for snake " << current_snake_idx << ": " << eval_dir.second << " with score: " << eval_dir.first << endl;

    // return eval_dir.second;

}
