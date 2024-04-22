# 02_downloader.py
# DOWNLOADER: from the CSV execute the wget and save it

### IMPORT ### 
from datetime import datetime
import pandas as pd
from pathlib import Path
import requests
import sys 

### LOCAL IMPORT ###
from config.config_reader import read_config_yaml
from utility_manager.utilities import check_and_create_directory, script_info

### GLOBALS ###
yaml_config = read_config_yaml()
verdict_dir = str(yaml_config["VERDICTS_DIR"])
verdict_cols = ["sentenza_url", "sentenza_file"] # columns needed from CSV
verdict_file_name = str(yaml_config["VERDICTS_FILE"])

script_path, script_name = script_info(__file__)

# INPUT
year_start = None
year_end = None

def data_load(verdict_dir: str, file_name: str, delimiter: str, usecols:list, remove_duplicates: bool) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame using specified columns.
    
    Args:
        file_name (str): Name of the CSV file.
        sentence_dir (str): Directory where the CSV file is stored.
        delimiter (str): Delimiter used in the CSV file. Default is ";".
        usecols (list): List of columns to use. Default is None.
        remove_duplicates (bool): Flag to remove duplicate rows. Default is False.
    
    Returns:
        pd.DataFrame: A DataFrame loaded with specified columns from the CSV file.
    """
    path_input = Path(verdict_dir) / file_name
    
    try:
        input_df = pd.read_csv(path_input, delimiter=delimiter, usecols=usecols)
    except Exception as e:
        print(f"Failed to read the CSV file '{file_name}': {e}")
        return pd.DataFrame()  # Return empty DataFrame or re-raise exception depending on your use case
    

    if remove_duplicates:
        duplicate_count = input_df.duplicated().sum()
        if duplicate_count > 0:
            print(f"Rows duplicated (to be deleted): {duplicate_count}")
            input_df = input_df.drop_duplicates()

    return input_df

def data_show(input_df:pd.DataFrame) -> None:
    """ 
    Given a pandas Dataframe, show the data inside of it
    
    Args:
        input_df (pd.DataFrame): the dataframe object
    
    Returns:
        None
    """
    
    if len(input_df) == 0:
        print("Empty dataframe")
        return
    print("Dataframe length (rows):", len(input_df)) # Show number of rows
    print("Dataframe shape (rows, cols):", input_df.shape) # Show rows,cols number
    print("Dataframe columns:", input_df.columns) # Show columns (features)
    print(input_df.head()) # Show first 10 rows
    print("...")
    print(input_df.tail()) # Show last 10 rows
    print()
    return

def get_sentence_file(url_download, file_download, year, verdict_dir):
    """
    Download the sentence file if it does not already exist in the specified directory.

    Args:
        url_download (str): URL from which to download the file.
        file_download (str): Name of the file to download.
        year (int or str): Year to categorize the file under.
        verdict_dir (str): Base directory to store the files.
        
    Returns:
        bool: True if a new file was downloaded, False if the file was already present.
    """
    path_file = Path(verdict_dir) / str(year) / file_download
    path_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    if not path_file.exists():  # Check if the file already exists
        try:
            response = requests.get(url_download, verify=False)  # Security warning: verify should ideally be True
            response.raise_for_status()  # Raise an exception for HTTP errors
            with open(path_file, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded: {path_file}")
            return True
        except requests.RequestException as e:
            print(f"Failed to download the file: {e}")
            return False
    else:
        print(f"File already downloaded: {path_file}")
        return False

### MAIN ###
def main():
    print()
    print(f"*** PROGRAM START ({script_name}) ***")
    print()

    start_time = datetime.now().replace(microsecond=0)

    print("Start process:", start_time)
    print()

    print(">> Year input")
    if len(sys.argv) > 1:
        year_start = int(sys.argv[1])
        year_end = year_start + 1
        print("Value:", year_start)
    else:
        print("WARNING! Year input missing, quitting the program.")
        print(f"Use example: {script_name} 2023")
        print()
        quit()
    print()

    # OUTPUT
    file_downloaded = 0 # total file downloaded from the wget
    file_not_downloaded = 0 # total file already saved in file system

    for year in range(year_start, year_end):

        print(">> Loading data")
        file_input = verdict_file_name.replace("Y", str(year))
        print("Year:", year)
        print("File with verdicts index:", file_input)
        print()

        # create the directory for download
        print(">> Creating output directory")
        print(f"Creating '{verdict_dir}/{year}'")
        check_and_create_directory(str(year), verdict_dir)
        print()

        print(">> Reading the verdicts index")
        input_df = data_load(verdict_dir, file_input, ";", verdict_cols, True)
        print()

        print("Input DF:")
        data_show(input_df)
        print()

        n = len(input_df)

        i = 0

        print(">> Downloading data")
        for row in input_df.itertuples():
            print(f"[{i} / {n}] - year: {year}")
            url_download = row[1]
            file_donwload = row[2]
            print("URL:", url_download)
            print("File:", file_donwload)
            # get_sentence_file(url_download, file_donwload, year)
            downloaded = get_sentence_file(url_download, file_donwload, year, verdict_dir)
            if downloaded:
                file_downloaded+=1
                print("OK! Download was successful.")
            else:
                file_downloaded+=1
                print("WARNING! No download needed or error.")
            print()
            i+=1
    print()

    print(">> Download results")
    print("Files downloaded:", file_downloaded)
    print("Files not downloaded (error or already downloaded):", file_not_downloaded)
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
