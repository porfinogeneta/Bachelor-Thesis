#include "State.h"
#include <iostream>
#include <string>
#include <random>
#include <set>






State::State(int n_snakes, int n_apples, int board_width, int board_height) {

    // set game parameters
    this->n_snakes = n_snakes;
    this->n_apples = n_apples;
    this->board_width = board_width;
    this->board_height = board_height;
    // this->coutname = coutname;
    
    // set_cout(coutname);

    snakes.clear();

    // create heads
    vector<pair<int, int> > snake_heads;
    get_beginning_snake_heads_positions(snake_heads);

    // initialize snakes
    for (size_t i = 0; i < snake_heads.size(); i++) {
        Snake new_snake = Snake(snake_heads[i].first, snake_heads[i].second);
        // save snake's initial position
        new_snake.moves_history.push_back(snake_heads[i]);
        // save snake's initial tail length
        new_snake.tails_len_history.push_back(new_snake.tail.size());
        new_snake.tails_last_segments_history.push_back(new_snake.get_last_snake_segment());
        snakes.push_back(new_snake);
    }

    // create apples positions
    apples.clear();
    get_apples_positions(apples);
    // apples history begins with apples state in the first turn
    apples_history.push_back(apples);
}


// State::~State(){
//     if (cout.is_open()){
//         cout.close();
//     }
// }


// void State::set_cout(const string& filename) {
//     if (cout.is_open()) {
//         cout.close();
//     }
//     coutname = filename;
//     cout.open(coutname);
// }


State* State::deepCopy() const {
    
    State* copiedState = new State(n_snakes, n_apples, board_width, board_height);
    
    // Clear the default initialization
    copiedState->snakes.clear();
    copiedState->apples.clear();
    copiedState->apples_history.clear();
    copiedState->eliminated_snakes.clear();
    
    // Copy the turn counter
    copiedState->turn = this->turn;
    copiedState->idx_prev_snake = this->idx_prev_snake;
    
    // Deep copy all snakes
    for (const Snake& snake : this->snakes) {
        Snake copiedSnake(snake.head.first, snake.head.second);
        
        // Copy the tail
        copiedSnake.tail = snake.tail;
        
        // Copy the history
        copiedSnake.moves_history = snake.moves_history;
        copiedSnake.tails_len_history = snake.tails_len_history;
        copiedSnake.tails_last_segments_history = snake.tails_last_segments_history;
        
        copiedState->snakes.push_back(copiedSnake);
    }
    
    // Deep copy apples
    for (const Apple& apple : this->apples) {
        copiedState->apples.push_back(Apple(apple.position.first, apple.position.second));
    }
    
    // Deep copy apple history
    for (const auto& appleVec : this->apples_history) {
        vector<Apple> copiedAppleVec;
        for (const Apple& apple : appleVec) {
            copiedAppleVec.push_back(Apple(apple.position.first, apple.position.second));
        }
        copiedState->apples_history.push_back(copiedAppleVec);
    }
    
    // Copy eliminated snakes set
    copiedState->eliminated_snakes = this->eliminated_snakes;
    
    return copiedState;
}


// generates distinct pairs in range [0, n] (beginning snakes and apples positions)
vector<pair<int, int> > State::generate_distinct_pairs(size_t n) {
    
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> distr(0, 9);
    
    set<pair<int, int> > uniquePairs;
    while (uniquePairs.size() < n) {
        int x = distr(gen);
        int y = distr(gen);
        uniquePairs.insert(make_pair(x, y));
    }
    
    vector<pair<int, int> > result;
    for (const auto& p : uniquePairs) {
        result.push_back(p);
    }
    
    return result;
}


void State::get_beginning_snake_heads_positions(vector<pair<int, int> >& snake_heads) {
    vector<pair<int, int> > position_pairs = generate_distinct_pairs(n_snakes);
    
    for (size_t i = 0; i < position_pairs.size(); i++) {
        snake_heads.push_back(position_pairs[i]);
    }
}

