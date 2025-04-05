#ifndef SNAKE_H
#define SNAKE_H

#include <vector>
#include <utility>
using namespace std;

class Snake {
private:
    pair<int, int> get_move(char move);

public:
    pair<int, int> head;
    vector<pair<int, int>> tail;

    Snake(int x, int y);
    void move_snake(char direction);
    pair<int, int> get_last_snake_segment();
};

#endif