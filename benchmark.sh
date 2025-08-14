#!/bin/bash
set -x

# Sample cmd:
# ./benchmark.sh --engine vLLM   --model-dir /data/huggingface/hub --out-dir Result/{Date}
# ./benchmark.sh --engine SGLang --model-dir /data/huggingface/hub --out-dir Result/{Date}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --engine)
            if [[ "$2" != "vLLM" && "$2" != "SGLang" ]]; then
                echo "Error: Invalid value for --engine. Choices are [vLLM, SGLang]."
                exit 1
            fi
            engine=$2
            shift 2
            ;;
        --model-dir)
            model_dir=$2
            shift 2
            ;;
        --out-dir)
            out_dir=$2
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "   --engine         (required) choices=[vLLM, SGLang]"
            echo "   --model-dir      (required) path to the folder of the model"
            exit 0
            ;;
        *)
            echo "Error: Unknown option: $1"
            exit 1
            ;;
    esac
done


# Dependencies
pip install xgrammar==0.1.11 pynvml==12.0.0 botocore datasets
apt-get update
apt-get install -y jq
apt install -y linux-tools-common linux-tools-$(uname -r)
source ./utils.sh

# Export environment variables
# General variables
export SERVER_PORT=8123
export TORCH_BLAS_PREFER_HIPBLASLT=1
export NCCL_MIN_NCHANNELS=112
export HIP_FORCE_DEV_KERNARG=1

# vLLM variables
export VLLM_USE_TRITON_FLASH_ATTN=0
export VLLM_FP8_PADDING=1
export VLLM_FP8_ACT_PADDING=1
export VLLM_FP8_WEIGHT_PADDING=1
export VLLM_FP8_REDUCE_CONV=1
export VLLM_RPC_TIMEOUT=200000 # default 10000 ms
export VLLM_V1_USE_PREFILL_DECODE_ATTENTION=1
export VLLM_USE_V1=1
export VLLM_ROCM_USE_AITER=1
export VLLM_ROCM_USE_AITER_RMSNORM=0
# export TENSILE_STREAMK_DYNAMIC_GRID=6 # StreamK
# streamK="streamK"

# Ray variables
# export RAYLLM_ROUTER_RAY_ACTOR_OPTIONS='{"num_cpus": 2}'
export RAYLLM_ROUTER_HTTP_TIMEOUT=7200 # 2 hour. Default=600 second
export RAY_CGRAPH_submit_timeout=120 # default 10 sec
export RAY_CGRAPH_get_timeout=120 # default 10 sec
sysctl kernel.numa_balancing=0


# 1. Llama 8B/70B benchmark

# 2. Llama4-Scout benchmark



# Ray settings
cpu_mode="schedutil"
n_iter=1
llm_replica=1
router_replica=16   # need to update ray_engine.py
total_cpu_cores=num_cpus=$(lscpu | grep '^CPU(s):' | awk '{print $2}')
remaining_cpu_core=$((total_cpu_cores - router_replica))
cpupower frequency-set -g $cpu_mode 

echo "The total number of CPU core on this system is: $total_cpu_cores"

models_configs_vLLM=( # Only v1 engine. v0 engine is deprecated.
    # engine ray model  dtype tp quant_type kv_type max_model_len batched_tokens llm_replica
    "vLLM  true meta-llama/Llama-3.1-8B-Instruct           float16 1 None auto    4096  8192 1"  
    "vLLM  true meta-llama/Llama-3.3-70B-Instruct          float16 8 None auto    4096 16384 1"  
    # "vLLM  true meta-llama/Llama-4-Scout-17B-16E-Instruct bfloat16 8 None auto 1000000  8192 1"
    "vLLM false meta-llama/Llama-3.1-8B-Instruct           float16 1 None auto    4096  8192 1"  
    "vLLM false meta-llama/Llama-3.3-70B-Instruct          float16 8 None auto    4096 16384 1"  
    # "vLLM false meta-llama/Llama-4-Scout-17B-16E-Instruct bfloat16 8 None auto 1000000  8192 1"    
)

models_configs_SGLang=(
    # model ray dtype tp max_model_len kv_type
    # "SGLang  true meta-llama/Llama-3.1-8B-Instruct           float16 1 4096 auto"    # Blocked by SGLang integrtion
    # "SGLang  true meta-llama/Llama-3.3-70B-Instruct          float16 8 8192 auto"    # Blocked by SGLang integrtion
    # "SGLang  true meta-llama/Llama-4-Scout-17B-16E-Instruct bfloat16 8 1450000 auto" # ROCm SGLang hasn't support Llama4
    "SGLang false meta-llama/Llama-3.1-8B-Instruct           float16 1 4096 auto"
    "SGLang false meta-llama/Llama-3.3-70B-Instruct          float16 8 8192 auto"
    # "SGLang false meta-llama/Llama-4-Scout-17B-16E-Instruct bfloat16 8 1450000 auto" # ROCm SGLang hasn't support Llama4
)