void State::get_apples_positions(vector<Apple>& apples){
    
    int apples_to_generate = n_apples - apples.size();
    
    if (apples_to_generate <= 0) {
        return;
    }


    // apple cannot be generated on the positions occupied by snakes
    vector<pair<int, int> > occupied_positions;
    set<pair<int, int> > occupied_set;


    for (const Snake& snake : snakes) {
        occupied_set.insert(snake.head);
        // occupied_positions.push_back(snake.head);
        for (const auto& segment : snake.tail) {
            // occupied_positions.push_back(segment);
            occupied_set.insert(segment);
        }
    }
    
    // set<pair<int, int> > occupied_set(occupied_positions.begin(), occupied_positions.end());
    
    // add rest of the apples positions to occupied positions
    for (const auto& apple : apples) {
        occupied_set.insert(apple.position);
    }
    
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> dist(0, board_width - 1);
    
    // add new apples as long as it needs to be added and there is place for them
    while (apples_to_generate > 0 and (size_t)apples_to_generate < (board_width * board_height - occupied_set.size())) {
        pair<int, int> new_position = make_pair(dist(gen), dist(gen));
        
        // check if this position is already occupied
        if (occupied_set.find(new_position) == occupied_set.end()) {
            // if not occupied, add it as a new apple
            apples.push_back(Apple(new_position.first, new_position.second));
            occupied_set.insert(new_position);
            apples_to_generate--;
        }
    }
}



bool State::is_snake_colliding_snakes(Snake& snake_moving, vector<Snake>& snakes){
    pair<int, int> moving_head = snake_moving.head;

    // head collision with the snake itself
    for (const auto& tail_segment : snake_moving.tail) {
        if (moving_head == tail_segment) {
            return true;
        }
    }

    for (const Snake& other_snake: snakes){
        
        if (&snake_moving == &other_snake) {
            continue;
        }

        // head collision with another snake's head
        if (moving_head == other_snake.head) {
            return true;
        }

        // collision with tail segment from the other snake
        for (const auto& tail_segment : other_snake.tail) {
            if (moving_head == tail_segment) {
                return true;
            }
        }
        
        
    }

    return false;
}


bool State::is_snake_colliding_snakes_no_state_change(Snake& tried_snake, Snake& snake_in_state_moving, vector<Snake>& snakes){
    // function checks for collisions with the snake that don't modify the state

    pair<int, int> moving_head = tried_snake.head;

    // head collision with the snake itself
    for (const auto& tail_segment : tried_snake.tail) {
        if (moving_head == tail_segment) {
            return true;
        }
    }

    // don't allow for collision with the snake itself, when it's length is 2
    // we need to consider stepping on the first tail segment in unmoved original snake
    if (!snake_in_state_moving.tail.empty() && moving_head == snake_in_state_moving.tail[0]){
        return true;
    }

    for (const Snake& other_snake: snakes){
        
        if (&snake_in_state_moving == &other_snake) {
            continue;
        }

        // head collision with another snake's head
        if (moving_head == other_snake.head) {
            return true;
        }

        // collision with tail segment from the other snake
        for (const auto& tail_segment : other_snake.tail) {
            if (moving_head == tail_segment) {
                return true;
            }
        }
        
        
    }

    return false;
}


bool State::is_snake_out_of_bounds(Snake& snake_moving){
    pair<int, int> moving_head = snake_moving.head;

    return moving_head.first < 0 || moving_head.first > board_width - 1 || moving_head.second < 0 || moving_head.second > board_height - 1;
}

// returns bool, but also gets rid of eaten apple
// return -1 if not colliding
int State::is_snake_apple_colliding(Snake& snake_moving, vector<Apple>& apples){
    pair<int, int> moving_head = snake_moving.head;
    for (size_t i = 0; i < apples.size(); i++){
        if (moving_head == apples[i].position){
            return i;
        }
    }
    return -1;
}


// returns True on valid move
bool State::try_move(char direction, Snake& tested_snake){
    Snake cpy = tested_snake;

    cpy.move_snake(direction);
    return !is_snake_colliding_snakes_no_state_change(cpy, tested_snake, snakes) && !is_snake_out_of_bounds(cpy);
}


vector<char> State::get_all_possible_moves(int snake_idx) {
    // returns all possible moves for the snake with index snake_idx
    vector<char> possible_moves;
    
    // check if snake is eliminated
    if (eliminated_snakes.find(snake_idx) != eliminated_snakes.end()) {
        return possible_moves; // no moves for eliminated snake
    }

    Snake& current_snake = snakes[snake_idx];

    // check all four directions
    for (char direction : {'U', 'D', 'L', 'R'}) {
        if (try_move(direction, current_snake)) {
            possible_moves.push_back(direction);
        }
    }

    return possible_moves;
}


