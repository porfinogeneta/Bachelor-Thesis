#ifndef SNAKE_STATE_H
#define SNAKE_STATE_H

#include <set>
#include <vector>
#include <utility>
#include "Snake.h" // Assuming Snake class is defined in Snake.h

class SnakeState {
public:
    int turn;
    int n_snakes;
    std::set<std::pair<int, int>> snake_positions;
    std::set<std::pair<int, int>> apple_positions;
    Snake current_snake;
    int board_width;
    int board_height;

    SnakeState(int t,
               std::set<std::pair<int, int>> snake_pos,
               std::set<std::pair<int, int>> apple_pos,
               Snake& snake,
               int width,
               int height);

    bool is_position_in_set(std::pair<int, int> position, std::set<std::pair<int, int>> positions);
    bool is_position_out_of_bounds(int x, int y, int board_width, int board_height);
    void move(char direction);
    std::vector<char> get_legal_moves();
    bool game_over();
};

#endif // SNAKE_STATE_H