TESTS_8B_70B=(
    # ilen olen concurrency num_prompts
    "32 32 16 3000"
    "32 32 64 3000"
    "32 32 256 3000"
    "128 128 16 3000"
    "128 128 64 3000"
    "128 128 256 3000"
    "1024 64 16 3000"
    "1024 64 64 3000"
    "1024 64 256 3000"
    "2048 128 16 1000"
    "2048 128 64 1000"
    "2048 128 256 1000"
    
    # Quick test
    # "32 32 256 300"
)

TESTS_Scout=(
    # ilen olen concurrency num_prompts
    "    120000 128 4 8"
    "    240000 128 4 8"
    "    480000 128 4 8"
    "    960000 128 4 8"
    "   1400000 128 4 8"
    # "  2097152 1920000 128 4 8"
    # "  4194304 3840000 128 4 8"
    # "  8388608 7680000 128 4 8"
    # " 10485760 9600000 128 4 8"

    # Quick test
    # "1024 32 256 300"
)


# Determine accelerator type
accelerator_type="unknown"
if command -v rocm-smi &>/dev/null; then
    gpu_info=$(rocm-smi --showproductname 2>/dev/null)
    subsystem_id=$(echo "$gpu_info" | grep "Card Model" | awk '{print $NF}' | head -n 1)
    if [ "$subsystem_id" == "0x74a1" ]; then
        accelerator_type="AMD-Instinct-MI300X-OAM"
    elif [ "$subsystem_id" == "0x74a5" ]; then
        accelerator_type="AMD-Instinct-MI325X-OAM"
    elif [ "$subsystem_id" == "0x74b9" ]; then
        accelerator_type="AMD-Instinct-MI325X-VF"
    else
        accelerator_type="Unknown_AMD_Accelerator"
        echo "Warning: Could not determine accelerator type from rocm-smi output."
        exit 0
    fi
    export RAY_EXPERIMENTAL_NOSET_HIP_VISIBLE_DEVICES=0
elif command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=gpu_name --format=csv,noheader 2>/dev/null | head -n 1 | xargs)
    # Determine GPU type based on the name
    if [[ "$GPU_NAME" == *"H200"* ]]; then
        accelerator_type="H200"
    elif [[ "$GPU_NAME" == *"H100"* ]]; then
        accelerator_type="H100"
    fi
fi


# Start benchmark
if [[ "$engine" == "vLLM" ]]; then
    models_configs=("${models_configs_vLLM[@]}")
elif [[ "$engine" == "SGLang" ]]; then
    models_configs=("${models_configs_SGLang[@]}")
fi

