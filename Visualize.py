import csv
import json
import os
from datetime import datetime
import argparse
from utils import setup_logger, bench_types, models, overview_files, log_files_prefix_Llama_8B_70B, log_file_prefix_Llama4_Scout, \
    csv_row_overview_Acc, csv_row_overview_8B_70B, csv_row_overview_Scout
import shutil
import logging
import sys
import pandas as pd
import matplotlib.pyplot as plt

py_script = os.path.basename(sys.argv[0])
logger = setup_logger("save_overview_logger")

START=0
END=1

def plot_metrics(data, title, ylabel, filename):
    # 直接從 DataFrame 的索引中獲取配置列表
    configs = data.index.tolist() 
    fig, axes = plt.subplots(3, 4, figsize=(16, 10))
    fig.suptitle(title, fontsize=16)

    for i, config in enumerate(configs):
        row, col = divmod(i, 4)
        ax = axes[row, col]
        
        # 繪圖時直接使用 DataFrame 的數據
        # .iloc[:, 1:] 應該調整為 .iloc[:, :]
        # 因為 'Empty' column 已經被排除，並且我們只想繪製數值
        values = data.iloc[i].astype(float).tolist() 
        ax.plot(data.columns, values, marker='o') # 更改 x 軸為 DataFrame 的欄位名稱 (日期)
        
        ax.set_title(config)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Date")
        ax.set_ylim(0, 8000)
        ax.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(filename, dpi=300)
    plt.close()

def Plot_Accuracy(df: pd.DataFrame, title, csv_row_mapping: dict, out_dir: str):
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()  
    fig.suptitle(title, fontsize=20, y=1.0) 
    dates = df.iloc[0, 2:].dropna().tolist()
 
    plot_index = 0
    for group_title, model_dict in csv_row_mapping.items():
        for model, row in model_dict.items(): # E.g., "meta-llama_Llama-3.1-8B-Instruct": 3,
            # Get values
            values = df.iloc[row, 2:].astype(float).tolist()
            ax = axes[plot_index]
            ax.plot(dates, values, marker='o')
            
            # Setting figure
            ax.set_title(f"{group_title}\n{model}")
            ax.set_ylabel("Accuracy")
            ax.set_xlabel("Date")
            ax.set_ylim(0, 1)
            ax.grid(True)
            plot_index += 1
    
    img_name = os.path.join(out_dir, title + ".jpg")
    logger.info(f"[{py_script}] Saving {img_name}.")
    axes[5].set_visible(False) # Hide figure 6 as it is empty
    plt.savefig(img_name, dpi=300)
    plt.close()

def Plot_Benchmark(df: pd.DataFrame, title: str, csv_row_mapping: dict, out_dir: str):
    dates = df.iloc[0, 2:].dropna().tolist()
    if "Scout" in title:
        benchmark_labels = log_file_prefix_Llama4_Scout
        plot_row, plot_col = 1, 4
        plot_combinations = {
            "vLLM"  : ["vLLM_ray", "vLLM_standalone"],
            # "SGLang": ["SGLang_ray", "SGLang_standalone"], # ROCm SGLang haven't support Llama4
            }
    else:
        benchmark_labels = log_files_prefix_Llama_8B_70B
        plot_row, plot_col = 4, 3
        plot_combinations = {
            "vLLM"  : ["vLLM_ray", "vLLM_standalone"],
            "SGLang": ["SGLang_ray", "SGLang_standalone"],
        }

    # Go through plot_combinations
    for engine, local_bench_types in plot_combinations.items():
        fig, axes = plt.subplots(plot_row, plot_col, figsize=(plot_col*6, plot_row*6))
        axes = axes.flatten()  
        bench_title = "_".join([title, engine])
        fig.suptitle(bench_title, fontsize=20, y=1.0) 

        margin = 2000
        # Go through benchmark configs
        for i in range(len(benchmark_labels)):
            # Get data
            ray_tput_data = None
            ray_ttft_data = None
            standalone_tput_data = None
            standalone_ttft_data = None
            # Collect data
            for bench_type in local_bench_types:
                if bench_type not in csv_row_mapping:
                    logger.warning(f"[{py_script}] Benchmark type '{bench_type}' not found in overview csv. Skipping.")
                    continue

                tput_rows = csv_row_mapping[bench_type]["tput"]
                ttft_rows = csv_row_mapping[bench_type]["ttft"]


                tput_values = df.iloc[tput_rows[START] + i, 2:].astype(float).tolist()
                ttft_values = df.iloc[ttft_rows[START] + i, 2:].astype(float).tolist()
                
                if "ray" in bench_type:
                    ray_tput_data = tput_values
                    ray_ttft_data = ttft_values

                else:
                    standalone_tput_data = tput_values
                    standalone_ttft_data = ttft_values

            # Plot data
            ax = axes[i]
            ax_ttft = ax.twinx()
            ax.plot(dates, ray_tput_data, marker='o', color='tab:orange', label="tput_ray")
            ax.plot(dates, standalone_tput_data, marker='o', color='tab:blue', label="tput_standalone")
            ax_ttft.plot(dates, ray_ttft_data, marker='x', linestyle='--', color='tab:orange', label="ttft_ray")   
            ax_ttft.plot(dates, standalone_ttft_data, marker='x', linestyle='--', color='tab:blue', label="ttft_standalone")                 

            # Set titles and labels
            tput_max = max(ray_tput_data + standalone_tput_data) + margin
            tput_min = max(-100, min(ray_tput_data + standalone_tput_data) - margin)
            ttft_max = max(ray_ttft_data + standalone_ttft_data) + margin
            ttft_min = max(-100, min(ray_ttft_data + standalone_ttft_data) - margin)
            ax.set_title(benchmark_labels[i], fontsize=12)
            ax.set_xlabel("Date")
            ax.set_ylabel("Throughput (tok/s)")
            ax_ttft.set_ylabel("TTFT (ms)")
            ax.set_ylim(tput_min, tput_max)
            ax_ttft.set_ylim(ttft_min, ttft_max)
            ax.grid(True)
            ax.tick_params(axis='y')
            ax_ttft.tick_params(axis='y')
            
            # Create a combined legend for both lines on the subplot
            lines_tput, labels_tput = ax.get_legend_handles_labels()
            lines_ttft, labels_ttft = ax_ttft.get_legend_handles_labels()
            ax.legend()
            ax.legend(lines_tput + lines_ttft, labels_tput + labels_ttft, loc='best', fontsize='small')

        img_name = os.path.join(out_dir, bench_title + ".jpg")
        logger.info(f"[{py_script}] Saving {img_name}.")
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(img_name, dpi=300)
        plt.close()


def main(args):
    # 讀取 CSV
    for csv_file in overview_files:
        df = pd.read_csv(csv_file, header=None)

        if csv_file == "overview_accuracy.csv":
            Plot_Accuracy(df, "Accuracy", csv_row_overview_Acc, args.out_dir)
        elif csv_file == "overview_perf_8B.csv":
            Plot_Benchmark(df, "Performance_Llama-8B", csv_row_overview_8B_70B, args.out_dir)
        elif csv_file == "overview_perf_70B.csv":
            Plot_Benchmark(df, "Performance_Llama-70B", csv_row_overview_8B_70B, args.out_dir)
        elif csv_file == "overview_perf_Scout.csv":
            Plot_Benchmark(df, "Performance_Llama-Scout", csv_row_overview_Scout, args.out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=str, required=True, help="Path to save the plots.")
    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir, exist_ok=True)

    main(args)


'''
python Visualize.py --out-dir Result/Figures


'''