// returns true if snake moved successfully
// returns false if snake collided with another snake or with the wall
bool State::move(char direction, int snake_moving_idx){

    idx_prev_snake = snake_moving_idx;
    // check if snake is already eliminated, treat eliminated snake as a wall
    if (eliminated_snakes.find(snake_moving_idx) != eliminated_snakes.end()){
        // skipped turn don't add any move
        turn++;
        return false;
    }
    
    // Snake current_snake = snakes[snake_moving_idx];
    // current_snake.move_snake(direction);
    
    
    
    // segment that might be added if collided with an apple
    pair<int, int> new_snake_segment = snakes[snake_moving_idx].get_last_snake_segment();


    

    snakes[snake_moving_idx].move_snake(direction);

    // add new position to the snake moves history
    snakes[snake_moving_idx].moves_history.push_back(snakes[snake_moving_idx].head);
    

    if (is_snake_colliding_snakes(snakes[snake_moving_idx], snakes) || 
        is_snake_out_of_bounds(snakes[snake_moving_idx]) || 
        // should not allow to move to the previous segment if snake has only one segment
        (snakes[snake_moving_idx].head == new_snake_segment && snakes[snake_moving_idx].tail.size() == 1)) {

        // add tail and last segment position to history 
        snakes[snake_moving_idx].tails_len_history.push_back(snakes[snake_moving_idx].tail.size());
        snakes[snake_moving_idx].tails_last_segments_history.push_back(snakes[snake_moving_idx].get_last_snake_segment());
        
        eliminated_snakes.insert(snake_moving_idx);
        // after the move, update apples history
        apples_history.push_back(apples);
        turn++;
        
        // in the case of two segment snake i don't allow to move to the previous segment
        if (snakes[snake_moving_idx].head == new_snake_segment && snakes[snake_moving_idx].tail.size() == 1) {
            snakes[snake_moving_idx].head = snakes[snake_moving_idx].tail[0];
        }
        return false;
    }

    int apple_eaten_idx = is_snake_apple_colliding(snakes[snake_moving_idx], apples);
    if (apple_eaten_idx != -1){
        // cout << "eating" << endl;
        // add new segment to the snake
        snakes[snake_moving_idx].tail.push_back(new_snake_segment);
        
        // delete apple after colliding
        apples.erase(apples.begin() + apple_eaten_idx);
        // function generates new apple position that's not on the snake or on one of the apples
        get_apples_positions(apples);
    }

    // after the move update apples history
    apples_history.push_back(apples);

    // after the move add tail length to history - we are interested in lengths after the move 
    snakes[snake_moving_idx].tails_len_history.push_back(snakes[snake_moving_idx].tail.size());
    snakes[snake_moving_idx].tails_last_segments_history.push_back(snakes[snake_moving_idx].get_last_snake_segment());

    turn++;

    return true;

}

bool State::move_without_apples_changed(char direction, int snake_moving_idx) {
    // this function is used to move the snake without changing apples positions
    // it is used in MCTS to simulate moves without changing apples positions

    // check if snake is already eliminated, treat eliminated snake as a wall
    if (eliminated_snakes.find(snake_moving_idx) != eliminated_snakes.end()) {
        // skipped turn don't add any move
        turn++;
        return false;
    }

    snakes[snake_moving_idx].move_snake(direction);

    if (is_snake_colliding_snakes(snakes[snake_moving_idx], snakes) || 
        is_snake_out_of_bounds(snakes[snake_moving_idx])) {

        eliminated_snakes.insert(snake_moving_idx);
        turn++;
        return false;
    }

    // add new position to the snake moves history
    snakes[snake_moving_idx].moves_history.push_back(snakes[snake_moving_idx].head);
    
    // after the move add tail length to history 
    snakes[snake_moving_idx].tails_len_history.push_back(snakes[snake_moving_idx].tail.size());
    snakes[snake_moving_idx].tails_last_segments_history.push_back(snakes[snake_moving_idx].get_last_snake_segment());

    turn++;

    return true;
}