echo "models_configs=$models_configs"
for config in "${models_configs[@]}"; do
    engine=$(echo "$config" | awk '{print $1}')
    if [[ "$engine" == "vLLM" ]]; then
        IFS=' ' read -r _ ray_enable model_name dtype tp quant_type kv_type max_model_len batched_tokens llm_replica<<< "$config"
    elif [[ "$engine" == "SGLang" ]]; then
        IFS=' ' read -r _ ray_enable model_name dtype tp max_model_len kv_type<<< "$config"   
    fi
    echo "llm_replica is $llm_replica"
    deployment_mode=$([[ "$ray_enable" == "true" ]] && echo "ray" || echo "standalone")
    result_folder=$out_dir/${engine}_${deployment_mode}/${model_name/\//_}
    cpu_core_per_llm_replica=$((remaining_cpu_core / llm_replica))
    
    model_path="${model_dir}${model_name}"
	mkdir -p $result_folder
    echo "Launching $engine with config: $config"

    if [[ "$ray_enable" == "true" ]]; then
        if [[ "$engine" == "vLLM" ]]; then
            python ray_engine.py \
                --engine $engine \
                --port $SERVER_PORT \
                --cpu_core_per_llm_replica $cpu_core_per_llm_replica \
                --accelerator_type "$accelerator_type" \
                --model_path "$model_path" \
                --dtype "$dtype" \
                --llm_replica $llm_replica \
                --router_replica $router_replica \
                --tp $tp \
                --quant_type "$quant_type" \
                --kv_type "$kv_type" \
                --max_model_len "$max_model_len" \
                --max_num_batched_tokens "$batched_tokens" &
        elif [[ "$engine" == "SGLang" ]]; then
            python ray_engine.py \
                --engine $engine \
                --port $SERVER_PORT \
                --cpu_core_per_llm_replica $cpu_core_per_llm_replica \
                --accelerator_type "$accelerator_type" \
                --model_path "$model_path" \
                --dtype "$dtype" \
                --llm_replica $llm_replica \
                --router_replica $router_replica \
                --tp $tp \
                --max_model_len "$max_model_len" & \
        fi
    elif [[ "$ray_enable" == "false" ]]; then # It was used to compare with ray+vllm
        if [[ "$engine" == "vLLM" ]]; then
            vllm serve ${model_path} --swap-space 16 --disable-log-requests --port $SERVER_PORT \
                --tensor-parallel-size $tp --distributed-executor-backend ray \
                --dtype "$dtype" --gpu-memory-utilization 0.9 --no-enable-chunked-prefill \
                --max-model-len "$max_model_len" --max-num-batched-tokens "$batched_tokens" \
                --max-num-seqs 512 --max-seq-len-to-capture $max_model_len \
                --compilation-config '{"full_cuda_graph": false}' \
                --kv-cache-dtype "$kv_type" --no-enable-prefix-caching --uvicorn-log-level warning & \
                # --quantization "$quant_type"
        elif [[ "$engine" == "SGLang" ]]; then
            python -m sglang.launch_server --port $SERVER_PORT \
                --model-path ${model_path} \
                --dtype $dtype \
                --tp $tp \
                --mem-fraction-static 0.8 \
                --cuda-graph-max-bs 256 \
                --chunked-prefill-size -1 \
                --disable-radix-cache  \
                --context-length  $max_model_len \
                --kv-cache-dtype  $kv_type \
                --log-level "warning" &
        fi
    fi

    # Wait for server to be ready
    echo "Waiting for the server to be ready..."
    if [[ "$ray_enable" == "true" ]]; then
        api_url="http://localhost:8265/api/serve/applications/"
        echo "Checking replica status..."
        while true; do
            sleep 5
            set +x
            if check_replicas_status $api_url $engine; then
                echo "All replicas are RUNNING."
                set -x
                break
            fi
        done
    else 
        server_url="http://localhost:${SERVER_PORT}"
        server_launch_time=0
        while ! curl -s "$server_url" > /dev/null; do
            sleep 5
            server_launch_time=$((server_launch_time + 5))
            echo "Waiting for ${model_name} launch... ${server_launch_time}s"
        done
    fi


    # Warmup
    common_args="--host 127.0.0.1 --port $SERVER_PORT --model ${model_path} \
                    --dataset-name random --num-prompts 100 \
                    --random-input-len 128 --random-output-len 128 --random-range-ratio 0"
    if [[ "$engine" == "vLLM" ]]; then        
        bench_cmd="vllm bench serve --backend openai "
        specific_args="--percentile-metrics ttft,tpot,itl,e2el"
    elif [[ "$engine" == "SGLang" ]]; then
        bench_cmd="python -m sglang.bench_serving --backend sglang-oai "
        specific_args=""
    fi
    $bench_cmd $common_args $specific_args        
    
    if [[ "$model_name" == "meta-llama/Llama-3.1-8B-Instruct" ]] || [[ "$model_name" == "meta-llama/Llama-3.3-70B-Instruct" ]]; then
        TESTS=("${TESTS_8B_70B[@]}")
    elif [[ "$model_name" == "meta-llama/Llama-4-Scout-17B-16E-Instruct" ]]; then
        TESTS=("${TESTS_Scout[@]}")
    fi

    for test in "${TESTS[@]}"; do
        IFS=' ' read -r ilen olen concurrency num_prompts <<< "$test"
        
        for i in $(seq 1 $n_iter); do
            # Define the benchmark file path
            benchmark_file="${result_folder}/i${ilen}_o${olen}_c${concurrency}_p${num_prompts}_iter${i}.log"

            # Run the benchmark and capture the output in a log file
            $bench_cmd  \
                --host localhost \
                --port $SERVER_PORT \
                --model $model_path \
                --dataset-name random \
                --num-prompts $num_prompts \
                --random-input-len "$ilen" \
                --random-output-len "$olen" \
                --random-range-ratio 0 \
                --max-concurrency "$concurrency" \
                $specific_args \
                2>&1 | tee "${benchmark_file}"
        done  
    done

    # Kill vLLM/Ray engine after benchmarking
    echo "Stopping the server for model $model_name"
    ps -ef | grep '[p]ython' | awk '{print $2}' | xargs kill -9
    pkill -9 -f VLLM
    sleep 10
done

echo "✅ Benchmark complete."

cpupower frequency-set -g  performance # reset to perf mode



