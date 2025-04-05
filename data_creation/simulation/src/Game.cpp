#include "Game.h"
#include <iostream>
#include <random>
#include <set>



Game::Game(){
    set_log_file(log_filename);
}

Game::~Game(){
    if (log_file.is_open()){
        log_file.close();
    }
}


void Game::set_log_file(const std::string& filename) {
    if (log_file.is_open()) {
        log_file.close();
    }
    log_filename = filename;
    log_file.open(log_filename);
}


// generates distinct pairs in range (beginning snakes and apples positions)
vector<pair<int, int> > Game::generateDistinctPairs(size_t n) {
    
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


void  Game::get_beginning_snake_positions(vector<pair<int, int> >& snakes) {
    vector<pair<int, int> > position_pairs = generateDistinctPairs(n_snakes);
    
    for (size_t i = 0; i < position_pairs.size(); i++) {
        snakes.push_back(position_pairs[i]);
    }
}

void Game::get_apples_positions(vector<pair<int, int> >& apples, vector<pair<int, int> >& occupied_positions){
    
    int apples_to_generate = n_apples - apples.size();
    
    if (apples_to_generate <= 0) {
        return;
    }
    
    set<pair<int, int> > occupied_set(occupied_positions.begin(), occupied_positions.end());
    
    // add rest of the apples positions to occupied positions
    for (const auto& apple : apples) {
        occupied_set.insert(apple);
    }
    
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> dist(0, 9);
    
    // add new apples as long as it needs to be added and there is place for them
    while (apples_to_generate > 0 and (size_t)apples_to_generate < (board_width * board_height - occupied_set.size())) {
        pair<int, int> new_position = make_pair(dist(gen), dist(gen));
        
        // Check if this position is already occupied
        if (occupied_set.find(new_position) == occupied_set.end()) {
            // If not occupied, add it as a new apple
            apples.push_back(new_position);
            occupied_set.insert(new_position);
            apples_to_generate--;
        }
    }
}

bool Game::is_snake_colliding_snakes(Snake& snake_moving, vector<Snake>& snakes){
    pair<int, int> moving_head = snake_moving.head;

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
        
        // collision with this snake's tail
        for (const auto& tail_segment : snake_moving.tail) {
            if (moving_head == tail_segment) {
                return true;
            }
        }
    }

    return false;
}

bool Game::is_snake_out_of_bounds(Snake& snake_moving){
    pair<int, int> moving_head = snake_moving.head;

    return moving_head.first < 0 or moving_head.first > board_width - 1
        or moving_head.second < 0 or moving_head.second > board_height - 1;
        
}

bool Game::is_snake_apple_colliding(Snake& snake_moving, vector<pair<int, int> >& apples){
    pair<int, int> moving_head = snake_moving.head;
    for (size_t i = 0; i < apples.size(); i++){
        if (moving_head == apples[i]){
            // delete apple after colliding
            apples.erase(apples.begin() + i);
            return true;
        }
    }

    return false;
}


void Game::print_snake_game_state(vector<Snake>& snakes, vector<pair<int, int> >& apples, int turn) {
    // Create an empty board representation
    vector<vector<char> > board(board_height, vector<char>(board_width, '.'));
    
    // Place apples on the board
    for (const auto& apple : apples) {
        if (apple.first >= 0 && apple.first < board_height && 
            apple.second >= 0 && apple.second < board_width) {
            board[apple.first][apple.second] = 'A';
        }
    }
    
    // Place snakes on the board
    for (size_t i = 0; i < snakes.size(); i++) {
        const Snake& snake = snakes[i];
        
        // Place tail segments
        for (const auto& segment : snake.tail) {
            if (segment.first >= 0 && segment.first < board_height && 
                segment.second >= 0 && segment.second < board_width) {
                board[segment.first][segment.second] = 'o';
            }
        }
        
        // Place snake head (using different numbers for different snakes)
        if (snake.head.first >= 0 && snake.head.first < board_height && 
            snake.head.second >= 0 && snake.head.second < board_width) {
            board[snake.head.first][snake.head.second] = '0' + i;  // Using '0', '1', etc. for different snake heads
        }
    }
    
    // Print the current turn information
    if (log_file.is_open()){
        log_file << "========== Turn " << turn << " ==========" << endl;

        // Print the top border
        log_file << "+";
        for (int j = 0; j < board_width; j++) {
            cout << "-";
        }
        log_file << "+" << endl;
        
        // Print the board with side borders
        for (int i = 0; i < board_height; i++) {
            log_file << "|";
            for (int j = 0; j < board_width; j++) {
                log_file << board[i][j];
            }
            log_file << "|" << endl;
        }
        
        // Print the bottom border
        log_file << "+";
        for (int j = 0; j < board_width; j++) {
            log_file << "-";
        }
        log_file << "+" << endl;
        
        // Print snake positions information
        for (size_t i = 0; i < snakes.size(); i++) {
            const Snake& snake = snakes[i];
            log_file << "Snake " << i << ": Head at (" << snake.head.first << "," << snake.head.second << "), ";
            log_file << "Length: " << snake.tail.size() + 1 << endl;
        }
        
        log_file << "Apples: " << apples.size() << endl;
        log_file << endl;
        }
    
    
    
}

void Game::run_game(){
    bool is_playing = true;
    int turn = 0;

    vector<pair<int, int> > snake_positions;
    vector<Snake> snakes;


    get_beginning_snake_positions(snake_positions);
    // initialize snakes
    for (const pair<int, int>& snake_pos: snake_positions){
        snakes.push_back(Snake(snake_pos.first, snake_pos.second));
    }
    
    // populate apples positions vector
    vector<pair<int, int> > apples;
    get_apples_positions(apples, snake_positions);

    

    Agent random_agent = Agent();

    while (is_playing)
    {
        int snake_moving_idx = turn % n_snakes;
        
        // this is the place where agent will come and decide on move
        char direction = random_agent.getRandomChar();

        // segment that might be added if collided with an apple
        pair<int, int> new_snake_segment = snakes[snake_moving_idx].get_last_snake_segment();

        snakes[snake_moving_idx].move_snake(direction);

        // for (const auto& position : apples) {
        //     cout << position.first << position.second << endl;
        // }
        

        if (is_snake_colliding_snakes(snakes[snake_moving_idx], snakes)
            or is_snake_out_of_bounds(snakes[snake_moving_idx])
            ) {
                is_playing = false;
            }

        if (is_snake_apple_colliding(snakes[snake_moving_idx], apples)){
            // cout << "eating" << endl;
            // add new segment to the snake
            snakes[snake_moving_idx].tail.push_back(new_snake_segment);

            
            // apple cannot be generated on the positions occupied by snakes
            vector<pair<int, int> > occupied_positions;
            for (const Snake& snake : snakes) {
                occupied_positions.push_back(snake.head);
                for (const auto& segment : snake.tail) {
                    occupied_positions.push_back(segment);
                }
            }

            get_apples_positions(apples, occupied_positions);
        }

        turn++;

        
        print_snake_game_state(snakes, apples, turn);

    }

    cout << "Game Over! Final score:" << endl;
    for (size_t i = 0; i < snakes.size(); i++) {
        cout << "Snake " << i << " length: " << snakes[i].tail.size() + 1 << endl;
    }
}
