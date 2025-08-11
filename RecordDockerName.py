import argparse
import json
import os
import sys

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Record model accuracy scores.")
    parser.add_argument("--json-file", type=str, required=True, help="The json file of saving docker names")
    parser.add_argument("--vLLM", type=str, required=True, help="vLLM docker name")
    parser.add_argument("--SGLang", type=str, required=True, help="SGLang docker name")
    return parser.parse_args()


def main():
    """Main function to run the script logic."""
    args = parse_args()

    # Save docker name
    print(os.path.exists(args.json_file))
    if not os.path.exists(args.json_file):
        data = dict()
    else:
        with open(args.json_file, "r") as f:
            data = json.load(f)

    data["vLLM Docker"] = args.vLLM
    data["SGLang Docker"] = args.SGLang
    with open(args.json_file, "w") as f:
        json.dump(data, f, indent=4)
        print(f"Docker names are saved successfully to '{args.json_file}'.")

if __name__ == "__main__":
    main()

'''
python3 RecordDockerName.py \
    --json-file Result/2025-08-11/Result.json \
    --vLLM rocm/vllm-dev:nightly_main_20250811 \
    --SGLang lmsysorg/sglang:v0.5.0rc0-rocm630-mi30x-srt


'''