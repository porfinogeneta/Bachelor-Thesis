#include <iostream>
#include <vector>
#include <tuple>
#include <string>
#include <random>
#include <unistd.h>
#include <set>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "../snake_game/include/State.h"
#include "../snake_game/include/Serializer.h"
#include "../snake_game/include/Agent.h"
// #include "../include/Snake.h"


using namespace std;

// game configs
int n_snakes = 2;
int n_apples = 5;
int board_width = 10;
int board_height = 10;


// string receive_complete_json(int socket) {
//     string buffer = "";
//     int depth = 0;
//     bool in_json = false;
//     int start_idx = 0;
    
//     char chunk[1024];
//     while (true) {
//         memset(chunk, 0, sizeof(chunk));
//         int bytes_received = recv(socket, chunk, sizeof(chunk) - 1, 0);
        
//         if (bytes_received <= 0) {
//             return ""; // Connection closed or error
//         }
        
//         buffer += string(chunk, bytes_received);
        
//         // Try to extract one complete JSON object
//         for (size_t i = 0; i < buffer.length(); i++) {
//             char c = buffer[i];
//             if (c == '{') {
//                 if (depth == 0) {
//                     in_json = true;
//                     start_idx = i;
//                 }
//                 depth++;
//             } else if (c == '}') {
//                 depth--;
//                 if (depth == 0 && in_json) {
//                     // We have a complete JSON object
//                     string json_str = buffer.substr(start_idx, i - start_idx + 1);
//                     buffer = buffer.substr(i + 1); // Save remaining data for next call
//                     return json_str;
//                 }
//             }
//         }
//     }
// }

// string leftover_data = "";
string receive_complete_json(int sock) {
    int depth = 0;
    bool in_json = false;
    size_t beginning = 0;
    string buffer = "";
    // string buffer = leftover_data; // Start with any leftover data from previous calls
    // leftover_data = ""; // Clear the leftover data as we've now incorporated it
    
    while (true) {
 
        char chunk[4097]; // 1024 + 1 for null terminator
        int bytesReceived = recv(sock, chunk, 1024, 0);
        if (bytesReceived <= 0) {
            return "";
        }
        chunk[bytesReceived] = '\0';
        buffer += chunk; // Append the new data to our existing buffer
    
        
        // Process the buffer character by character
        for (size_t i = 0; i < buffer.size(); i++) {
            if (buffer[i] == '{') {
                if (depth == 0) {
                    in_json = true;
                    beginning = i;
                }
                depth++;
            } else if (buffer[i] == '}') {
                depth--;
                if (depth == 0 && in_json) {
                    string result = buffer.substr(beginning, i - beginning + 1);
                    
                    // // Save any remaining data for the next call
                    // if (i + 1 < buffer.size()) {
                    //     leftover_data = buffer.substr(i + 1);
                    // }
                    
                    return result;
                }
            }
        }
        
        // If we've processed the entire buffer without finding a complete JSON,
        // we need more data, so loop back and receive more
    }
}



void send_serialized_state(State *state, Serializer *serializer, int client_socket){
    string state_string = serializer->serialize_state(*state);

    cout << "Sending: " + state_string << endl;

    if ((send(client_socket, state_string.c_str(), state_string.size(), 0)) < 0){
        cerr << "Buffer overflown" << endl;
    }

}


int main() {


    // if (argc < 2){
    //     cout << "Usage: " << argv[0] << " <log_file_name>" << endl;
    //     return 1;
    // }

    
    Serializer serializer;

    // SOCKETS SETUP
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        cerr << "Error creating socket" << endl;
        return 1;
    }

    cout << "Socket created successfully" << endl;


    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);
    // bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr));
    if (::bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        cerr << "Error binding socket" << endl;
        return 1;
    }
    cout << "Socket bound successfully" << endl;


    if (listen(server_socket, 1) < 0) {
        cerr << "Error listening on socket" << endl;
        return 1;
    }

    
    cout << "C++ server waiting for Python client to connect..." << endl;


    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_addr_len);
    if (client_socket < 0) {
        cerr << "Error accepting client connection" << endl;
        return 1;
    }
    cout << "Python client connected" << endl;
    
    
    State state = State(n_snakes, n_apples, board_width, board_height);
    Agent agent = Agent();

    // cpp always begin
    bool is_cpp_turn = true;

    // since python is moving as the second one, its index is 1
    // cpp - 0 & python - 1
    while (true)
    {   
        cout << "C++'s turn" << endl;

        if (is_cpp_turn == true){
            char direction = agent.bfs_based_agent(state, 0);
            state.move(direction, 0);
            

            send_serialized_state(&state, &serializer, client_socket);
            is_cpp_turn = false; // it's python turn
            if (state.is_game_over()){
                cout << "Python won" << endl;
                break;
            }
        }else {
            
            cout << "Python's turn" << endl;

            string serialized_state;
            serialized_state = receive_complete_json(client_socket);

            cout << "Receiving" + serialized_state << endl;

            state = serializer.deserialize_state(serialized_state);
            is_cpp_turn = true;
        
            if (state.is_game_over()){
                cout << "C++ won" << endl;
                break;
            }

            cout << "before" << endl;
            // get new apples positions if Python side ate it xd
            if (state.n_apples != state.apples.size()){
                state.get_apples_positions(state.apples);
                cout << "After" << endl;
            }
        }
    }

    // clean sockets
    close(client_socket);
    close(server_socket);
    cout << "Socket closed" << endl;

    
    return 0;
}