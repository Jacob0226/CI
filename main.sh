#!/bin/bash
set -x

# Sample cmd:
# ./main.sh --model-dir $HOME/data/huggingface/hub


# 1. Download models
ci_dir=$(pwd)
date=$(date +"%Y-%m-%d") #  +"%Y-%m-%d-%H%M%S"
out_dir=$ci_dir/Result/$date
mkdir -p $out_dir $out_dir/vLLM $out_dir/SGLang
exit
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
    # "meta-llama/Llama-3.3-70B-Instruct"
    # "meta-llama/Llama-4-Scout-17B-16E-Instruct"
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
latest_vLLM_docker="rocm/vllm-dev:nightly_main_20250804"
echo "Latest vLLM docker=$latest_vLLM_docker"
# 2.2 Fetch latest ROCm SGLang image with 'mi30x' and 'srt' sub-string
latest_SGLang_docker=$(python3 GetLatestSGLangDocker.py | tail -n 1)
echo "Latest SGLang docker=$latest_SGLang_docker"
# ToDo: Record docker images to a list. Check if the images are already in the list, if so, skip benchmark.


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
        -v $model_dir:/data/huggingface/hub \
        -v $ci_dir:$ci_dir \
        -w $ci_dir \
        "$docker_image"
}


# 3. vLLM benchmark
vllm_container_id=$(run_benchmark_container "CI_vLLM" "$latest_vLLM_docker")
docker exec "CI_vLLM" bash -c "pip install gradio plotly evalscope"
for model_name in "${models[@]}"; do
    # 3.1 Accuracy Test-evalscope
    echo "--------------------------- vLLM Accuracy Test ------------------------------------"
    model_path="/data/huggingface/hub/${model_name}"
    docker exec -d "CI_vLLM" bash -c "vllm serve $model_path -tp 8 --max_model_len 8192 > /tmp/vllm_accuracy_test.log 2>&1 &"
    docker exec "CI_vLLM" tail -f /tmp/vllm_accuracy_test.log &
    log_pid=$!

    wait_time=0
    until curl -s http://localhost:8000/v1/models | grep -q '"object"'; do
        echo "Waiting for the vLLM server to start...$wait_time sec"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    kill $log_pid
    output=$(docker exec "CI_vLLM" bash -c \
        "evalscope eval \
            --model $model_path  \
            --api-url http://localhost:8000/v1 \
            --api-key EMPTY \
            --eval-type service \
            --datasets gsm8k \
            --limit 10 2>&1")
    report_path=$(echo "$output" | grep "Dump report to:" | awk '{print $NF}')
    echo "The report file is located at: $report_path"
    docker exec "CI_vLLM" bash -c "ps -ef | grep '[p]ython' | awk '{print \$2}' | xargs kill -9 && echo 'Kill server...'"
    python3 RecordAccuracy.py --engine vLLM --model $model_name --acc-path $report_path
    echo "------------------------------------------------------------------------"

    # 3.2 Performance Test
    # 3.2.1 Old Configuration (no Ray)
    ./benchmark.sh --engine vLLM   --model-dir /data/huggingface/hub --out-dir $out_dir
    
    # 3.2.2 New Configuration (Ray)
    # 3.2.3 Long Context (Ray)
done


# 4. SGLang benchmark
sglang_container_id=$(run_benchmark_container "CI_SGLang" "$latest_SGLang_docker")
for model_name in "${models[@]}"; do
    # 4.1 Accuracy Test
    echo "--------------------------- SGLang Accuracy Test ------------------------------------"
    model_path="/data/huggingface/hub/${model_name}"
    docker exec -d "CI_SGLang" bash -c \
        "python -m sglang.launch_server --model-path $model_path --tp 8 \
        --mem-fraction-static 0.7 --context-length 8192 > /tmp/sglang_accuracy_test.log 2>&1 &"
    docker exec "CI_SGLang" tail -f /tmp/sglang_accuracy_test.log &
    log_pid=$!

    wait_time=0
    until curl -s http://localhost:30000/v1/models | grep -q '"object"'; do
        echo "Waiting for the SGLang server to start...$wait_time sec"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    kill $log_pid
    output=$(docker exec "CI_SGLang" bash -c \ "python3 -m sglang.test.few_shot_gsm8k --num-questions 200 --parallel 200")
    acc=$(echo "$output" | grep "Accuracy:" | awk '{print $2}')
    docker exec "CI_SGLang" bash -c "ps -ef | grep '[p]ython' | awk '{print \$2}' | xargs kill -9 && echo 'Kill server...'"
    python3 RecordAccuracy.py --engine SGLang --model $model_name --acc $acc
    echo "------------------------------------------------------------------------"

    # 4.2 Performance Test

done

# 5. Visualization



docker stop CI_vLLM CI_SGLang
