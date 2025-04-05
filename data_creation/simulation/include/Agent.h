#include <vector>
#include <Snake.h>

#ifndef AGENT_H
#define AGENT_H

using namespace std;

class Agent {
private:
    char directions[4] = {'U', 'D', 'L', 'R'};

public:
    char getRandomChar();


};

#endif