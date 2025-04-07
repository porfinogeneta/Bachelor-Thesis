#include <vector>
#include <set>
#include <Snake.h>

#ifndef AGENT_H
#define AGENT_H

using namespace std;


set<pair<int, int> > get_positions_occupiend_by_snakes(size_t current_snake_idx, const vector<Snake>& snakes);

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