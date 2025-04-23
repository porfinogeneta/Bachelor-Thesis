#!/usr/bin/env python3
import subprocess
import argparse
import os
from tqdm import tqdm

def run_cpp_program(executable_path, output_file, flags=None, iterations=1, delimiter=None):
    """
    Run a compiled C++ program multiple times with the given flags and save output to a file.
    
    Args:
        executable_path (str): Path to the compiled C++ executable
        output_file (str): Path to the output file
        flags (list): Command-line flags to pass to the executable
        iterations (int): Number of times to run the program
        delimiter (str): Custom delimiter to use between executions (default: timestamp-based)
    """
    # Validate executable exists
    if not os.path.isfile(executable_path):
        raise FileNotFoundError(f"Executable not found: {executable_path}")
    
    # Make sure executable has execute permissions
    if not os.access(executable_path, os.X_OK):
        print(f"Warning: {executable_path} may not have execute permissions. Attempting to add them.")
        try:
            os.chmod(executable_path, 0o755)
        except Exception as e:
            print(f"Failed to add execute permissions: {e}")
    
    # Prepare the command
    cmd = [executable_path]
    if flags:
        cmd.extend(flags)
    
    # Default delimiter if none provided
    if delimiter is None:
        delimiter = f"\n{'=' * 50}\n"
    else:
        delimiter = f"\n{delimiter}\n"
    
    # Open output file
    with open(output_file, 'w') as f:
        for i in tqdm(range(iterations)):
            # Write delimiter before each execution (except the first if requested)
            if i > 0 or i == 0 and delimiter.strip():
                f.write(delimiter.format(i + 1))
                f.flush()
            
            # Run the program and capture output
            try:
                # # Print command being executed for debugging
                # print(f"Running: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                      text=True, check=False)
                f.write(result.stdout)
                
                # # Also write return code
                # f.write(f"\nReturn Code: {result.returncode}\n")
                f.flush()
                
                # print(f"Execution {i + 1}/{iterations} completed with return code {result.returncode}")
                
            except Exception as e:
                error_msg = f"Error executing program: {e}\n"
                f.write(error_msg)
                print(error_msg)

        f.write(f'{delimiter}')


# TO RUN
# python3 src/training/generate_data.py /Users/szymon/Documents/Bachelor-Thesis/data_creation/generation/snake_game_generation /Users/szymon/Documents/Bachelor-Thesis/src/training/raw_state_history.txt -i 30 --cpp-args -h
def main():
    parser = argparse.ArgumentParser(description='Run a C++ program multiple times and save output')
    parser.add_argument('executable', help='Path to the compiled C++ executable')
    parser.add_argument('output', help='Path to the output file')
    parser.add_argument('--cpp-args', nargs=argparse.REMAINDER, help='Arguments to pass to the C++ executable (include flags like -v and -h here)')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='Number of times to run the program')
    parser.add_argument('-d', '--delimiter', help='Custom delimiter between executions')
    
    args = parser.parse_args()
    
    # Run the program
    try:
        run_cpp_program(
            args.executable,
            args.output,
            args.cpp_args,
            args.iterations,
            args.delimiter
        )
        print(f"Output saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())