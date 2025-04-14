#include "State.h"
#include <iostream>
#include <string>
#include <random>
#include <set>





State::State(int n_snakes, int n_apples, int board_width, int board_height, string log_filename) {

    // set game parameters
    this->n_snakes = n_snakes;
    this->n_apples = n_apples;
    this->board_width = board_width;
    this->board_height = board_height;
    this->log_filename = log_filename;
    
    set_log_file(log_filename);

    snakes.clear();

    // create heads
    vector<pair<int, int> > snake_heads;
    get_beginning_snake_heads_positions(snake_heads);

    // initialize snakes
    for (size_t i = 0; i < snake_heads.size(); i++) {
        Snake new_snake = Snake(snake_heads[i].first, snake_heads[i].second);
        new_snake.moves_history.push_back(snake_heads[i]);
        snakes.push_back(new_snake);
    }

    // create apples positions
    apples.clear();
    get_apples_positions(apples);
}


State::~State(){
    if (log_file.is_open()){
        log_file.close();
    }
}


void State::set_log_file(const std::string& filename) {
    if (log_file.is_open()) {
        log_file.close();
    }
    log_filename = filename;
    log_file.open(log_filename);
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

bool State::is_snake_out_of_bounds(Snake& snake_moving){
    pair<int, int> moving_head = snake_moving.head;

    return moving_head.first < 0 or moving_head.first > board_width - 1
        or moving_head.second < 0 or moving_head.second > board_height - 1;
        
}

// returns bool, but also gets rid of eaten apple
bool State::is_snake_apple_colliding(Snake& snake_moving, vector<Apple>& apples){
    pair<int, int> moving_head = snake_moving.head;
    for (size_t i = 0; i < apples.size(); i++){
        if (moving_head == apples[i].position){
            // delete apple after colliding
            apples.erase(apples.begin() + i);
            return true;
        }
    }

    return false;
}

// returns true if snake moved successfully
// returns false if snake collided with another snake or with the wall
bool State::move(char direction, int snake_moving_idx){

    // check if snake is already eliminated, treat eliminated snake as a wall
    if (eliminated_snakes.find(snake_moving_idx) != eliminated_snakes.end()){
        return false;
    }
    
    // Snake current_snake = snakes[snake_moving_idx];
    // current_snake.move_snake(direction);
    
    
    
    // segment that might be added if collided with an apple
    pair<int, int> new_snake_segment = snakes[snake_moving_idx].get_last_snake_segment();

    snakes[snake_moving_idx].move_snake(direction);
    
    // add new position to the snake moves history
    snakes[snake_moving_idx].moves_history.push_back(snakes[snake_moving_idx].head);


    if (is_snake_colliding_snakes(snakes[snake_moving_idx], snakes)
        || is_snake_out_of_bounds(snakes[snake_moving_idx])
        ) {
            // acknowledge that snake is eliminated
            eliminated_snakes.insert(snake_moving_idx);
            // // after this move snake is dead, but it has moved the posisition of it's body is not correct, to mitigate
            // // this problem, we need to remove the last move from the moves history
            // // and make the first element from the tail to be a head, and eliminated
            // // tail segment would reappear
            // snakes[snake_moving_idx].moves_history.pop_back();
            // pair<int, int> prev_head_cpy = snakes[snake_moving_idx].tail[0];
            // snakes[snake_moving_idx].head = prev_head_cpy;
            // snakes[snake_moving_idx].tail.push_back(new_snake_segment);
            return false;
        }

    if (is_snake_apple_colliding(snakes[snake_moving_idx], apples)){
        // cout << "eating" << endl;
        // add new segment to the snake
        snakes[snake_moving_idx].tail.push_back(new_snake_segment);

        // function generates new apple position that's not on the snake or on one of the apples
        get_apples_positions(apples);
    }

    return true;

}

// all snakes eliminated => game over
bool State::is_game_over() {
    
    // // print eliminated snakes
    // for (const auto& snake : eliminated_snakes) {
    //     cout << "Snake " << snake << " is eliminated." << endl;
    // }

    return eliminated_snakes.size() == (uint)n_snakes;
}


void State::print_game_state(int turn) {

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
    
    // Print the current turn information
    if (log_file.is_open()) {

        if (turn == 0) {
            log_file << "========== Game Start ==========" << endl;
        }else {
            pair<int, int> curr_move = snakes[(turn-1) % n_snakes].moves_history.back();
            pair<int, int> prev_move;
            if (snakes.size() == 1) {
                prev_move = curr_move;
            }else {
                prev_move = snakes[(turn-1) % n_snakes].moves_history[snakes[(turn-1) % n_snakes].moves_history.size() - 2];
            }
            log_file << "========== Turn " << turn << " - Snake " << turn % n_snakes \
            << " | Snake" << (turn-1) % n_snakes << " " <<  "(" << prev_move.first << "," << prev_move.second << ")" \
            << " -> " << "(" << curr_move.first << "," << curr_move.second << ")" << " ==========" << endl;
        }
        log_file << "+";
        for (int j = 0; j < board_width; j++) {
            log_file << "-";
        }
        log_file << "+" << endl;
        
        for (int i = 0; i < board_height; i++) {
            log_file << "|";
            for (int j = 0; j < board_width; j++) {
                log_file << board[i][j];
            }
            log_file << "|" << endl;
        }
        
        log_file << "+";
        for (int j = 0; j < board_width; j++) {
            log_file << "-";
        }
        log_file << "+" << endl;
        
        // snake positions information
        for (size_t i = 0; i < snakes.size(); i++) {
            const Snake& snake = snakes[i];
            if (eliminated_snakes.find(i) != eliminated_snakes.end()) {
                log_file << "(dead) Snake " << i << ": Head at (" << snake.head.first << "," << snake.head.second << "), ";
            }else {
                log_file << "Snake " << i << ": Head at (" << snake.head.first << "," << snake.head.second << "), ";

            }
            log_file << "Length: " << snake.tail.size() + 1 << endl;
            
            // print movement history
            log_file << "  Movement history: ";
            for (const auto& position : snake.moves_history) {
                log_file << "(" << position.first << "," << position.second << ") ";
            }
            log_file << endl;
        }

        // print apple positions
        log_file << "Apples: ";
        for (size_t i = 0; i < apples.size(); i++) {
            log_file << "(" << apples[i].position.first << "," << apples[i].position.second << ") ";
        }
        log_file << endl << endl;
    }
}
