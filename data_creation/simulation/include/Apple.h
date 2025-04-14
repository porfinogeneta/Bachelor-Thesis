// Apple.h
#ifndef APPLE_H
#define APPLE_H

#include <utility>
#include <iostream>

using namespace std;

class Apple {
public:
    pair<int, int> position;
    Apple(int x, int y);
    void print();
};

#endif