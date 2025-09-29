#!/bin/bash
set -x

# Sample cmd:
# ./main.sh --model-dir $HOME/data/huggingface/hub

pip3 install -r requirement.txt

# 1. Download models
ci_dir=$(pwd)
date=$(date +"%Y-%m-%d") #  +"%Y-%m-%d-%H%M%S"
out_dir=$ci_dir/Result/$date
out_json=$out_dir/Result.json
out_figures_dir=$ci_dir/Result/Figures
mkdir -p $out_dir
host_model_dir=$HOME/data/huggingface/hub/
container_model_dir=/data/huggingface/hub/
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --model-dir)
            host_model_dir=$2
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --model-dir         Directory of model (default: $host_model_dir)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Set host_model_dir=$host_model_dir"
models=(
    "meta-llama/Llama-3.1-8B-Instruct"
    "meta-llama/Llama-3.3-70B-Instruct"
    # "meta-llama/Llama-4-Scout-17B-16E-Instruct"
)


# Check if model exists
hf auth login --token #Your_Token
EXCLUDE_PATTERN="original/*" # Llama 8B & 70B has the folder 'original' storing the duplicate checkpoint so we ignore it
download_pids=()
for model_name in "${models[@]}"; do
    model_path="${host_model_dir}/${model_name}"
    if [ ! -d "$model_path" ]; then
        echo "Model not found: $model_path. Downloading..."
        hf download "$model_name" \
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
latest_vLLM_docker=$(python3 -u GetLatestVllmDocker.py | tee /dev/tty | tail -n 1)
echo "Latest vLLM docker=$latest_vLLM_docker"
# latest_vLLM_docker="rocm/vllm-dev:nightly_main_20250804"
# 2.2 Fetch latest ROCm SGLang image with 'mi30x' and 'srt' sub-string
latest_SGLang_docker=$(python3 -u GetLatestSGLangDocker.py | tee /dev/tty | tail -n 1)
echo "Latest SGLang docker=$latest_SGLang_docker"
# ToDo: Record docker images to a list. Check if the images are already in the list, if so, skip benchmark.
python3 RecordDockerName.py \
    --json-file $out_json \
    --vLLM $latest_vLLM_docker \
    --SGLang $latest_SGLang_docker

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
        -v $host_model_dir:$container_model_dir \
        -v $HOME:$HOME \
        -v $ci_dir:$ci_dir \
        -w $ci_dir \
        "$docker_image"
}

pip install -r requirement.txt


# 3. vLLM benchmark
vllm_container_id=$(run_benchmark_container "CI_vLLM" "$latest_vLLM_docker")
# Dependencies of accuracy test
docker exec "CI_vLLM" bash -c "pip install gradio plotly evalscope" 
# Dependencies of benchmark
docker exec "CI_vLLM" bash -c "
    mkdir -p /app && \
    git clone https://github.com/ray-project/ray.git /app/ray && \
    pip install -r /app/ray/python/requirements.txt && \
    pip install --upgrade ray[serve,llm] --no-deps
"


# 3.1 Accuracy Test-evalscope
for model_name in "${models[@]}"; do
    echo "--------------------------- vLLM Accuracy Test ------------------------------------"
    model_path="$container_model_dir/${model_name}"
    # "--distributed-executor-backend ray"  tends to result in 'HW Exception by GPU node-5 (Agent handle: 0x16f721e0) reason :GPU Hang'
    docker exec -d "CI_vLLM" bash -c \
        "vllm serve $model_path -tp 8 --max_model_len 8192 --uvicorn-log-level warning \
        --distributed-executor-backend mp \
        --compilation-config '{\"full_cuda_graph\": false}' > /tmp/vllm_accuracy_test.log 2>&1 "
    docker exec "CI_vLLM" tail -f /tmp/vllm_accuracy_test.log &
    log_pid=$!

    wait_time=0
    until curl -s http://localhost:8000/v1/models | grep -q '"object"'; do
        echo "Waiting for the vLLM server to start $model_name...$wait_time sec"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    kill $log_pid

    output=$(docker exec "CI_vLLM" bash -c \
        "evalscope eval \
            --model $model_path  \
            --api-url http://localhost:8000/v1 \
            --api-key EMPTY \
            --eval-type openai_api \
            --datasets gsm8k \
            --limit 50 2>&1")
    report_path=$(echo "$output" | grep "Dump report to:" | awk '{print $NF}')
    echo "The report file is located at: $report_path"
    docker exec "CI_vLLM" bash -c "ps -ef | grep '[p]ython' | awk '{print \$2}' | xargs kill -9 && echo 'Kill server...'"
    docker exec "CI_vLLM" bash -c "pkill -9 -f VLLM"
    sleep 10 # Wait for killing server
    model_name_str=$(echo "$model_name" | sed 's/\//_/g') # "meta-llama/Llama-3.1-8B-Instruct" -> "meta-llama_Llama-3.1-8B-Instruct"
    python3 RecordAccuracy.py --engine vLLM --model $model_name_str --acc-path $report_path --out-json $out_json
    echo "------------------------------------------------------------------------"
done

# 3.2 Performance Test
docker exec "CI_vLLM" bash -c \
    "./benchmark.sh --engine vLLM  --model-dir $container_model_dir --out-dir $out_dir "



# 4. SGLang benchmark
sglang_container_id=$(run_benchmark_container "CI_SGLang" "$latest_SGLang_docker")

# Delete sglang code signal.signal...
docker exec "CI_SGLang" bash -c "
    sed -i '/signal.signal/d' /sgl-workspace/sglang/python/sglang/srt/entrypoints/engine.py
"

# 4.1 Accuracy Test
for model_name in "${models[@]}"; do
    if [ "$model_name" = "meta-llama/Llama-4-Scout-17B-16E-Instruct" ]; then
        continue
    fi
    
    echo "--------------------------- SGLang Accuracy Test ------------------------------------"
    model_path="$container_model_dir/${model_name}"
    docker exec -d "CI_SGLang" bash -c \
       "python -m sglang.launch_server --model-path $model_path --tp 8 \
       --mem-fraction-static 0.7 --context-length 8192 --log-level warning > /tmp/sglang_accuracy_test.log 2>&1"
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
    sleep 10 # Wait for killing server
    model_name_str=$(echo "$model_name" | sed 's/\//_/g') # "meta-llama/Llama-3.1-8B-Instruct" -> "meta-llama_Llama-3.1-8B-Instruct"
    python3 RecordAccuracy.py --engine SGLang --model $model_name_str --acc $acc --out $out_json
    echo "------------------------------------------------------------------------" 
done

# 4.2 Performance Test
docker exec "CI_SGLang" bash -c \
    "./benchmark.sh --engine SGLang  --model-dir $container_model_dir --out-dir $out_dir "



# 5. Visualization
# 5.1 Parse benchmark logs and save metrics into json file
python3 ParseBenchmark.py --json-file $out_json --folder $out_dir
# 5.2 Check regression. Threshold: 3%
python3 CheckRegression.py --json-file $out_json --result-folder $ci_dir/Result --exclude-date $date --threshold 3
# 5.3 Plot accuracy and performance figures 
python3 SaveOverviewCSV.py --json-file $out_json
python3 Visualize.py --out-dir Result/Figures

echo "----------------------------- Finish ------------------------"
rm -f *.jsonl 
docker stop CI_vLLM CI_SGLang

