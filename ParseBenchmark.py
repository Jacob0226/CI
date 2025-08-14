import json
import csv
import argparse
import os
import re
import numpy as np
from utils import bench_types, models, log_files_prefix_Llama_8B_70B, log_file_prefix_Llama4_Scout, GetMetrics


def CheckFileName(log_file, target_log_files):
    for target_log_file in target_log_files:
        if target_log_file in log_file: # e.g., log_file=i32_o32_c16_p3000_iter1.log
            return True, target_log_file
    return False, None

def process_logs_in_folder(args):
    # folders under args.folder
    engine_folders = [os.path.join(args.folder, bt) for bt in bench_types]
    
    with open(args.json_file, "r") as f:
        data = json.load(f)
    data["Benchmark"] = {}
    
    for engine_folder in engine_folders:
        bench_type = engine_folder.split('/')[-1]
        data["Benchmark"][bench_type] = {}
        if os.path.exists(engine_folder) == False:
            print(f"[{bench_type}] Benchmark folder {engine_folder} deos not existed, skip...")
            continue
        
        for model in models:
            data["Benchmark"][bench_type][model] = {}
            engine_model_folder = os.path.join(engine_folder, model)
            if os.path.exists(engine_model_folder) == False:
                print(f"  Model folder {engine_model_folder} deos not existed, skip...")
                continue
            
            # Init empty 
            if model == "meta-llama_Llama-3.1-8B-Instruct" or model == "meta-llama_Llama-3.3-70B-Instruct":
                log_files_prefix = log_files_prefix_Llama_8B_70B
            else: 
                log_files_prefix = log_file_prefix_Llama4_Scout
            metrics=GetMetrics(engine_folder)
            results={}
            for filename in log_files_prefix:
                results[filename] = {metric: [] for metric in metrics}

            # List all files. e.g., i32_o32_c16_p3000_iter1.log, i32_o32_c64_p3000_iter1.log ...
            log_files = [os.path.join(engine_model_folder, f) for f in os.listdir(engine_model_folder)]

            # Parse performance numbers from logs
            for log_file in log_files:
                check, target = CheckFileName(log_file, log_files_prefix)
                if check:
                    with open(log_file, 'r') as file:
                        for line in file:
                            for metric in metrics:
                                if metric in line:
                                    try: 
                                        value = float(line.split()[-1]) # e.g., "Output token throughput (tok/s):         543.82  "
                                        results[target][metric].append(value)
                                    except (ValueError, IndexError) as e:
                                        print(f"Skip this file {log_file} due to error: {e}")
            
            # Average
            for config_name, metric_values in results.items():
                data["Benchmark"][bench_type][model][config_name]={}
                for metric in metrics:
                    value_list = metric_values[metric]
                    if len(value_list)==0:
                        average=0
                    else:
                        average = np.mean(value_list)
                    data["Benchmark"][bench_type][model][config_name][metric]=average
    
    with open(args.json_file, "w") as f:
        json.dump(data, f, indent=4)
        print(f"Benchmark numbers are saved successfully to '{args.json_file}'.")

    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process JSON log files from a folder and create a CSV summary."
    )
    parser.add_argument("--json-file", type=str, required=True, help="Path to the save the benchmark result.")
    parser.add_argument("--folder", type=str, default=None, help="Folder of the benchmark logs")
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: Json file {args.json_file} doesn't exist.")
        print(f"ParseBenchmark.py failed.")
        exit()

    process_logs_in_folder(args)

'''
python3 $HOME/CI/ParseBenchmark.py \
    --json-file $HOME/CI/Result/2025-08-13/Result.json \
    --folder $HOME/CI/Result/2025-08-13/ 

python3 $HOME/CI/ParseBenchmark.py \
    --json-file $HOME/CI/Result/2025-08-12/Result.json \
    --folder $HOME/CI/Result/2025-08-12/ 
    

'''