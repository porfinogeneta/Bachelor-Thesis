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
    pair<int, int> head_cpy = head;

    head.first += move_pair.first;
    head.second += move_pair.second;

    if (tail.size() > 0){
        // get rid of the last segment
        tail.pop_back();
        // at the beginning of the tail insert the head
        tail.insert(tail.begin(), head_cpy);
    }
}

pair<int, int> Snake::get_last_snake_segment(){
    if (tail.size() == 0){
        return make_pair(head.first, head.second);
    }
    return make_pair(tail.back().first, tail.back().second);
}

char Snake::get_last_direction() {
    if (moves_history.size() < 2) {
        return ' '; 
    }
    pair<int, int> last_move = moves_history[moves_history.size() - 1];
    pair<int, int> second_last_move = moves_history[moves_history.size() - 2];

    if (last_move.first < second_last_move.first) {
        return 'U';
    } else if (last_move.first > second_last_move.first) {
        return 'D';
    } else if (last_move.second < second_last_move.second) {
        return 'L';
    } else {
        return 'R';
    }
}



