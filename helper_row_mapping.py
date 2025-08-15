from utils import bench_types,  log_files_prefix_Llama_8B_70B, log_file_prefix_Llama4_Scout






# 8B
def print_8B():
    model = "meta-llama_Llama-3.1-8B-Instruct"
    metrics = [
        "Output token throughput (tok/s)",
        "Mean TTFT (ms)",
    ]
    model_size = "8B"
    configs = log_files_prefix_Llama_8B_70B
    start_row = 4

    print("row_mapping_8B = [")
    print("    # name, row, json_key_layer")
    for bt in bench_types:
        for metric in metrics:
            if metric == "Output token throughput (tok/s)":
                metric_space = 34
            else:
                metric_space = 12
            for config in configs:

                name = f'"{bt}_{model_size}_{config}_Perf",'.ljust(50) # 41
                row_str = f'"{str(start_row)}",'.ljust(6)
                bt_str = f'"{bt}",' # bt_str = f'"{bt}",'.ljust(15)
                model_str = f'"{model}",' # f'"{model}",'.ljust(40)
                config_str = f'"{config}",'.ljust(24)
                metric_str = f'"{metric}",'.ljust(metric_space)

                generated_string = f'    [{name} {row_str} ["Benchmark", {bt_str} {model_str} {config_str} {metric_str}]],'
                start_row += 1
                print(generated_string)
            print()
            start_row += 2
        start_row += 1
    print("]")

# 70B
def print_70B():
    model = "meta-llama_Llama-3.3-70B-Instruct"
    metrics = [
        "Output token throughput (tok/s)",
        "Mean TTFT (ms)",
    ]
    model_size = "70B"
    configs = log_files_prefix_Llama_8B_70B
    start_row = 4

    print("row_mapping_70B = [")
    print("    # name, row, json_key_layer")
    for bt in bench_types:
        for metric in metrics:
            if metric == "Output token throughput (tok/s)":
                metric_space = 34
            else:
                metric_space = 12
            for config in configs:

                name = f'"{bt}_{model_size}_{config}_Perf",'.ljust(52) 
                row_str = f'"{str(start_row)}",'.ljust(6)
                bt_str = f'"{bt}",' # bt_str = f'"{bt}",'.ljust(15)
                model_str = f'"{model}",' # f'"{model}",'.ljust(40)
                config_str = f'"{config}",'.ljust(24)
                metric_str = f'"{metric}",'.ljust(metric_space)

                generated_string = f'    [{name} {row_str} ["Benchmark", {bt_str} {model_str} {config_str} {metric_str}]],'
                start_row += 1
                print(generated_string)
            print()
            start_row += 2
        start_row += 1
    print("]")

# Scout
def print_Scout():
    model = "meta-llama_Llama-4-Scout-17B-16E-Instruct"
    metrics = [
        "Output token throughput (tok/s)",
        "Mean TTFT (ms)",
    ]
    model_size = "Scout"
    configs = log_file_prefix_Llama4_Scout
    start_row = 4
    bench_types = [
        "vLLM_ray",
        "vLLM_standalone",
        # "SGLang_ray",         # ROCm SGLang doesn't support Llama4
        # "SGLang_standalone",
    ]

    print("row_mapping_Scout = [")
    print("    # name, row, json_key_layer")
    for bt in bench_types:
        for metric in metrics:
            if metric == "Output token throughput (tok/s)":
                metric_space = 34
            else:
                metric_space = 12
            for config in configs:

                name = f'"{bt}_{model_size}_{config}_Perf",'.ljust(52) 
                row_str = f'"{str(start_row)}",'.ljust(6)
                bt_str = f'"{bt}",' # bt_str = f'"{bt}",'.ljust(15)
                model_str = f'"{model}",' # f'"{model}",'.ljust(40)
                config_str = f'"{config}",'.ljust(24)
                metric_str = f'"{metric}",'.ljust(metric_space)

                generated_string = f'    [{name} {row_str} ["Benchmark", {bt_str} {model_str} {config_str} {metric_str}]],'
                start_row += 1
                print(generated_string)
            print()
            start_row += 2
        start_row += 1
    print("]")

if __name__ == "__main__":
    # print_8B()
    # print_70B()
    print_Scout()