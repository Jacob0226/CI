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