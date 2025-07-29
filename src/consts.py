import pathlib


N_SNAKES = 2
N_APPLES = 5
BOARD_WIDTH = 10
BOARD_HEIGHT = 10


# PROJECT_PATH = pathlib.Path("/Users/szymon/Documents/Bachelor-Thesis")
PROJECT_PATH = pathlib.Path("/root/Bachelor-Thesis")
NANOGPT_DIR = PROJECT_PATH / pathlib.Path("src/training/nanoGPT/")

# PYBIND
PYBIND_DIR = PROJECT_PATH / pathlib.Path("python_cpp_binding/")


# CORPORA PATHS
CORPORA_DELIMETER = "=================================================="
CORPORA_DIR = PROJECT_PATH / pathlib.Path("src/training/corpora/")
RAW_DATA_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history20k.txt")
RAW_DATA_TAILS_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history20k_tails.txt")
RAW_DATA_TAILS_MCTS_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history20k_tails_mcts.txt")
RAW_TEST_DATA_100 = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history10.txt")
RAW_DATA_MINIMAX_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history_minimax20k.txt")



# MODEL CONSTS
TRAIN_VAL_SPLIT = 0.9
GAMES_IN_RAW_FILE = 20001

# CORPORA NAMES
STANDARD = "standard"
APPLES_CORPORA = "apples_corpora"
NO_TAILS = "no_tails_corpora"
MINIMAL = "minimal_corpora"