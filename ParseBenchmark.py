import json
import csv
import argparse
import os
import re
import numpy as np

def CheckFileName(log_file, target_log_files):
    for target_log_file in target_log_files:
        if target_log_file in log_file: # e.g., log_file=i32_o32_c16_p3000_iter1.log
            return True, target_log_file
    return False, None

def GetMetrics(folder):
    if "SGLang" in folder:
        metrics = [
            "Output token throughput (tok/s)",
            "Mean TTFT (ms)",
            "Mean E2E Latency (ms)", # SGLang
            "Mean ITL (ms)",  
        ]
    else: # "vLLM" in folder:
        metrics = [
            "Output token throughput (tok/s)",
            "Mean TTFT (ms)",
            "Mean E2EL (ms)",
            "Mean ITL (ms)",  
        ]
    return metrics

def process_logs_in_folder(args):
    log_files_prefix_Llama_8B_70B = [
        "i32_o32_c16_p3000",
        "i32_o32_c64_p3000",
        "i32_o32_c256_p3000",
        "i128_o128_c16_p3000",
        "i128_o128_c64_p3000",
        "i128_o128_c256_p3000",
        "i1024_o64_c16_p3000",
        "i1024_o64_c64_p3000",
        "i1024_o64_c256_p3000",
        "i2048_o128_c16_p1000",
        "i2048_o128_c64_p1000",
        "i2048_o128_c256_p1000",
    ]

    log_file_prefix_Llama4_Scout= [
        "i120000_o128_c4_p8",
        "i240000_o128_c4_p8",
        "i480000_o128_c4_p8",
        "i960000_o128_c4_p8",
        # "i1400000_o128_c4_p8",
    ]


    
    # folders under args.folder
    engine_folders = [
        os.path.join(args.folder, "vLLM_ray"),
        os.path.join(args.folder, "vLLM_standalone"),
        os.path.join(args.folder, "SGLang_ray"),
        os.path.join(args.folder, "SGLang_standalone"),
    ]

    models = [
        "meta-llama_Llama-3.1-8B-Instruct",
        "meta-llama_Llama-3.3-70B-Instruct",
        "meta-llama_Llama-4-Scout-17B-16E-Instruct",
    ]
    
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
                data["Benchmark"][bench_type][config_name]={}
                for metric in metrics:
                    value_list = metric_values[metric]
                    if len(value_list)==0:
                        average=0
                    else:
                        average = np.mean(value_list)
                    data["Benchmark"][bench_type][config_name][metric]=average
    
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
python $HOME/CI/ParseBenchmark.py \
    --json-file $HOME/CI/Result/2025-08-12/Result.json \
    --folder $HOME/CI/Result/2025-08-12/ 
    

'''