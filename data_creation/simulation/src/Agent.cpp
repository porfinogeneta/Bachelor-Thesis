#include "Agent.h"
#include <random>



    
char Agent::getRandomChar() {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distr(0, 3);

    return directions[distr(gen)];
};

// char Agent::bfsBasedChoice(vector<Snake> snakes, vector<pair<int, int> > apples, int current_snake){
//    pair<int, int> moving_head = snakes[current_snake];


// }
    
    