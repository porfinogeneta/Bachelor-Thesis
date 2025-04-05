#include "Snake.h"




Snake::Snake(int x, int y) {
    head = make_pair(x, y);
}

pair<int, int> Snake::get_move(char move) {
    switch (move) {
        case 'U':
            return make_pair(-1, 0);
        case 'D':
            return make_pair(1, 0);
        case 'L':
            return make_pair(0, -1);
        case 'R':
            return make_pair(0, 1);
        default:
            return make_pair(0, 0);
    }
}


void Snake::move_snake(char direction){
    pair<int, int> move_pair = get_move(direction);
    // cout << move_pair.first << endl;
    head.first += move_pair.first;
    head.second += move_pair.second;

    for (size_t i = 0; i < tail.size(); i++){
        tail[i].first += move_pair.first;
        tail[i].second += move_pair.second;
    }

    // cout << head.first << endl;
}

pair<int, int> Snake::get_last_snake_segment(){
    if (tail.size() == 0){
        return make_pair(head.first, head.second);
    }
    return make_pair(tail.back().first, tail.back().second);
}

