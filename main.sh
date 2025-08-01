#!/bin/bash
set -x

# Sample cmd:
# ./main.sh --model-dir $HOME/data/huggingface/hub

# 1. Download models
ci_dir=$(pwd)
model_dir=$HOME/data/huggingface/hub
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

echo "Set model_dir=$model_dir"
models=(
    "meta-llama/Llama-3.1-8B-Instruct"
    "meta-llama/Llama-3.3-70B-Instruct"
    "meta-llama/Llama-4-Scout-17B-16E-Instruct"
)


# Check if model exists
huggingface-cli login --token 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
EXCLUDE_PATTERN="original/*" # Llama 8B & 70B has the folder 'original' storing the duplicate checkpoint so we ignore it
download_pids=()
for model_name in "${models[@]}"; do
    model_path="${model_dir}/${model_name}"
    if [ ! -d "$model_path" ]; then
        echo "Model not found: $model_path. Downloading..."
        huggingface-cli download "$model_name" \
            --local-dir "$model_path" \
            --resume-download \
            --exclude "$EXCLUDE_PATTERN"  &
        download_pids+=($!)
    else
        echo "Model already exists: $model_path. Skipping download."
    fi
done

# Wait for download
if [ ${#download_pids[@]} -gt 0 ]; then
    echo "Waiting for all background downloads to complete..."
    wait "${download_pids[@]}"
fi
echo "All models are ready."


# 2. Setup
# 2.1 Fetch latest ROCm vLLM image with 'rc' sub-string
latest_vLLM_docker=$(python3 GetLatestVllmDocker.py | tail -n 1)
echo "Latest vLLM docker=$latest_vLLM_docker"
# 2.2 Fetch latest ROCm SGLang image with 'mi30x' and 'srt' sub-string
latest_SGLang_docker=$(python3 GetLatestSGLangDocker.py | tail -n 1)
echo "Latest SGLang docker=$latest_SGLang_docker"

run_benchmark_container() {
    local container_name="$1"
    local docker_image="$2"

    echo "Starting benchmark container: ${container_name} with image ${docker_image}"

    docker run -t -d --rm --privileged \
        --name="${container_name}" \
        --network=host \
        --device=/dev/kfd \
        --device=/dev/dri \
        --group-add video \
        --cap-add=SYS_PTRACE \
        --security-opt seccomp=unconfined \
        --ipc=host \
        --shm-size=32g \
        -v "$model_dir":/data/ \
        -w "$ci_dir" \
        "$docker_image"
}


# 3. vLLM benchmark
vllm_container_id=$(run_benchmark_container "CI_vLLM" "$latest_vLLM_docker")
# 3.1 Accuracy Test
# 3.2 Performance Test
# 3.2.1 Old Configuration (no Ray)
# 3.2.2 New Configuration (Ray)
# 3.2.3 Long Context (Ray)

# 4. SGLang benchmark
sglang_container_id=$(run_benchmark_container "CI_SGLang" "$latest_SGLang_docker")
# 4.1 Accuracy Test
# 4.2 Performance Test

# 5. Visualization