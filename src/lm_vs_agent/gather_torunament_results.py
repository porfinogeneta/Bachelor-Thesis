import pathlib
import re
import ast
from src.consts import PROJECT_PATH


def parse_model_name_details(model_name_str):
    """
    Parses the model name string to extract a simplified configuration name
    and a context value (typically the number after '_bs_').
    Example: "out_standard_positions_bs_64" -> context=64, config_name="standard"
             "out_aligned_games_bs_4372" -> context=4372, config_name="aligned"
    """
    parts = model_name_str.split('_')
    context_val = "Unknown"
    config_name_simplified = "Unknown"

    # Try to find "_bs_" pattern for batch size / context
    bs_pattern_match = re.search(r"_bs_(\w+)$", model_name_str)
    if bs_pattern_match:
        potential_context = bs_pattern_match.group(1)
        try:
            context_val = int(potential_context)
        except ValueError:
            context_val = potential_context # Keep as string if not an integer
        
        # Extract config name part before "_bs_"
        config_name_prefix = model_name_str.split('_bs_')[0]
        if config_name_prefix.startswith("out_"):
            config_name_simplified = config_name_prefix[len("out_"):] # Remove "out_"
        else:
            config_name_simplified = config_name_prefix

    elif parts[0] == "out" and len(parts) > 1: # Fallback if "_bs_" not found
        config_name_simplified = parts[1]
        # Try to see if the last part is numeric for context
        if len(parts) > 2:
            try:
                context_val = int(parts[-1])
            except ValueError:
                pass # Keep "Unknown" if last part isn't numeric
    
    # Further simplify config name if it contains "positions" or "games"
    if "standard_positions" in config_name_simplified:
        config_name_simplified = "standard"
    elif "aligned_games" in config_name_simplified:
        config_name_simplified = "aligned"

    return context_val, config_name_simplified

def sort_key_for_results(item):
    """
    Creates a sort key for an item from the results list.
    Sorts by: agent_type, sampling_bool, model_idx_val, then context.
    Contexts that are integers are sorted numerically; strings are sorted alphabetically after numbers.
    """
    context = item['derived_context']
    # Make context sortable: (0, int_value) for ints, (1, str_value) for strings
    sortable_context = (0, context) if isinstance(context, int) else (1, str(context))
    
    return (
        item['agent_type'],
        item['sampling_bool'],
        item['model_idx_val'],
        sortable_context 
    )

def main():
    # Define the base path where the tournament result directories are located.
    base_search_path = pathlib.Path("src/llm_vs_agent/tournaments")

    # --- Configuration from your script ---
    # Modify these lists to match the configurations you want to parse
    MODELS = [
        "out_standard_positions_bs_8",
        "out_standard_positions_bs_32", 
        "out_standard_positions_bs_64", 
        "out_standard_positions_bs_1600", 
        "out_standard_positions_bs_8000"
    ]
    # MODELS = ["out_aligned_games_bs_4372", "out_standard_positions_bs_64"] 

    AGENTS = ["bfs", "random"]
    VALID = ["valid", "invalid"] 
    MODEL_IDX = [0, 1]
    # ------------------------------------

    all_results_data = []

    for model_name in MODELS:
        for agent_type in AGENTS:
            for do_sample_status in VALID: 
                for model_idx_val in MODEL_IDX:
                    
                    current_config_path = PROJECT_PATH / base_search_path / model_name / agent_type / do_sample_status / f"model_idx_{model_idx_val}"
                    output_file = current_config_path / "tournaments_results.txt"

                    # Prepare data structure for this configuration
                    derived_context, derived_config_name = parse_model_name_details(model_name)
                    sampling_bool = True if do_sample_status == "valid" else False

                    result_entry = {
                        'file_path': output_file,
                        'model_name': model_name,
                        'agent_type': agent_type,
                        'do_sample_status': do_sample_status,
                        'model_idx_val': model_idx_val,
                        'derived_context': derived_context,
                        'derived_config_name': derived_config_name,
                        'sampling_bool': sampling_bool,
                        'first_line_data_str': "N/A",
                        'first_line_parsed': None,
                        'bad_generations_count': "N/A",
                        'status_message': ""
                    }

                    if not output_file.exists():
                        result_entry['status_message'] = "File not found."
                        all_results_data.append(result_entry)
                        continue
                    
                    try:
                        with open(output_file, 'r') as f:
                            lines = f.readlines()
                        
                        if lines:
                            first_line_data_str_temp = lines[0].strip()
                            result_entry['first_line_data_str'] = first_line_data_str_temp
                            try:
                                result_entry['first_line_parsed'] = ast.literal_eval(first_line_data_str_temp)
                            except (ValueError, SyntaxError) as e:
                                result_entry['status_message'] = f"Warning: Could not parse first line as dict: {e}"
                                # Keep first_line_parsed as None, but store raw string
                        else:
                            result_entry['status_message'] = "Warning: File is empty."
                            result_entry['first_line_data_str'] = "File is empty."

                        file_content = "".join(lines)
                        match = re.search(r"BAD GENERATIONS:\s*(\d+)", file_content)
                        if match:
                            result_entry['bad_generations_count'] = int(match.group(1))
                        else:
                            match_alt = re.search(r"incorrect_generations':\s*(\d+)\}", file_content)
                            if match_alt:
                                result_entry['bad_generations_count'] = f"{int(match_alt.group(1))} (from incorrect_generations in summary line)"
                            else:
                                result_entry['bad_generations_count'] = "Not found in file."
                        
                        if not result_entry['status_message']: # If no warnings so far
                             result_entry['status_message'] = "Processed successfully."

                    except Exception as e:
                        result_entry['status_message'] = f"Error reading or processing file: {e}"
                    
                    all_results_data.append(result_entry)

    # Sort the collected data
    sorted_results = sorted(all_results_data, key=sort_key_for_results)

    # Print the sorted results
    if not sorted_results:
        print("No data found for the specified configurations.")
        print(f"Please ensure that the base path '{base_search_path}' is correct and contains the expected subdirectories.")
    else:
        for item in sorted_results:
            print(f"--- Configuration & Results ---")
            print(f"File Path: {item['file_path']}")
            print(f"Status: {item['status_message']}")
            
            # Print details only if successfully processed or has data
            if item['status_message'] == "Processed successfully." or item['first_line_parsed'] or item['bad_generations_count'] not in ["N/A", "Not found in file."]:
                print(f"context: {item['derived_context']}")
                print(f"against: {item['agent_type']}")
                print(f"configuration: {item['derived_config_name']}") # e.g. "standard", "aligned"
                print(f"sampling: {item['sampling_bool']}")
                print(f"model_idx: {item['model_idx_val']}")
                
                print("--- Extracted Scores ---")
                if item['first_line_parsed'] and isinstance(item['first_line_parsed'], dict):
                    print(f"First line data: {item['first_line_parsed']}")
                    if 'incorrect_generations' in item['first_line_parsed']:
                        print(f"Total incorrect generations (from first line dict): {item['first_line_parsed']['incorrect_generations']}")
                elif item['first_line_data_str'] not in ["N/A", "File is empty."]:
                     print(f"First line raw: {item['first_line_data_str']}")

                print(f"Bad Generations (from end of file): {item['bad_generations_count']}")
            print("--------------------------------\n")

if __name__ == "__main__":
    main()