#ifndef NODE_H
#define NODE_H

#include <vector>
#include <unordered_map>
#include <cmath>

// Default exploration rate
extern double EXPLORATION_RATE;

using namespace std;

class Node {
public:
    char move;
    int N; // number of simulations
    int Q; // number of wins
    Node* parent;
    unordered_map<char, Node*> children;

    // Constructor
    Node(char move, Node* parent);
    
    // Destructor
    ~Node();
    
    // Methods
    void add_children(std::vector<Node*>& children);
    double get_value(double explore = EXPLORATION_RATE);
};

#endif // NODE_H