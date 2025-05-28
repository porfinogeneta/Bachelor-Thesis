import pathlib

# PROJECT_PATH = pathlib.Path("/Users/szymon/Documents/Bachelor-Thesis")
PROJECT_PATH = pathlib.Path("/home/ubuntu/Bachelor-Thesis")
NANOGPT_DIR = PROJECT_PATH / pathlib.Path("src/training/nanoGPT/")

# PYBIND
PYBIND_DIR = PROJECT_PATH / pathlib.Path("python_cpp_binding/")


# CORPORA PATHS
CORPORA_DELIMETER = "=================================================="
CORPORA_DIR = PROJECT_PATH / pathlib.Path("src/training/corpora/")
RAW_DATA_20K = PROJECT_PATH / pathlib.Path("src/training/corpora/raw/raw_state_history20kp.txt")

