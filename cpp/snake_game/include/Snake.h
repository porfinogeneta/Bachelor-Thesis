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

    // snake moves history
    vector<pair<int, int>> moves_history;
    // snake tail lengths history (size is measured after a move)
    vector<size_t> tails_len_history;

    Snake(int x, int y);
    void move_snake(char direction);
    pair<int, int> get_last_snake_segment();
};

#endif