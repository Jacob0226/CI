#!/bin/bash
# set -x

# Sample cmd:
# ./main.sh --model-dir /data/huggingface/hub

# 1. Check models
model_dir=/data/huggingface/hub
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --model-dir)
            model_dir=$2
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --model-dir         Directory of model (default: $model_dir)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "model_dir=$model_dir"
models=(
    "meta-llama/Llama-3.1-8B-Instruct"
    "meta-llama/Llama-3.3-70B-Instruct"
    "meta-llama/Llama-4-Scout-17B-16E-Instruct"
)

# 2. Setup
# 2.1 Fetch latest vLLM image with 'rc' sub-string
# 2.2 Fetch latest SGLang image with


# 2. vLLM benchmark
# 2.1 Accuracy Test
# 2.2 Performance Test
# 2.2.1 Old Configuration (no Ray)
# 2.2.2 New Configuration (Ray)
# 2.2.3 Long Context (Ray)


# 3. SGLang benchmark
# 3.1 Accuracy Test
# 3.2 Performance Test

# 4. Visualization