// all snakes eliminated => game over
bool State::is_game_over() {
    
    // all snakes eliminated, no point of game continuation
    // game is played for over 1000 rounds, just finish it
    if (eliminated_snakes.size() == n_snakes || turn >= MAX_GAME_LENGTH) {
        return true; // all snakes are eliminated
    }


    vector<int> living_snakes;
    for (size_t i = 0; i < snakes.size(); i++) {
        if (eliminated_snakes.find(i) == eliminated_snakes.end()) {
            living_snakes.push_back(i);
        }
    }

    // only one living snake has left
    if (living_snakes.size() == 1) {
        // if the snake is longer than all eliminated snakes
        for (int e : eliminated_snakes) {
            if (snakes[living_snakes[0]].tail.size() <= snakes[e].tail.size()) {
                // game is not over, this snake is not the winner
                // it's still not longer than all of eliminated snakes
                return false; 
            }
        }

        return true; // only one snake left, game is over
    }

    return false;
}

const int GROWTH_PER_SEGMENT = 200;
const int DEATH_PENALTY = -200;
const int CLOSE_TO_APPLE = 10;
const int KILL_OPPONENT_BONUS = 1000;
int State::evaluate_winner(const State& prev_state) {

    // returns the index of winning snake or -1 if no winner yet
    // winner is calculated based on scores
    
    if (is_game_over()){
        if (snakes[0].tail.size() > snakes[1].tail.size()) {
            // snake 0 is the winner
            return 0;
        }else if (snakes[1].tail.size() > snakes[0].tail.size()) {
            // snake 1 is the winner
            return 1;

        }else {
            // no winner yet, both snakes have the same length
            return -1;
        }
    }
    

    int snake_0_score = 0;
    int snake_1_score = 0;


    // find out which snake died in this state
    bool is_snake_0_dead_now = prev_state.eliminated_snakes.find(0) == prev_state.eliminated_snakes.end() && 
        eliminated_snakes.find(0) != eliminated_snakes.end();
    
    bool is_snake_1_dead_now = prev_state.eliminated_snakes.find(1) == prev_state.eliminated_snakes.end() && 
        eliminated_snakes.find(1) != eliminated_snakes.end();


    bool is_snake_0_dead_before = prev_state.eliminated_snakes.find(0) != prev_state.eliminated_snakes.end();
    bool is_snake_1_dead_before = prev_state.eliminated_snakes.find(1) != prev_state.eliminated_snakes.end();
   

    // if snake grows in the current rollout increase it's points
    // by the amount of segments it grew
    // if snake 0 grew
    if (prev_state.snakes[0].tail.size() < snakes[0].tail.size()) {
        snake_0_score += GROWTH_PER_SEGMENT * (snakes[0].tail.size() - prev_state.snakes[0].tail.size());
        if (is_snake_1_dead_before){
            snake_0_score += 2*GROWTH_PER_SEGMENT * (snakes[0].tail.size() - prev_state.snakes[0].tail.size());
        }
    }
    if (prev_state.snakes[1].tail.size() < snakes[1].tail.size()) {
        snake_1_score += GROWTH_PER_SEGMENT * (snakes[1].tail.size() - prev_state.snakes[1].tail.size());
        if (is_snake_0_dead_before){
            snake_1_score += 2*GROWTH_PER_SEGMENT * (snakes[1].tail.size() - prev_state.snakes[1].tail.size());
        }
    }



    
    if (is_snake_0_dead_now){
        // discourage death of snake, substract points
        // if (!is_snake_1_dead_before)
        snake_0_score += DEATH_PENALTY;
        // if (is_snake_1_dead_before){
        //     snake_0_score += DEATH_PENALTY;
        // }
        // if snake_1 is still alive give it points for killing
        if (eliminated_snakes.find(1) == eliminated_snakes.end()){
            snake_1_score += KILL_OPPONENT_BONUS;
        }
    }else if (is_snake_1_dead_now) {
        // if (!is_snake_0_dead_before)
        snake_1_score += DEATH_PENALTY;
        // if (is_snake_0_dead_before){
        //     snake_1_score += DEATH_PENALTY;
        // }
        // if snake_0 is still alive give it points for killing
        if (eliminated_snakes.find(0) == eliminated_snakes.end()){
            snake_0_score += KILL_OPPONENT_BONUS;
        }
    }

    if (snake_0_score > snake_1_score) {
        // snake 0 is the winner
        return 0;
    } else if (snake_1_score > snake_0_score) {
        // snake 1 is the winner
        return 1;
    } else {
        // no winner yet
        return -1;
    }
    

}


