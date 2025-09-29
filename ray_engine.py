import ray
from ray import serve
from ray.serve.llm import LLMConfig, LLMServer, LLMRouter
from ray.serve.schema import LoggingConfig
import os
import argparse
import time
import logging
import uvicorn
import json

def main():
    parser = argparse.ArgumentParser(description="Deploy and test LLM using Ray Serve")
    parser.add_argument("--engine", type=str, help="LLM engine:[vLLM, SGLang]", choices=["vLLM", "SGLang"], required=True)
    parser.add_argument("--port", type=int, help="server port", default=8000)
    parser.add_argument("--cpu_core_per_llm_replica", type=int, help="cpu core per llm replica", required=True)
    parser.add_argument("--accelerator_type", type=str, help="MI300X or H100", required=True)
    parser.add_argument("--model_path", type=str, help="Path to the model folder", required=True)
    parser.add_argument("--dtype", type=str, help="data type", required=True)
    parser.add_argument("--llm_replica", type=int, help="The number of vLLM instances", required=True)
    parser.add_argument("--router_replica", type=int, help="The number of router instances", required=True)
    parser.add_argument("--tp", type=int, help="Tensor parallel size", required=True)
    parser.add_argument("--quant_type", type=str, default=None, help="Quantization type")
    parser.add_argument("--kv_type", type=str, default="auto", help="KV cache data type")
    parser.add_argument("--max_model_len", type=int, help="Maximum model length", required=True)
    parser.add_argument("--max_num_batched_tokens", type=int, help="Maximum number of batched tokens", default=8192)
    args = parser.parse_args()
    # Create LLMConfig object


    n_replica=args.llm_replica
    server_config = LLMConfig(
        llm_engine=args.engine,
        model_loading_config=dict(
            model_id=args.model_path,
            model_source=args.model_path,
        ),
        deployment_config=dict(
            max_ongoing_requests=256, 
            autoscaling_config=dict(
                initial_replicas=n_replica,
                min_replicas=n_replica,
                max_replicas=n_replica,
            ),
            ray_actor_options=dict(
                num_cpus=args.cpu_core_per_llm_replica
            ),
        ),
        experimental_configs={
            # Maximum batching
            "stream_batching_interval_ms": 50,
        },
        # accelerator_type=args.accelerator_type,
    )
    from vllm.config import CompilationConfig
    vllm_compilation_config = CompilationConfig(full_cuda_graph=False)
    if args.engine == "vLLM":
        server_config.engine_kwargs=dict(
            swap_space=16,
            tensor_parallel_size=args.tp,
            dtype=args.dtype,
            gpu_memory_utilization=0.9,
            enable_chunked_prefill=False,
            enable_prefix_caching=False,
            max_model_len=args.max_model_len,
            max_num_batched_tokens=args.max_num_batched_tokens,
            quantization=None if args.quant_type == 'None' else args.quant_type,
            kv_cache_dtype=args.kv_type,
            max_num_seqs=256,
            compilation_config=vllm_compilation_config,
            # max_seq_len_to_capture=args.max_num_batched_tokens, # Deprecated in vLLM v 0.11
            # disable_log_requests=True, # Deprecated in vLLM v 0.11
        )
    elif args.engine == "SGLang":
        server_config.engine_kwargs=dict( 
            model_path= args.model_path,
            mem_fraction_static = 0.8, # only reserve for model checkpoints and kv cache. the intermediate results are not in this reservation
            tp_size = args.tp,                 
            cuda_graph_max_bs = 256,
            dtype=args.dtype,
            chunked_prefill_size=-1, # enable_chunked_prefill=False,
            disable_radix_cache=True, # enable_prefix_caching=False,
            context_length=args.max_model_len, #max_model_len=8192,
            kv_cache_dtype=args.kv_type, 
            attention_backend="aiter",
            log_level='warning',
        )

    # Configure LLMRouter with explicit settings
    router_config = LLMConfig(
        model_loading_config=dict(
            model_id=args.model_path,
            model_source=args.model_path,
        ),
        experimental_configs={
            "num_router_replicas": args.router_replica,
        },
    )


    print(f"[DEBUG] server_config={server_config}")
    # Deploy the LLMServer. name_prefix must be "vLLM" to help parsing correctly in utils.sh
    deployment = LLMServer.as_deployment(server_config.get_serve_options(name_prefix=f"{args.engine}:")).bind(server_config)
    llm_app = LLMRouter.as_deployment([router_config]).bind([deployment])

    # Run the serve deployment
    serve.start(http_options={"host": "0.0.0.0", "port": args.port})
    logging_config = LoggingConfig(log_level="WARNING")
    serve.run(llm_app, logging_config=logging_config)
    
    while True:
        time.sleep(100)

if __name__ == "__main__":
    main()
