#ifndef SNAKE_H
#define SNAKE_H

#include <vector>
#include <utility>
using namespace std;

class Snake {
private:
    std::pair<int, int> get_move(char move);

public:
    std::pair<int, int> head;
    std::vector<std::pair<int, int>> tail;

    Snake(int x, int y);
    void move_snake(char direction);
    std::pair<int, int> get_last_snake_segment();
};

#endif