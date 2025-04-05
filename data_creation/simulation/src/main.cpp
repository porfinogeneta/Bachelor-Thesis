#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <random>
#include <set>


/**
 * 
 * TODO:
 * - funkcja do wrzucania węży na jakieś lokacje, nie te same [+]
 * - to samo dla jabłek [+]
 * - funkcja zmiany stanu by się przydała (ruch węża w odpowiednim kierunku, zmiana stanu jabłek) [+]
 * - jakieś ograniczenia na planszy i kolizje [+]
 * - zapis stanu po każdym ruchu do pliku
 * - ranom agent [+]
 * - naprawić bugi :(
 */

#include "Game.h"

int main(int argc, char* argv[]) {

    Game snakeGame;
    snakeGame.run_game();

    // if (argc > 1){
    //     string filename = argv[1];
    //     cout << "Logging game to file: " << filename << endl;
    //     snakeGame.set_log_file(filename);
    // }

    
    
    return 0;
}