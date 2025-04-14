#include "NodeMCTS.h"
#include <vector>
#include <unordered_map> 

using namespace std;

double EXPLORATION_RATE = sqrt(2.0);



Node::Node(char move, Node* parent) : move(move), N(0), Q(0), parent(parent) {}

Node::~Node() {
    for (auto& child : children) {
        delete child.second;
    }
}


void Node::add_children(vector<Node*>& children) {
    for (auto& child : children) {
        children[child->move] = child;
    }

}

double Node::get_value(double explore){
    if (N == 0){
        return (explore == 0) ? 0 : INFINITY;
    }
    // value of a node is detemined by the formula
    else {
        return Q / N + explore * sqrt(log(parent->N) / N);
    }
}


