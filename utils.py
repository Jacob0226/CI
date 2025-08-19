# logger_setup.py
import logging
import sys
import colorlog

def setup_logger(name="default_logger", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s %(message)s %(reset)s",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={}
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger



bench_types = [
    "vLLM_ray",
    "vLLM_standalone",
    "SGLang_ray",
    "SGLang_standalone",
]

models = [
    "meta-llama_Llama-3.1-8B-Instruct",
    "meta-llama_Llama-3.3-70B-Instruct",
    "meta-llama_Llama-4-Scout-17B-16E-Instruct",
]

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

metric_mapping = {
    "tput": "Output token throughput (tok/s)",
    "ttft": "Mean TTFT (ms)",
}

def GetMetrics(folder):
    # Only need throughput and ttft
    if "SGLang" in folder:
        metrics = [
            "Output token throughput (tok/s)",
            "Mean TTFT (ms)",
            # "Mean E2E Latency (ms)", # SGLang
            # "Mean ITL (ms)",  
        ]
    else: # "vLLM" in folder:
        metrics = [
            "Output token throughput (tok/s)",
            "Mean TTFT (ms)",
            # "Mean E2EL (ms)",
            # "Mean ITL (ms)",  
        ]
    return metrics

# -------------------------------------------------
# About overview csv files
overview_files = [
    "overview_accuracy.csv",
    "overview_perf_8B.csv",
    "overview_perf_70B.csv",
    "overview_perf_Scout.csv",
]

csv_row_overview_Acc = { # draw plots
    "vLLM-Evalscope":{ # Title
        "meta-llama_Llama-3.1-8B-Instruct": 3,
        "meta-llama_Llama-3.3-70B-Instruct": 4,
        "meta-llama_Llama-4-Scout-17B-16E-Instruct": 5,
    },
    "SGLang-few_shot_gsm8k":{
        "meta-llama_Llama-3.1-8B-Instruct": 8,
        "meta-llama_Llama-3.3-70B-Instruct": 9,
    }
}

csv_row_overview_8B_70B = { # draw plots
    "vLLM_ray":{
        "tput": [4, 15], # start row and end row
        "ttft": [18, 29],
    },
    "vLLM_standalone":{
        "tput": [33, 44],
        "ttft": [47, 58],
    },
    "SGLang_ray":{
        "tput": [62, 73],
        "ttft": [76, 87],
    },
    "SGLang_standalone":{
        "tput": [91, 102],
        "ttft": [105, 116],
    }
}

csv_row_overview_Scout = { # draw plots
    "vLLM_ray":{
        "tput": [4, 7], # start row and end row
        "ttft": [10, 13],
    },
    "vLLM_standalone":{
        "tput": [17, 20],
        "ttft": [20, 23],
    },
    # "SGLang_ray":{   # ROCm SGLang doesn't support Llama4 yet
    #     "tput": [],
    #     "ttft": [],
    # }
    # "SGLang_standalone":{
    #     "tput": [],
    #     "ttft": [],
    # }
}

row_mapping_acc = [ # map to Result.json
    # name, row, json_key_layer
    ["vLLM_meta-llama_Llama-3.1-8B-Instruct_Acc",          3, ["Accuracy", "vLLM",   "meta-llama_Llama-3.1-8B-Instruct"]],
    ["vLLM_meta-llama_Llama-3.3-70B-Instruct_Acc",         4, ["Accuracy", "vLLM",   "meta-llama_Llama-3.3-70B-Instruct"]],
    ["vLLM_meta-llama_Llama-4-Scout-17B-16E-Instruct_Acc", 5, ["Accuracy", "vLLM",   "meta-llama_Llama-4-Scout-17B-16E-Instruct"]],
    ["SGLang_meta-llama_Llama-3.1-8B-Instruct_Acc",        8, ["Accuracy", "SGLang", "meta-llama_Llama-3.1-8B-Instruct"]],
    ["SGLang_meta-llama_Llama-3.3-70B-Instruct_Acc",       9, ["Accuracy", "SGLang", "meta-llama_Llama-3.3-70B-Instruct"]],
]

row_mapping_Scout = [
    # name, row, json_key_layer
    ["vLLM_ray_Scout_i120000_o128_c4_p8_Perf",            "4",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i120000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_ray_Scout_i240000_o128_c4_p8_Perf",            "5",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i240000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_ray_Scout_i480000_o128_c4_p8_Perf",            "6",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i480000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_ray_Scout_i960000_o128_c4_p8_Perf",            "7",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i960000_o128_c4_p8",    "Output token throughput (tok/s)",]],

    ["vLLM_ray_Scout_i120000_o128_c4_p8_Perf",            "10",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i120000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_ray_Scout_i240000_o128_c4_p8_Perf",            "11",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i240000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_ray_Scout_i480000_o128_c4_p8_Perf",            "12",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i480000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_ray_Scout_i960000_o128_c4_p8_Perf",            "13",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i960000_o128_c4_p8",    "Mean TTFT (ms)",]],

    ["vLLM_standalone_Scout_i120000_o128_c4_p8_Perf",     "17",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i120000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_standalone_Scout_i240000_o128_c4_p8_Perf",     "18",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i240000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_standalone_Scout_i480000_o128_c4_p8_Perf",     "19",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i480000_o128_c4_p8",    "Output token throughput (tok/s)",]],
    ["vLLM_standalone_Scout_i960000_o128_c4_p8_Perf",     "20",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i960000_o128_c4_p8",    "Output token throughput (tok/s)",]],

    ["vLLM_standalone_Scout_i120000_o128_c4_p8_Perf",     "23",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i120000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_standalone_Scout_i240000_o128_c4_p8_Perf",     "24",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i240000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_standalone_Scout_i480000_o128_c4_p8_Perf",     "25",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i480000_o128_c4_p8",    "Mean TTFT (ms)",]],
    ["vLLM_standalone_Scout_i960000_o128_c4_p8_Perf",     "26",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-4-Scout-17B-16E-Instruct", "i960000_o128_c4_p8",    "Mean TTFT (ms)",]],
]


row_mapping_8B = [
    ["vLLM_ray_8B_i32_o32_c16_p3000_Perf",              "4",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i32_o32_c64_p3000_Perf",              "5",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i32_o32_c256_p3000_Perf",             "6",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i128_o128_c16_p3000_Perf",            "7",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i128_o128_c64_p3000_Perf",            "8",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i128_o128_c256_p3000_Perf",           "9",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i1024_o64_c16_p3000_Perf",            "10",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i1024_o64_c64_p3000_Perf",            "11",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i1024_o64_c256_p3000_Perf",           "12",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i2048_o128_c16_p1000_Perf",           "13",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i2048_o128_c64_p1000_Perf",           "14",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_8B_i2048_o128_c256_p1000_Perf",          "15",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["vLLM_ray_8B_i32_o32_c16_p3000_Perf",              "18",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i32_o32_c64_p3000_Perf",              "19",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i32_o32_c256_p3000_Perf",             "20",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i128_o128_c16_p3000_Perf",            "21",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i128_o128_c64_p3000_Perf",            "22",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i128_o128_c256_p3000_Perf",           "23",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i1024_o64_c16_p3000_Perf",            "24",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i1024_o64_c64_p3000_Perf",            "25",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i1024_o64_c256_p3000_Perf",           "26",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i2048_o128_c16_p1000_Perf",           "27",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i2048_o128_c64_p1000_Perf",           "28",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_8B_i2048_o128_c256_p1000_Perf",          "29",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["vLLM_standalone_8B_i32_o32_c16_p3000_Perf",       "33",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i32_o32_c64_p3000_Perf",       "34",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i32_o32_c256_p3000_Perf",      "35",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i128_o128_c16_p3000_Perf",     "36",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i128_o128_c64_p3000_Perf",     "37",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i128_o128_c256_p3000_Perf",    "38",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i1024_o64_c16_p3000_Perf",     "39",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i1024_o64_c64_p3000_Perf",     "40",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i1024_o64_c256_p3000_Perf",    "41",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i2048_o128_c16_p1000_Perf",    "42",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i2048_o128_c64_p1000_Perf",    "43",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_8B_i2048_o128_c256_p1000_Perf",   "44",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["vLLM_standalone_8B_i32_o32_c16_p3000_Perf",       "47",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i32_o32_c64_p3000_Perf",       "48",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i32_o32_c256_p3000_Perf",      "49",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i128_o128_c16_p3000_Perf",     "50",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i128_o128_c64_p3000_Perf",     "51",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i128_o128_c256_p3000_Perf",    "52",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i1024_o64_c16_p3000_Perf",     "53",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i1024_o64_c64_p3000_Perf",     "54",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i1024_o64_c256_p3000_Perf",    "55",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i2048_o128_c16_p1000_Perf",    "56",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i2048_o128_c64_p1000_Perf",    "57",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_8B_i2048_o128_c256_p1000_Perf",   "58",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["SGLang_ray_8B_i32_o32_c16_p3000_Perf",            "62",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i32_o32_c64_p3000_Perf",            "63",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i32_o32_c256_p3000_Perf",           "64",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i128_o128_c16_p3000_Perf",          "65",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i128_o128_c64_p3000_Perf",          "66",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i128_o128_c256_p3000_Perf",         "67",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i1024_o64_c16_p3000_Perf",          "68",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i1024_o64_c64_p3000_Perf",          "69",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i1024_o64_c256_p3000_Perf",         "70",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i2048_o128_c16_p1000_Perf",         "71",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i2048_o128_c64_p1000_Perf",         "72",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_8B_i2048_o128_c256_p1000_Perf",        "73",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["SGLang_ray_8B_i32_o32_c16_p3000_Perf",            "76",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i32_o32_c64_p3000_Perf",            "77",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i32_o32_c256_p3000_Perf",           "78",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i128_o128_c16_p3000_Perf",          "79",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i128_o128_c64_p3000_Perf",          "80",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i128_o128_c256_p3000_Perf",         "81",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i1024_o64_c16_p3000_Perf",          "82",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i1024_o64_c64_p3000_Perf",          "83",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i1024_o64_c256_p3000_Perf",         "84",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i2048_o128_c16_p1000_Perf",         "85",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i2048_o128_c64_p1000_Perf",         "86",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_8B_i2048_o128_c256_p1000_Perf",        "87",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["SGLang_standalone_8B_i32_o32_c16_p3000_Perf",     "91",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i32_o32_c64_p3000_Perf",     "92",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i32_o32_c256_p3000_Perf",    "93",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i128_o128_c16_p3000_Perf",   "94",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i128_o128_c64_p3000_Perf",   "95",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i128_o128_c256_p3000_Perf",  "96",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i1024_o64_c16_p3000_Perf",   "97",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i1024_o64_c64_p3000_Perf",   "98",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i1024_o64_c256_p3000_Perf",  "99",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i2048_o128_c16_p1000_Perf",  "100", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i2048_o128_c64_p1000_Perf",  "101", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_8B_i2048_o128_c256_p1000_Perf", "102", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["SGLang_standalone_8B_i32_o32_c16_p3000_Perf",     "105", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i32_o32_c64_p3000_Perf",     "106", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i32_o32_c256_p3000_Perf",    "107", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i128_o128_c16_p3000_Perf",   "108", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i128_o128_c64_p3000_Perf",   "109", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i128_o128_c256_p3000_Perf",  "110", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i1024_o64_c16_p3000_Perf",   "111", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i1024_o64_c64_p3000_Perf",   "112", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i1024_o64_c256_p3000_Perf",  "113", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i2048_o128_c16_p1000_Perf",  "114", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i2048_o128_c64_p1000_Perf",  "115", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_8B_i2048_o128_c256_p1000_Perf", "116", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.1-8B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

]
row_mapping_70B = [
    ["vLLM_ray_70B_i32_o32_c16_p3000_Perf",               "4",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i32_o32_c64_p3000_Perf",               "5",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i32_o32_c256_p3000_Perf",              "6",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i128_o128_c16_p3000_Perf",             "7",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i128_o128_c64_p3000_Perf",             "8",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i128_o128_c256_p3000_Perf",            "9",   ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i1024_o64_c16_p3000_Perf",             "10",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i1024_o64_c64_p3000_Perf",             "11",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i1024_o64_c256_p3000_Perf",            "12",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i2048_o128_c16_p1000_Perf",            "13",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i2048_o128_c64_p1000_Perf",            "14",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_ray_70B_i2048_o128_c256_p1000_Perf",           "15",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["vLLM_ray_70B_i32_o32_c16_p3000_Perf",               "18",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i32_o32_c64_p3000_Perf",               "19",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i32_o32_c256_p3000_Perf",              "20",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i128_o128_c16_p3000_Perf",             "21",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i128_o128_c64_p3000_Perf",             "22",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i128_o128_c256_p3000_Perf",            "23",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i1024_o64_c16_p3000_Perf",             "24",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i1024_o64_c64_p3000_Perf",             "25",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i1024_o64_c256_p3000_Perf",            "26",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i2048_o128_c16_p1000_Perf",            "27",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i2048_o128_c64_p1000_Perf",            "28",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_ray_70B_i2048_o128_c256_p1000_Perf",           "29",  ["Benchmark", "vLLM_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["vLLM_standalone_70B_i32_o32_c16_p3000_Perf",        "33",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i32_o32_c64_p3000_Perf",        "34",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i32_o32_c256_p3000_Perf",       "35",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i128_o128_c16_p3000_Perf",      "36",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i128_o128_c64_p3000_Perf",      "37",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i128_o128_c256_p3000_Perf",     "38",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i1024_o64_c16_p3000_Perf",      "39",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i1024_o64_c64_p3000_Perf",      "40",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i1024_o64_c256_p3000_Perf",     "41",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i2048_o128_c16_p1000_Perf",     "42",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i2048_o128_c64_p1000_Perf",     "43",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["vLLM_standalone_70B_i2048_o128_c256_p1000_Perf",    "44",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["vLLM_standalone_70B_i32_o32_c16_p3000_Perf",        "47",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i32_o32_c64_p3000_Perf",        "48",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i32_o32_c256_p3000_Perf",       "49",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i128_o128_c16_p3000_Perf",      "50",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i128_o128_c64_p3000_Perf",      "51",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i128_o128_c256_p3000_Perf",     "52",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i1024_o64_c16_p3000_Perf",      "53",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i1024_o64_c64_p3000_Perf",      "54",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i1024_o64_c256_p3000_Perf",     "55",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i2048_o128_c16_p1000_Perf",     "56",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i2048_o128_c64_p1000_Perf",     "57",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["vLLM_standalone_70B_i2048_o128_c256_p1000_Perf",    "58",  ["Benchmark", "vLLM_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["SGLang_ray_70B_i32_o32_c16_p3000_Perf",             "62",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i32_o32_c64_p3000_Perf",             "63",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i32_o32_c256_p3000_Perf",            "64",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i128_o128_c16_p3000_Perf",           "65",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i128_o128_c64_p3000_Perf",           "66",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i128_o128_c256_p3000_Perf",          "67",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i1024_o64_c16_p3000_Perf",           "68",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i1024_o64_c64_p3000_Perf",           "69",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i1024_o64_c256_p3000_Perf",          "70",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i2048_o128_c16_p1000_Perf",          "71",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i2048_o128_c64_p1000_Perf",          "72",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_ray_70B_i2048_o128_c256_p1000_Perf",         "73",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["SGLang_ray_70B_i32_o32_c16_p3000_Perf",             "76",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i32_o32_c64_p3000_Perf",             "77",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i32_o32_c256_p3000_Perf",            "78",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i128_o128_c16_p3000_Perf",           "79",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i128_o128_c64_p3000_Perf",           "80",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i128_o128_c256_p3000_Perf",          "81",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i1024_o64_c16_p3000_Perf",           "82",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i1024_o64_c64_p3000_Perf",           "83",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i1024_o64_c256_p3000_Perf",          "84",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i2048_o128_c16_p1000_Perf",          "85",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i2048_o128_c64_p1000_Perf",          "86",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_ray_70B_i2048_o128_c256_p1000_Perf",         "87",  ["Benchmark", "SGLang_ray", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

    ["SGLang_standalone_70B_i32_o32_c16_p3000_Perf",      "91",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i32_o32_c64_p3000_Perf",      "92",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i32_o32_c256_p3000_Perf",     "93",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i128_o128_c16_p3000_Perf",    "94",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i128_o128_c64_p3000_Perf",    "95",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i128_o128_c256_p3000_Perf",   "96",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i1024_o64_c16_p3000_Perf",    "97",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i1024_o64_c64_p3000_Perf",    "98",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i1024_o64_c256_p3000_Perf",   "99",  ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i2048_o128_c16_p1000_Perf",   "100", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i2048_o128_c64_p1000_Perf",   "101", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Output token throughput (tok/s)",]],
    ["SGLang_standalone_70B_i2048_o128_c256_p1000_Perf",  "102", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Output token throughput (tok/s)",]],

    ["SGLang_standalone_70B_i32_o32_c16_p3000_Perf",      "105", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c16_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i32_o32_c64_p3000_Perf",      "106", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c64_p3000",     "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i32_o32_c256_p3000_Perf",     "107", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i32_o32_c256_p3000",    "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i128_o128_c16_p3000_Perf",    "108", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i128_o128_c64_p3000_Perf",    "109", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i128_o128_c256_p3000_Perf",   "110", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i128_o128_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i1024_o64_c16_p3000_Perf",    "111", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c16_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i1024_o64_c64_p3000_Perf",    "112", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c64_p3000",   "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i1024_o64_c256_p3000_Perf",   "113", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i1024_o64_c256_p3000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i2048_o128_c16_p1000_Perf",   "114", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c16_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i2048_o128_c64_p1000_Perf",   "115", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c64_p1000",  "Mean TTFT (ms)",]],
    ["SGLang_standalone_70B_i2048_o128_c256_p1000_Perf",  "116", ["Benchmark", "SGLang_standalone", "meta-llama_Llama-3.3-70B-Instruct", "i2048_o128_c256_p1000", "Mean TTFT (ms)",]],

]
