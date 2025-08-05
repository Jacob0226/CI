import argparse
import json
import os
import sys

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Record model accuracy scores.")
    parser.add_argument("--engine", type=str, required=True, choices=["vLLM", "SGLang"],
                        help="The name of the engine used")
    parser.add_argument("--model", type=str, required=True, help="The name of the model")
    parser.add_argument("--acc", type=float, required=False, help="Accuracy number")
    parser.add_argument("--acc-path", type=str, required=False, help="The path to the accuracy report JSON file.")
    return parser.parse_args()

def get_accuracy_from_json(file_path):
    """Extract the accuracy score from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON format.", file=sys.stderr)
        return None

    return data['score']

def main():
    """Main function to run the script logic."""
    args = parse_args()

    if args.engine == "SGLang":
        accuracy_score = args.acc
        dataset="gsm8k"
    elif args.engine == "vLLM":
        if not os.path.exists(args.acc_path):
            print(f"Error: The specified path does not exist: '{args.acc_path}'", file=sys.stderr)
            sys.exit(1)
        accuracy_score = get_accuracy_from_json(args.acc_path)
        dataset=os.path.basename(args.acc_path).split('.')[0]

    if accuracy_score is not None:
        print("---------- Accuracy Test Report ----------")
        print(f"Engine: {args.engine}")
        print(f"Model: {args.model}")
        print(f"Dataset: {dataset}")
        print(f"Accuracy Score: {accuracy_score}")
        print("----------------------------------------")
    else:
        print("Failed to retrieve the accuracy score. Please check the error messages.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

'''
# vLLM
python3 RecordAccuracy.py --engine vLLM --model meta-llama/Llama-3.1-8B-Instruct \
    --acc-path ./outputs/20250804_090128/reports/Llama-3.1-8B-Instruct/gsm8k.json
# SGLang
python3 RecordAccuracy.py --engine SGLang --model meta-llama/Llama-3.1-8B-Instruct --acc 0.5


'''