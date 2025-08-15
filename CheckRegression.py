import json
import argparse
import os
import sys
from datetime import datetime
import numpy as np
from utils import bench_types, models, \
    log_files_prefix_Llama_8B_70B, log_file_prefix_Llama4_Scout, metric_mapping, GetMetrics
import logging

logger = logging.getLogger("check_regression_logger")
logger.setLevel(logging.DEBUG)  
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def CheckAccuracy(cur_acc: dict, pre_acc: dict, threshold):
    engines = ["vLLM", "SGLang"]

    for engine in engines:
        if engine in cur_acc and engine in pre_acc:
            for model in models:
                if model in cur_acc[engine] and model in pre_acc[engine]:
                    diff = (cur_acc[engine][model] - pre_acc[engine][model]) / pre_acc[engine][model]
                    if diff < - threshold:
                        logger.warning(f"[{engine}] {model} Seeing a accuracy regression.")
                else:
                    logger.warning(f"[{engine}] {model} accuracy in not in json file.")

def CheckBenchmark(cur_bench: dict, pre_bench: dict, threshold):
    tput_diff_8B_70B = []
    ttft_diff_8B_70B = []
    tput_diff_Scout = []
    ttft_diff_Scout = []
    def CheckValue(data: dict, metrics: list):
        for metric in metrics:
            if metric not in data:
                return False
            if data[metric] == 0:
                return False
        return True

    # Calculate the changes
    for bt in bench_types:
        if bt in cur_bench and bt in pre_bench:
            metrics=GetMetrics(bt)
            for model in models:
                if model in cur_bench[bt] and model in pre_bench[bt]:
                    model_8B_70B = ("meta-llama_Llama-3.1-8B-Instruct", "meta-llama_Llama-3.3-70B-Instruct")
                    configs = log_files_prefix_Llama_8B_70B if model in model_8B_70B else log_file_prefix_Llama4_Scout
                    tput_list, ttft_list = (
                        (tput_diff_8B_70B, ttft_diff_8B_70B)
                        if model in model_8B_70B
                        else (tput_diff_Scout, ttft_diff_Scout)
                    )

                    for config in configs:
                        if config in cur_bench[bt][model] and config in pre_bench[bt][model]:
                            # Check metrics are saved correctly and non zero value
                            pass_cur = CheckValue(cur_bench[bt][model][config], metrics)
                            pass_pre = CheckValue(pre_bench[bt][model][config], metrics)
                            if pass_cur and pass_pre:
                                tput = metric_mapping["tput"]
                                diff = (cur_bench[bt][model][config][tput] - pre_bench[bt][model][config][tput]) / pre_bench[bt][model][config][tput]
                                tput_list.append(diff)

                                ttft = metric_mapping["ttft"]
                                diff = (cur_bench[bt][model][config][ttft] - pre_bench[bt][model][config][ttft]) / pre_bench[bt][model][config][ttft]
                                ttft_list.append(diff)
    
    # Validate regression
    tput_diff_8B_70B = []
    ttft_diff_8B_70B = []
    tput_diff_Scout = []
    ttft_diff_Scout = []
    tput_mean_8B_70B_pct = (0 if len(tput_diff_8B_70B) == 0 else np.mean(tput_diff_8B_70B)) * 100
    ttft_mean_8B_70B_pct = (0 if len(ttft_diff_8B_70B) == 0 else np.mean(ttft_diff_8B_70B)) * 100
    logger.debug(f"[Regression Test] Llama-8B+70B TPUT changes: {tput_mean_8B_70B_pct}%, threshold=-{threshold}%")
    logger.debug(f"[Regression Test] Llama-8B+70B TTFT changes: {ttft_mean_8B_70B_pct}%, threshold=-{threshold}%")

    tput_mean_Scout_pct = (0 if len(tput_diff_Scout) == 0 else np.mean(tput_diff_Scout)) * 100
    ttft_mean_Scout_pct = (0 if len(ttft_diff_Scout) == 0 else np.mean(ttft_diff_Scout)) * 100
    logger.debug(f"[Regression Test] Llama-Scout TPUT changes: {tput_mean_Scout_pct}%, threshold=-{threshold}%")
    logger.debug(f"[Regression Test] Llama-Scout TTFT changes: {ttft_mean_Scout_pct}%, threshold=-{threshold}%")
                 


def main(args):
    # Load the current benchmark JSON
    with open(args.json_file, "r") as f:
        cur_data = json.load(f)
    # Load the most recent benchmark JSON
    if not os.path.isdir(args.result_folder):
        print(f"Error: Directory '{args.result_folder}' not found.")
        exit()

    folders = [f for f in os.listdir(args.result_folder) if os.path.isdir(os.path.join(args.result_folder, f))]
    date_folders = []
    for f in folders:
        try:
            if args.exclude_date in f:
                continue
            date_obj = datetime.strptime(f, "%Y-%m-%d")
            date_folders.append((date_obj, f))
        except ValueError:
            continue  # Ignore folders which are not named in data format
    
    if not date_folders: # No previous data so exit the script
        sys.exit(0)
    
    previous_folder = max(date_folders, key=lambda x: x[0])[1]
    previous_json = os.path.join(args.result_folder, previous_folder, "Result.json")
    if not os.path.exists(previous_json):
        print(f"Error: Directory '{previous_json}' not found.")
        exit()
    with open(previous_json, "r") as f:
        pre_data = json.load(f)
    
    CheckAccuracy(cur_data["Accuracy"], pre_data["Accuracy"], args.threshold)
    CheckBenchmark(cur_data["Benchmark"], pre_data["Benchmark"], args.threshold)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file", type=str, required=True, help="Path to the save the benchmark result.")
    parser.add_argument("--result-folder", type=str, required=True, help="The 'root' of the benchmark folder")
    parser.add_argument("--exclude-date", type=str, required=True, help="Exclude the current benchmark folder")
    parser.add_argument("--threshold", type=float, default=3, help="The threshold of performance change in %.")
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"Error: Json file {args.json_file} doesn't exist.")
        print(f"CheckRegression.py failed.")
        exit()

    main(args)

'''
python $HOME/CI/CheckRegression.py \
    --json-file $HOME/CI/Result/2025-08-13/Result.json \
    --result-folder $HOME/CI/Result/ \
    --exclude-date 2025-08-13

'''