string State::get_full_history() {
    string result;


    result += "==================================================\n";
    
    // turns amount
    result += "Turns " + to_string(turn) + "\n";
    
    // snake positions information
    for (size_t i = 0; i < snakes.size(); i++) {
        const Snake& snake = snakes[i];
        result += "Length: " + to_string(snake.tail.size() + 1) + "\n";
        
        // print movement history
        result += "Snake " + to_string(i) + "\n";
        for (const auto& position : snake.moves_history) {
            result += "(" + to_string(position.first) + "," + to_string(position.second) + ") ";
        }
        result += "\n";
        
        // print tail sizes history
        result += "Tail Snake" + to_string(i) + "\n";
        for (const auto& size : snake.tails_len_history) {
            result += to_string(size) + " ";
        }
        result += "\n";

        result += "Last segment Snake" + to_string(i) + "\n";
        for (const auto& segment : snake.tails_last_segments_history) {
            result += "(" + to_string(segment.first) + "," + to_string(segment.second) + ") ";
        }
        result += "\n";


    }
    
    result += "Apples\n";
    int apple_vec_index = 0;
    for (const auto& apple_vec : apples_history) {
        for (const auto& apple : apple_vec) {
            result += "(" + to_string(apple.position.first) + "," + to_string(apple.position.second) + ") ";
        }
        result += to_string(apple_vec_index) + "\n";
        apple_vec_index++;
    }
    
    return result;
}


string State::get_game_state() {
    string result;
    
    // empty board representation
    vector<vector<char>> board(board_height, vector<char>(board_width, '.'));
    
    // place apples
    for (const auto& apple : apples) {
        if (apple.position.first >= 0 && apple.position.first < board_height &&
            apple.position.second >= 0 && apple.position.second < board_width) {
            board[apple.position.first][apple.position.second] = 'A';
        }
    }
    
    // place snakes
    for (size_t i = 0; i < snakes.size(); i++) {
        const Snake& snake = snakes[i];
        // place tail segments
        for (const auto& segment : snake.tail) {
            if (segment.first >= 0 && segment.first < board_height &&
                segment.second >= 0 && segment.second < board_width) {
                board[segment.first][segment.second] = '0' + i;
            }
        }
        // Place snake head (using different character for head)
        if (snake.head.first >= 0 && snake.head.first < board_height &&
            snake.head.second >= 0 && snake.head.second < board_width) {
            board[snake.head.first][snake.head.second] = 'H';
        }
    }
    
    if (turn == 0) {
        result += "========== Game Start ==========\n";
    } else {
        pair<int, int> curr_move = snakes[(turn-1) % n_snakes].moves_history.back();
        pair<int, int> prev_move;
        if (snakes.size() == 1) {
            prev_move = curr_move;
        } else {
            prev_move = snakes[(turn-1) % n_snakes].moves_history[snakes[(turn-1) % n_snakes].moves_history.size() - 2];
        }
        result += "========== Turn " + to_string(turn) + " - Snake " + to_string(turn % n_snakes) 
               + " | Snake" + to_string((turn-1) % n_snakes) + " " + "(" + to_string(prev_move.first) + "," + to_string(prev_move.second) + ")" 
               + " -> " + "(" + to_string(curr_move.first) + "," + to_string(curr_move.second) + ")" + " ==========\n";
    }
    
    result += "+";
    for (int j = 0; j < board_width; j++) {
        result += "-";
    }
    result += "+\n";
    
    for (int i = 0; i < board_height; i++) {
        result += "|";
        for (int j = 0; j < board_width; j++) {
            result += board[i][j];
        }
        result += "|\n";
    }
    
    result += "+";
    for (int j = 0; j < board_width; j++) {
        result += "-";
    }
    result += "+\n";
    
    // snake positions information
    for (size_t i = 0; i < snakes.size(); i++) {
        const Snake& snake = snakes[i];
        if (eliminated_snakes.find(i) != eliminated_snakes.end()) {
            result += "(dead) Snake " + to_string(i) + ": Head at (" + to_string(snake.head.first) + "," + to_string(snake.head.second) + "), ";
        } else {
            result += "Snake " + to_string(i) + ": Head at (" + to_string(snake.head.first) + "," + to_string(snake.head.second) + "), ";
        }
        result += "Length: " + to_string(snake.tail.size() + 1) + "\n";
        
        // print movement history
        result += " Movement history: ";
        for (const auto& position : snake.moves_history) {
            result += "(" + to_string(position.first) + "," + to_string(position.second) + ") ";
        }
        result += "\n";
    }
    
    // print apple positions
    result += "Apples: ";
    for (size_t i = 0; i < apples.size(); i++) {
        result += "(" + to_string(apples[i].position.first) + "," + to_string(apples[i].position.second) + ") ";
    }
    result += "\n\n";
    
    return result;
}

