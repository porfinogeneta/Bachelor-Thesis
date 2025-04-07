#include "SnakeState.h"

SnakeState::SnakeState(int t,
                     std::set<std::pair<int, int>> snake_pos,
                     std::set<std::pair<int, int>> apple_pos,
                     Snake& snake,
                     int width,
                     int height)
    : turn(t),
      snake_positions(snake_pos),
      apple_positions(apple_pos),
      current_snake(snake),
      board_width(width),
      board_height(height) {}

bool SnakeState::is_position_in_set(std::pair<int, int> position, std::set<std::pair<int, int>> positions) {
    return positions.find({position.first, position.second}) != positions.end();
}

bool SnakeState::is_position_out_of_bounds(int x, int y, int board_width, int board_height) {
    return x < 0 || x >= board_width || y < 0 || y >= board_height;
}

void SnakeState::move(char direction) {
    current_snake.move_snake(direction);
    turn = (turn + 1) % n_snakes;
    // what needs to remain after apple eating
    std::pair<int, int> last_segment = current_snake.get_last_snake_segment();
    if (is_position_in_set(current_snake.head, apple_positions)) {
        // Add new apple
        // pair<int, int> new_apple = generate_new_apple();
        // apple_positions.insert(new_apple);
        snake_positions.insert(last_segment);
    }
}

std::vector<char> SnakeState::get_legal_moves() {
    std::vector<char> legal_moves;
    char directions[4] = {'U', 'D', 'L', 'R'};
    for (char move : directions) {
        std::pair<int, int> new_head = current_snake.head;
        switch (move) {
            case 'U':
                new_head.first -= 1;
                break;
            case 'D':
                new_head.first += 1;
                break;
            case 'L':
                new_head.second -= 1;
                break;
            case 'R':
                new_head.second += 1;
                break;
        }
        if (!is_position_in_set(new_head, snake_positions) && 
            !is_position_out_of_bounds(new_head.first, new_head.second, board_width, board_height)) {
            legal_moves.push_back(move);
        }
    }
    return legal_moves;
}

bool SnakeState::game_over() {
    // Check if the snake collides with itself or goes out of bounds
    if (is_position_in_set(current_snake.head, snake_positions) || 
        is_position_out_of_bounds(current_snake.head.first, current_snake.head.second, board_width, board_height)) {
        return true;
    }
    return false;
}