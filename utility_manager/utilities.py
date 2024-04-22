# utilities.py

from pathlib import Path

def check_and_create_directory(dir_name:str, dir_parent:str="") -> None:
    """
    Create a directory in its parent directory (optional)

    Parameters
    -----------------------
    dir_name: str,
        directory to be created
    dir_parent: str,
        parent directory in which to create the directory
    """

    path_directory = ""
    path_directory = Path(dir_parent) / dir_name if dir_parent else Path(dir_name)
    if not path_directory.exists():
        path_directory.mkdir(parents=True, exist_ok=True)
        print(f"The directory '{dir_name}' has been created successfully")
    else:
        print(f"The directory '{dir_name}' already exists")


def script_info(file_name:str) -> tuple: 
    """
    Returns information about the script being considered in the application log

    Parameters
    -----------------------
    file_name: str,
        script filename

    Returns
    -----------------------
    file path, file name
    """

    # Create a Path object from the file_name
    file_path = Path(file_name)

    # Ensure the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The specified file does not exist: {file_name}")
    
    # Get absolute path of the file
    script_path = str(file_path.resolve())
    
    # Get the base name of the file
    script_name = file_path.name
    
    return script_path, script_name