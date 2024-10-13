import os
import csv
from pprint import pprint
from typing import Optional, List, Dict


def find_last_modified_test_dir() -> Optional[str]:
    """_summary_
    Finds the last modified directory in the 'test/logs' folder.

    Returns:
        Optional[str]: The path of the last modified directory, 
        or None if no directories are found.
    """
    dirs = []
    test_data_directory = os.path.join("test","logs")
    
    # Iterate through all items in the base_directory
    for d in os.listdir(test_data_directory):
        dir_path = os.path.join(test_data_directory, d)
        # Check if the item is a directory and add to the list
        if os.path.isdir(dir_path):
            dirs.append(dir_path)
    
    if not dirs:
        return None 

    # Find the directory with the latest modification time
    last_modified_dir = max(dirs, key=os.path.getmtime)
    
    return last_modified_dir

def get_timestamped_lines() -> Optional[List[Dict[str, float]]]:
    """_summary_

    Returns:
        list[dict]: A list of dictionaries with line contents and duration
    """
    
    LATEST_LOG_PATH = find_last_modified_test_dir()
    if not LATEST_LOG_PATH:
        print("No test log directories found.")
        return None

    LATEST_DATA_CSV_PATH = os.path.join(LATEST_LOG_PATH, "uart_export.csv")
    
    if not os.path.exists(LATEST_DATA_CSV_PATH):
        print(f"File '{LATEST_DATA_CSV_PATH}' not found.")
        return None

    timestamped_lines = []
    
    with open(LATEST_DATA_CSV_PATH, "r") as r:
        reader = csv.reader(r)
        header = next(reader, None)
        if not header:
                print("Empty CSV file or no header row.")
                return None
        try:
            # Get the column indices
            DATA_COL = header.index("data")
            START_TIME_COL = header.index("start_time")
        except ValueError:
            print("Required columns 'data' or 'start_time' not found.")
            return None
        
        # Flag to avoid storing consecutive newlines
        last_newline = False
        # Current text line (seperated by newline)
        current_line = ""
        # The timestamp of when the last line finished
        last_line_timestamp = 0.0
        
        # Header row is skipped because the iterator has passed it previously
        for row in reader:
            # Add data collumn which is probably last row
            data = row[DATA_COL]
            if data not in "\n\r":
                current_line += data
                last_newline = False
            elif not last_newline:
                current_line_timestamp = float(row[START_TIME_COL])
                timestamped_lines.append({
                    "line":current_line,
                    "duration":current_line_timestamp-last_line_timestamp
                    })
                last_line_timestamp = current_line_timestamp
                current_line = ""
                last_newline = True
    return timestamped_lines
             

if __name__ == "__main__":
    # Now create a bunch of test objects using `ArduinoUnitTest.py`
    pprint(get_timestamped_lines())