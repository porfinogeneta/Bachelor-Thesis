#include <vector>
#include <set>
#include "Snake.h"
#include "Apple.h"
#include "State.h"

#ifndef AGENT_H
#define AGENT_H

using namespace std;



class Agent {
private:
    char directions[4] = {'U', 'D', 'L', 'R'};

public:
    char getRandomChar();

    char bfs_based_agent(
        const State &state, int current_snake_idx
    );

    char random_based_agent(const State &state, int current_snake_idx);

    // set<pair<int, int> > get_positions_occupiend_by_snakes(State state);
    // set<pair<int, int> > get_positions_occupied_by_apples(const vector<Apple>& apples);

};

#endif