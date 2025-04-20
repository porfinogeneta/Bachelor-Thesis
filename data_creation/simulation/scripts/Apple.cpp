#include <utility>
#include <iostream>
#include "Apple.h"

// using namespace std;


Apple::Apple(int x, int y) {
    position = make_pair(x, y);
}

void Apple::print() {
    cout << "Apple at (" << position.first << ", " << position.second << ")" << endl;
}