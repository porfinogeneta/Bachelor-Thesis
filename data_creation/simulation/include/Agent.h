#include <vector>
#include <Snake.h>
#include "Game.h"

#ifndef AGENT_H
#define AGENT_H

using namespace std;

class Agent {
private:
    char directions[4] = {'U', 'D', 'L', 'R'};

public:
    char getRandomChar();

    char bfs_based_agent(
        const vector<Snake>& snakes,
        const vector<pair<int, int> >& apples,
        int current_snake_idx,
        int board_width,
        int board_height
    );

};

#endif