// function checks if given snake is in eliminated_snakes set
bool State::is_snake_alive(int snake_idx) {
    // check if snake is alive
    return eliminated_snakes.find(snake_idx) == eliminated_snakes.end();
}

double State::score_state(const State& initial_state) {
    // player 0 is minimaxing player, player 1 is maximizing player
    // draw happens on both snakes having the same length and both eliminated or both alive
    // we have only two snakes

    // index of the root snake in the initial state
    int maximized_player = (initial_state.turn % initial_state.n_snakes);
    int minimized_player = ((initial_state.turn + 1) % initial_state.n_snakes);


    double score = 0.0;


    // penalty for dying
    if (!is_snake_alive(maximized_player)) {
        // cout << "Penalty for dying, returning -100" << endl;
        score -=15.0;
    }

    // penalty for blocking the maximized snake
    if (is_snake_alive(maximized_player) && get_all_possible_moves(maximized_player).empty()){
        // cout << "Blocked maximized snake, returning -100" << endl;
        score  -=15.0;
    }

    // killing the opponent score
    if (initial_state.eliminated_snakes.find(minimized_player) == initial_state.eliminated_snakes.end()
        && !is_snake_alive(minimized_player)
        ) {
            // cout << "Killed opponent, adding score normal" << endl;
            score += 30.0;
    }


    // if (is_game_over()){
    //     int max_len = snakes[maximized_player].tail.size();
    //     int min_len = snakes[minimized_player].tail.size();
    //     if (max_len > min_len) return 100.0;
    //     if (max_len < min_len) return -100.0;
    //     return 0.0;              
    // }

    


    int snake_initial_length = initial_state.snakes[maximized_player].tail.size() + 1; // +1 for head
    int snake_current_length = snakes[maximized_player].tail.size() + 1; // +1 for head
    
    if (is_snake_alive(maximized_player) && snake_initial_length < snake_current_length) {
        score += (snake_current_length - snake_initial_length) * 2.0;
    }

    // closer to apples score
    if (!apples.empty()){
        int cloest_apples_amount = 0;

        // which snake is closer to any apple
        for (const Apple& apple : apples) {
            double dist_maximized = abs(snakes[maximized_player].head.first - apple.position.first) + abs(snakes[maximized_player].head.second - apple.position.second);
            double dist_minimized = abs(snakes[minimized_player].head.first - apple.position.first) + abs(snakes[minimized_player].head.second - apple.position.second);

            // bonus for being closer to an apple than the enemy
            if (dist_maximized < dist_minimized) {
                // cloest_apples_amount++;
                score += 0.25;
            }

            // bonus for being just close to an apple
            if (dist_maximized <= 2) {
                score += 0.25;
            }
        }

        // random numebr between 0 and 1
        random_device rd;
        mt19937 gen(rd());
        uniform_real_distribution<double> distr(0.0, 1.0);
        double random_factor = distr(gen);

        // score += 0.25 * cloest_apples_amount;
    }

    

    // // killing the oponent score
    // if (initial_state.eliminated_snakes.find(minimized_player) == initial_state.eliminated_snakes.end()
    //     && !is_snake_alive(minimized_player)
    //     ) {
    //         cout << "Killed opponent, adding score normal" << endl;
    //         score += 100.0;
    // }


    return score;


    // double score = 0;
    // // // Example: difference in length
    // // score += (snakes[1].tail.size() - snakes[0].tail.size()) * 10;

    // int snake_0_initial_length = prev_state.snakes[0].tail.size() + 1; // +1 for head
    // int snake_1_initial_length = prev_state.snakes[1].tail.size() + 1; // +1 for head

    // int current_snake_0_length = snakes[0].tail.size() + 1; // +1 for head
    // int current_snake_1_length = snakes[1].tail.size() + 1; // +1 for head


    // if (is_snake_alive(0) && snake_0_initial_length < snakes[0].tail.size() + 1) {
    //     score -= double(pow(0.85, turn - prev_state.turn) * (current_snake_0_length - snake_0_initial_length));
    // }
    // if (is_snake_alive(1) && snake_1_initial_length < snakes[1].tail.size() + 1){
    //     score += double(pow(0.85, turn - prev_state.turn) *  (current_snake_1_length - snake_1_initial_length));
    // }


    // if (!apples.empty()){
    //     // get nearest distance to an apple
    //     int min_dist_0 = numeric_limits<int>::max();
    //     int min_dist_1 = numeric_limits<int>::max();

    //     // which snake is closer to any apple
    //     for (const Apple& apple : apples) {
    //         min_dist_0 = min(min_dist_0, abs(snakes[0].head.first - apple.position.first) + abs(snakes[0].head.second - apple.position.second));
    //         min_dist_1 = min(min_dist_1, abs(snakes[1].head.first - apple.position.first) + abs(snakes[1].head.second - apple.position.second));
    //     }

    //     if (is_snake_alive(0)){
    //         score -= 0.25;

    //         // if snake is like 2 fields from apple add close again
    //         if (min_dist_0 <= 2){
    //             score -= 0.25;
    //         }
    //     }

    //     if (is_snake_alive(1)){
    //         score += 0.25;

    //         if (min_dist_1 <= 2){
    //             score += 0.25;
    //         }
    //     }

    // }


    // if (prev_state.eliminated_snakes.find(0) == prev_state.eliminated_snakes.end() && 
    //     !is_snake_alive(0)) {
    //         score += 5.0; // snake 0 died
    // } else if (prev_state.eliminated_snakes.find(1) == prev_state.eliminated_snakes.end() && 
    //            !is_snake_alive(1)) {
    //         score -= 5.0; // snake 1 died
    // }


    // // Add more heuristics, always positive for maximizing player, negative for minimizing

    // return score;


    // int snake_0_initial_length = prev_state.snakes[0].tail.size() + 1; // +1 for head
    // int snake_1_initial_length = prev_state.snakes[1].tail.size() + 1; // +1 for head



    // if (is_snake_alive(0) && snake_0_initial_length > snakes[0].tail.size() + 1) {
    //     total_score -= pow(0.85, turn - prev_state.turn);
    // }
    // if (is_snake_alive(0) && snake_1_initial_length > snakes[1].tail.size() + 1){
    //     total_score += pow(0.85, turn - prev_state.turn);
    // }

    // // give some score for killing the opponent
    // if (prev_state.eliminated_snakes.find(0) == prev_state.eliminated_snakes.end() && 
    //     !is_snake_alive(0)) {
    //         total_score += 1.0; // snake 0 died
    // } else if (prev_state.eliminated_snakes.find(1) == prev_state.eliminated_snakes.end() && 
    //            !is_snake_alive(1)) {
    //         total_score -= 1.0; // snake 1 died
    // }
   
    // if (!apples.empty()){
    //     // get nearest distance to an apple
    //     int min_dist_0 = numeric_limits<int>::max();
    //     int min_dist_1 = numeric_limits<int>::max();

    //     // which snake is closer to any apple
    //     for (const Apple& apple : apples) {
    //         min_dist_0 = min(min_dist_0, abs(snakes[0].head.first - apple.position.first) + abs(snakes[0].head.second - apple.position.second));
    //         min_dist_1 = min(min_dist_1, abs(snakes[1].head.first - apple.position.first) + abs(snakes[1].head.second - apple.position.second));
    //     }

    //     if (is_snake_alive(0)){
    //         total_score -= 0.25;

    //         // if snake is like 2 fields from apple add close again
    //         if (min_dist_0 <= 2){
    //             total_score -= 0.25;
    //         }
    //     }

    //     if (is_snake_alive(1)){
    //         total_score += 0.25;

    //         if (min_dist_1 <= 2){
    //             total_score += 0.25;
    //         }
    //     }

    // }


    // // add a lot of points for blocking the enemy
    // if (is_snake_alive(1) && get_all_possible_moves(1).empty()){
    //     total_score -= 1.0;
    // }

    // if (is_snake_alive(0) && get_all_possible_moves(0).empty()){
    //     total_score += 1.0;
    // }

    // return total_score;    
}
// returns the index of the winning snake or -1 if no winner yet
int State::get_winner() {
    // winner is calculated based on scores
    
    if (is_game_over()){
        if (snakes[0].tail.size() > snakes[1].tail.size()) {
            // snake 0 is the winner
            return 0;
        }else if (snakes[1].tail.size() > snakes[0].tail.size()) {
            // snake 1 is the winner
            return 1;

        }else {
            // no winner yet, both snakes have the same length
            return -1;
        }
    }

    return -1;
}