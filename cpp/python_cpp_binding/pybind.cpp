// g++ -std=c++17 -shared -undefined dynamic_lookup -I./pybind11/include/ `python3.11 -m pybind11 --includes` pybind.cpp -o snake_lib.so `python3.11-config --ldflags`
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "snake_game/include/Agent.h"
#include "snake_game/include/Apple.h"
#include "snake_game/include/Snake.h"
#include "snake_game/include/State.h"

namespace py = pybind11;

PYBIND11_MODULE(snake_lib, m) {
    m.doc() = "pybind11 binding for the Snake game classes";

    // Binding for the Apple class
    py::class_<Apple>(m, "Apple")
        .def(py::init<int, int>(), "Construct an Apple object")
        .def_readwrite("position", &Apple::position, "Apple's position (pair of ints)")
        .def("print", &Apple::print, "Print Apple's position");

    // Binding for the Snake class
    py::class_<Snake>(m, "Snake")
        .def(py::init<int, int>(), "Construct a Snake object")
        .def_readwrite("head", &Snake::head, "Snake's head position (pair of ints)")
        .def_readwrite("tail", &Snake::tail, "Snake's tail segments (vector of pairs of ints)")
        .def_readwrite("moves_history", &Snake::moves_history, "History of snake moves")
        .def_readwrite("tails_len_history", &Snake::tails_len_history, "History of snake tail lengths")
        .def("move_snake", &Snake::move_snake, "Move the snake in a given direction")
        .def("get_last_snake_segment", &Snake::get_last_snake_segment, "Get the position of the last tail segment");

    // Binding for the State class
    py::class_<State>(m, "State")
        .def(py::init<int, int, int, int>(), "Construct a State object")
        .def_readwrite("n_snakes", &State::n_snakes, "Number of snakes")
        .def_readwrite("n_apples", &State::n_apples, "Number of apples")
        .def_readwrite("board_width", &State::board_width, "Board width")
        .def_readwrite("board_height", &State::board_height, "Board height")
        .def_readwrite("turn", &State::turn, "Current turn number")
        .def_readwrite("snakes", &State::snakes, "Vector of Snake objects")
        .def_readwrite("apples", &State::apples, "Vector of Apple objects")
        .def_readwrite("eliminated_snakes", &State::eliminated_snakes, "Set of eliminated snake indices")
        .def_readwrite("apples_history", &State::apples_history, "History of apple positions")
        .def_readwrite("idx_prev_snake", &State::idx_prev_snake, "Index of the previous snake that moved")
        .def_readwrite("whoose_prev_turn", &State::whoose_prev_turn, "Identifier of who took the previous turn")
        .def_readwrite("all_snakes_moves", &State::all_snakes_moves, "All snakes moves history")
        .def("generate_distinct_pairs", &State::generate_distinct_pairs, "Generate distinct pairs")
        // .def("set_log_file", &State::set_log_file, "Set the log file name")
        .def("move", &State::move, "Move a snake in a given direction")
        .def("get_beginning_snake_heads_positions", &State::get_beginning_snake_heads_positions, "Get initial snake head positions")
        .def("get_apples_positions", &State::get_apples_positions, "Get apple positions")
        .def("is_game_over", &State::is_game_over, "Check if the game is over")
        .def("is_snake_colliding_snakes", &State::is_snake_colliding_snakes, "Check for snake-snake collision")
        .def("is_snake_out_of_bounds", &State::is_snake_out_of_bounds, "Check if snake is out of bounds")
        .def("is_snake_apple_colliding", &State::is_snake_apple_colliding, "Check for snake-apple collision")
        .def("print_game_state", &State::print_game_state, "Print the current game state")
        .def("get_full_history", &State::get_full_history, "Get the full game history");

    // Binding for the Agent class
    py::class_<Agent>(m, "Agent")
        .def(py::init<>(), "Construct an Agent object")
        .def("bfs_based_agent", &Agent::bfs_based_agent, "Get move based on BFS algorithm");

    // // You can also expose free functions like 'add' if needed
    // m.def("add", &add, "A function that adds two numbers");

}