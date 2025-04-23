# kompilator i flagi
CXX := g++
CXXFLAGS := -Wall -Wextra -O2 -std=c++17 -I/opt/homebrew/include
# nazwa wynikowego programu
BIN := snake_game_generation
# nazwa folderu w którym pojawią sie object files
OBJ_DIR := build

# ścieżki do plików
SRC_DIR := ..
INCLUDE_DIR := ../snake_game/include
SCRIPTS_DIR := ../snake_game/scripts

# wszystkie pliki źródłowe
SRCS := main.cpp \
 $(INCLUDE_DIR)/Agent.h \
 $(SCRIPTS_DIR)/Agent.cpp \
 $(INCLUDE_DIR)/Apple.h \
 $(SCRIPTS_DIR)/Apple.cpp \
 $(INCLUDE_DIR)/Snake.h \
 $(SCRIPTS_DIR)/Snake.cpp \
 $(INCLUDE_DIR)/Serializer.h \
 $(SCRIPTS_DIR)/Serializer.cpp \
 $(INCLUDE_DIR)/State.h \
 $(SCRIPTS_DIR)/State.cpp

# lista object files (zrobiona z plików wejściowych)
OBJS := $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(filter %.cpp,$(SRCS)))
# OBJS += $(patsubst $(SCRIPTS_DIR)/%.cpp,$(OBJ_DIR)/scripts/%.o,$(filter $(SCRIPTS_DIR)/%.cpp,$(SRCS)))

all: $(BIN)

# linkowanie wynikowego programu
$(BIN): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# jak ma kompilować dla plików z głównego katalogu
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

# jak ma kompilować dla plików ze scripts
$(OBJ_DIR)/scripts/%.o: $(SCRIPTS_DIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

# usuwanie tylko wyjściowej binarki
clean:
	rm -f $(BIN)

# usuwanie wszystkich object files
distclean: clean
	rm -rf $(OBJ_DIR)

.PHONY: all clean distclean