import csv
import json
import os
from datetime import datetime
import argparse
from utils import bench_types, models, overview_files, row_mapping_acc, row_mapping_8B, row_mapping_70B, row_mapping_Scout
import shutil
import logging
import sys

logger = logging.getLogger("save_overview_logger")
logger.setLevel(logging.DEBUG)  
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_nested_value(data: dict, json_key_layer: list):
    current_level = data
    for key in json_key_layer:
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        else:
            # if key not exist, return 0
            # logger.warning(f"[SaveOverviewCSV.py] No key {key} found in {current_level}, json_key_layer={json_key_layer}")
            return 0
    return current_level

def CheckDate(csv_lines: list, date_str: str, overview_file: str):
    for i, row in enumerate(csv_lines):
        if row and row[0] == "Date":
            try:
                date_col_index = row.index(date_str)
                logger.debug(f"[SaveOverviewCSV.py] {date_str} already in {overview_file}, overwrite it.")
            except ValueError: # date_str doesn't exist in row
                # Only save the newer data so checking the last date is older than current one.
                if len(row) > 1 and row[-1] != "":
                    latest_date_str = row[-1]
                    latest_date = datetime.strptime(row[-1], "%Y-%m-%d")
                    new_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if new_date < latest_date:
                        logger.warning(f"[SaveOverviewCSV.py] The date '{date_str}' is older than the latest date '{latest_date_str}'. {overview_file} Aborting.")
                        return -1

                csv_lines[i].append(date_str)
                date_col_index = len(csv_lines[i]) - 1
            break  

    if date_col_index == -1:
        logger.warning(f"Error: 'Date' row not found in the {overview_file}. Aborting.")
        return -1
    return date_col_index


def SaveAccuracyOverview(csv_lines: list, data: dict, date_str: str, overview_file: str):
    # Setup date
    date_col_index = CheckDate(csv_lines, date_str, overview_file)
    if date_col_index == -1:
        return
    
    # Fill the accuracy numbers
    for name, row, json_key_layer in row_mapping_acc:
        value = get_nested_value(data, json_key_layer)
        row = int(row)

        while len(csv_lines[row]) <= date_col_index:
            csv_lines[row].append("")
        csv_lines[row][date_col_index] = value

def Save_8B_70B_Overview(csv_lines: list, data: dict, date_str: str, overview_file: str, is_8B: bool):
    date_col_index = CheckDate(csv_lines, date_str, overview_file)
    if date_col_index == -1:
        return
    
    # Fill the accuracy numbers
    row_mapping = row_mapping_8B if is_8B else row_mapping_70B
    for name, row, json_key_layer in row_mapping:
        value = get_nested_value(data, json_key_layer)
        row = int(row)

        while len(csv_lines[row]) <= date_col_index:
            csv_lines[row].append("")
        csv_lines[row][date_col_index] = value

def Save_Scout_Overview(csv_lines: list, data: dict, date_str: str, overview_file: str):
    # Setup date
    date_col_index = CheckDate(csv_lines, date_str, overview_file)
    if date_col_index == -1:
        return
    
    # Fill the accuracy numbers
    for name, row, json_key_layer in row_mapping_Scout:
        value = get_nested_value(data, json_key_layer)
        row = int(row)

        while len(csv_lines[row]) <= date_col_index:
            csv_lines[row].append("")
        csv_lines[row][date_col_index] = value

def main(args):
    with open(args.json_file, "r") as f:
        data = json.load(f)
    date_str = args.json_file.split('/')[-2] # e.g., $HOME/CI/Result/2025-08-12/Result.json 

    # Check if the overview files exist
    for overview_file in overview_files:
        if not os.path.exists(overview_file):
            print(f"{overview_file} doesn't exist. Copy an empty template from the folder ./template")
            source_file = f"template/{overview_file}"
            destination_file = "overview_file"
            shutil.copyfile(source_file, overview_file)
        
        with open(overview_file, 'r', newline='') as f:
            reader = csv.reader(f)
            csv_lines = list(reader)
            # print(f"{overview_file}\n {csv_lines}")
        
        if "accuracy" in overview_file:
            SaveAccuracyOverview(csv_lines, data, date_str, overview_file)
        elif "8B" in overview_file:
            Save_8B_70B_Overview(csv_lines, data, date_str, overview_file, is_8B=True)
        elif "70B" in overview_file:
            Save_8B_70B_Overview(csv_lines, data, date_str, overview_file, is_8B=False)
        elif "Scout" in overview_file:
            Save_Scout_Overview(csv_lines, data, date_str, overview_file)
        
        with open(overview_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file", type=str, required=True, help="Path to the save the benchmark result.")
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: Json file {args.json_file} doesn't exist.")
        print(f"SaveOverviewCSV.py failed.")
        exit()

    main(args)
    

'''
python $HOME/CI/SaveOverviewCSV.py --json-file $HOME/CI/Result/2025-08-12/Result.json 

python $HOME/CI/SaveOverviewCSV.py --json-file $HOME/CI/Result/2025-08-11/Result.json 

python $HOME/CI/SaveOverviewCSV.py --json-file $HOME/CI/Result/2025-08-13/Result.json 

python $HOME/CI/SaveOverviewCSV.py --json-file $HOME/CI/Result/2025-08-14/Result.json 
'''