# 03_analyzer.py
# Analyze the downloaded files

from datetime import datetime
import pandas as pd
from pathlib import Path
import json

### LOCAL IMPORT ###
from verdict import Verdict 
from config.config_reader import read_config_yaml
from utility_manager.utilities import check_and_create_directory, script_info
from collections import defaultdict

### GLOBALS ###
yaml_config = read_config_yaml()
verdict_dir = str(yaml_config["VERDICTS_DIR"])
verdict_stats_dir = str(yaml_config["VERDICTS_STATS"])
verdict_stats_file = str(yaml_config["VERDICTS_STATS_FILE"])
courts_dir = str(yaml_config["COURTS_DIR"])
courts_file = str(yaml_config["COURTS_FILE"])
script_path, script_name = script_info(__file__)

# dictionaries of the files found
court_dic = {}
year_dic = {}
ext_dic = {}

# court info
court_dir = "court"
court_file = "court.csv"

### FUNCTIONS ###

def court_load(court_dir: str, court_file:str) -> list:
    """
    Loads the specified CSV file from court_dir and court_file and returns a list of the elements in the first column.
    
    Args:
        court_dir (str): The directory containing the file.
        court_file (str): The name of the file to load.

    Returns:
        list of elements from the first column of the CSV.
    """

    try:
        file_path = Path(court_dir) / court_file
        df = pd.read_csv(file_path)
        df_len = len(df)
        #print("DataFrame preview:")
        # print(df.head())
        # print(f"DataFrame length: {df_len}")
        return df.iloc[:, 0].tolist()
    except FileNotFoundError:
        print(f"The file '{court_file}' was not found in '{court_dir}'.")
        return []
    except Exception as e:
        print(f"An error occurred while loading the file '{court_file}': {e}")
        return []


def list_subdirectories(directory_path:str) -> list:
    """
    List all subdirectories in the specified directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        list: A list of paths to the subdirectories.
    """
    path = Path(directory_path)
    # Using the .iterdir() method to iterate through the directory contents
    # and the .is_dir() method to filter only directories
    subdirectories = [subdir for subdir in path.iterdir() if subdir.is_dir()]
    return subdirectories

def count_file_extensions(directory_path:str, court_prefixes:list) -> dict:
    """
    Count file extensions in the given directory, exclude temporary MacOS files that start with '._',
    count files starting with specified court_prefixes, and include the total number of files. 
    The function returns a dictionary with the directory path, a sub-dictionary for extensions,
    the counts for specified court_prefixes, and the total file count.

    Args:
        directory_path (str): The path to the directory to search for files.
        court_prefixes (list): A list of string court_prefixes to count files that start with them.

    Returns:
        dict: A dictionary containing the directory path, a dictionary with extensions as keys and their counts as values,
        a dictionary with court_prefixes as keys and their counts as values, and the total number of files.
    """
    result = None
    path = Path(directory_path)
    extension_count = defaultdict(int)
    prefix_count = defaultdict(int)
    total_files = 0  # Initialize a counter for the total number of files
    
    # Iterate over all files in the directory using .rglob('*') to include all files
    for file in path.rglob('*'):
        # Check if the path is a file and not a MacOS temporary file
        if file.is_file() and not file.name.startswith('._'):
            total_files += 1  # Increment the total file counter
            # Get the file extension in lowercase and update the count
            extension = file.suffix[1:].lower()
            extension_count[extension] += 1
            # Count files starting with specified court_prefixes
            for prefix in court_prefixes:
                if file.name.startswith(prefix):
                    prefix_count[prefix] += 1

    # Prepare the result dictionary with the directory path, the extension counts, the prefix counts, and the total file count
    result = {
        "directory_path": str(path),
        "extensions": dict(extension_count),
        "court_counts": dict(prefix_count),
        "total_files": total_files
    }

    return result

def save_results_to_file(result:dict, output_directory:str, output_filename:str) -> int:
    """
    Save the results dictionary to a file in a specified directory as a JSON list.

    This function appends the given results dictionary to a file (specified by the output filename) within a given directory,
    formatted as a JSON list. If the file does not exist or is empty, it initializes a new list. Each entry is added as an element
    in the JSON list.
    
    Args:
        result (dict): The results dictionary to be saved.
        output_directory (str): The directory where the file will be saved.
        output_filename (str): The name of the file to which the results will be appended.

    Return:
        1 if done, else 0.
    """
    # Convert the dictionary to a JSON string
    result_json = json.dumps(result)
    # Ensure the directory exists, if not create it
    file_path = Path(output_directory) / output_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if the file exists and is not empty
    if file_path.exists() and file_path.stat().st_size > 0:
        # Read the existing data and append the new result
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                if isinstance(data, list):
                    data.append(result)
                else:
                    data = [result]
            except json.JSONDecodeError:
                data = [result]
    else:
        # Initialize a new list with the result
        data = [result]
    
    # Write the updated list back to the file
    with open(file_path, 'w') as fp:
        json.dump(data, fp, indent=4)
        return 1
    
    return 0

### MAIN ###
def main():
    print()
    print(f"*** PROGRAM START ({script_name}) ***")
    print()

    start_time = datetime.now().replace(microsecond=0)

    print("Start process:", start_time)
    print()

    print(">> Creating output directories")
    print(f"Creating '{verdict_stats_dir}' directory")
    check_and_create_directory(verdict_stats_dir)
    print()

    print(">> Loading courts")
    print("Verdicts directory:", court_dir)
    print("Verdicts file:", court_file)
    list_court = court_load(court_dir, court_file) # get the court list
    print("Courts found:")
    print(list_court)
    print()
    
    print(">> Loading verdict directories")
    verdicts_dir_list = list_subdirectories(verdict_dir)
    verdicts_dir_list_len = len(verdicts_dir_list)
    print("Verdict directories found:", verdicts_dir_list_len)
    print(verdicts_dir_list)
    print()


    print(">> Analysis of individual verdict directories")
    print()
    for v_dir in verdicts_dir_list:
        print("Verdict directory:", v_dir)
        dic_result_by_year = count_file_extensions(v_dir, list_court)
        print(dic_result_by_year)
        print("Total files in the directory:", dic_result_by_year["total_files"])
        ok = save_results_to_file(dic_result_by_year, verdict_stats_dir, verdict_stats_file)
        if ok == 1:
            print(f"OK! Result saved in '{verdict_stats_file}'")
        else:
            print(f"WARNING! Result not saved in '{verdict_stats_file}'")
        print()

    end_time = datetime.now().replace(microsecond=0)
    delta_time = end_time - start_time

    print("End process:", end_time)
    print("Time to finish:", delta_time)
    print()

    print()
    print("*** PROGRAM END ***")
    print()

if __name__ == "__main__":
    main()
