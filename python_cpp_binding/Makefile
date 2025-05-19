# Makefile for Snake Game Python-C++ binding

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -fPIC -Wall -O2

# Python configuration
# PYTHON = python3.11
PYTHON = python3.10
PYTHON_CONFIG = $(PYTHON)-config
PYTHON_INCLUDES = $(shell $(PYTHON) -m pybind11 --includes)
PYTHON_LDFLAGS = $(shell $(PYTHON_CONFIG) --ldflags)

# Directories
SNAKE_GAME_DIR = snake_game
INCLUDE_DIR = $(SNAKE_GAME_DIR)/include
SCRIPTS_DIR = $(SNAKE_GAME_DIR)/scripts
# PYBIND_INCLUDE = pybind11/include # This line is likely not needed and can be removed
BUILD_DIR = build

# Create build directory if it doesn't exist
$(shell mkdir -p $(BUILD_DIR))

# Source files
SOURCES = $(SCRIPTS_DIR)/Agent.cpp \
          $(SCRIPTS_DIR)/Apple.cpp \
          $(SCRIPTS_DIR)/Snake.cpp \
          $(SCRIPTS_DIR)/State.cpp \
          pybind.cpp

# Object files (in build directory)
OBJECTS = $(patsubst %.cpp,$(BUILD_DIR)/%.o,$(notdir $(SOURCES)))

# VPATH helps make find source files
VPATH = $(SCRIPTS_DIR):$(dir pybind.cpp)

# Library name
TARGET = snake_lib.so

# Default target
all: $(TARGET)

# Rule to build the shared library
$(TARGET): $(OBJECTS)
	# For Linux, remove -undefined dynamic_lookup. Explicitly link to libpython if needed.
	# The $(PYTHON_LDFLAGS) should usually handle linking to libpython.
	$(CXX) -shared $^ -o $@ $(PYTHON_LDFLAGS)

# Rule to compile source files from scripts directory
$(BUILD_DIR)/%.o: %.cpp
	# $(PYTHON_INCLUDES) already provides pybind11 paths
	$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIR) $(PYTHON_INCLUDES) -c $< -o $@

# Clean target
clean:
	rm -rf $(BUILD_DIR) $(TARGET)

# Rebuild target
rebuild: clean all

# Phony targets
.PHONY: all clean rebuild



# # Makefile for Snake Game Python-C++ binding

# # Compiler settings
# CXX = g++
# CXXFLAGS = -std=c++17 -fPIC -Wall -O2

# # Python configuration
# # PYTHON = python3.11
# PYTHON = python3.10
# PYTHON_CONFIG = $(PYTHON)-config
# PYTHON_INCLUDES = $(shell $(PYTHON) -m pybind11 --includes)
# PYTHON_LDFLAGS = $(shell $(PYTHON_CONFIG) --ldflags)

# # Directories
# SNAKE_GAME_DIR = snake_game
# INCLUDE_DIR = $(SNAKE_GAME_DIR)/include
# SCRIPTS_DIR = $(SNAKE_GAME_DIR)/scripts
# PYBIND_INCLUDE = pybind11/include
# BUILD_DIR = build

# # Create build directory if it doesn't exist
# $(shell mkdir -p $(BUILD_DIR))

# # Source files
# SOURCES = $(SCRIPTS_DIR)/Agent.cpp \
#           $(SCRIPTS_DIR)/Apple.cpp \
#           $(SCRIPTS_DIR)/Snake.cpp \
#           $(SCRIPTS_DIR)/State.cpp \
#           pybind.cpp

# # Object files (in build directory)
# OBJECTS = $(patsubst %.cpp,$(BUILD_DIR)/%.o,$(notdir $(SOURCES)))

# # VPATH helps make find source files
# VPATH = $(SCRIPTS_DIR):$(dir pybind.cpp)

# # Library name
# TARGET = snake_lib.so

# # Default target
# all: $(TARGET)

# # Rule to build the shared library
# $(TARGET): $(OBJECTS)
# 	$(CXX) -shared -undefined dynamic_lookup $^ -o $@ $(PYTHON_LDFLAGS)

# # Rule to compile source files from scripts directory
# $(BUILD_DIR)/%.o: %.cpp
# 	$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIR) -I$(PYBIND_INCLUDE) $(PYTHON_INCLUDES) -c $< -o $@

# # Clean target
# clean:
# 	rm -rf $(BUILD_DIR) $(TARGET)

# # Rebuild target
# rebuild: clean all

# # Phony targets
# .PHONY: all clean rebuild