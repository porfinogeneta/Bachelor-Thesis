import pathlib

PROJECT_PATH = pathlib.Path("/Users/szymon/Documents/Bachelor-Thesis")
# PROJECT_PATH = pathlib.Path("/home/ubuntu/Bachelor-Thesis")
NANOGPT_DIR = PROJECT_PATH / pathlib.Path("src/training/nanoGPT/")

# PYBIND
PYBIND_DIR = PROJECT_PATH / pathlib.Path("python_cpp_binding/")


# CORPORA PATHS
CORPORA_DELIMETER = "=================================================="
CORPORA_DIR = PROJECT_PATH / pathlib.Path("src/training/corpora/")
RAW_DATA_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history20k.txt")
RAW_TEST_DATA_100 = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history10.txt")



# MODEL CONSTS
TRAIN_VAL_SPLIT = 0.9
GAMES_IN_RAW_FILE = 20001

# CORPORA NAMES
STANDARD = "standard"
APPLES_CORPORA = "apples_corpora"
NO_TAILS = "no_tails_corpora"