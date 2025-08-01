#!/bin/bash
# set -x

# Set the model folder directory
MODEL_FOLDER="/data/huggingface/hub"
echo "Save model under $MODEL_FOLDER"
mkdir -p $MODEL_FOLDER
# Consider moving login outside the loop if it's always the same token
huggingface-cli login

# Define a function to download the models
download_model() {
    MODEL_NAME=$1
    LOCAL_DIR=$MODEL_FOLDER/$MODEL_NAME
    EXCLUDE_PATTERN=$2 # Renamed for clarity, though $2 is fine

    # Start with the base download command
    DOWNLOAD_CMD="huggingface-cli download \"$MODEL_NAME\" --local-dir \"$LOCAL_DIR\" --resume-download"

    # Append the --exclude flag ONLY if EXCLUDE_PATTERN is not empty
    if [ -n "$EXCLUDE_PATTERN" ]; then
        DOWNLOAD_CMD="${DOWNLOAD_CMD} --exclude \"$EXCLUDE_PATTERN\""
    fi

    # Check if the model already exists
    if [ ! -d "$LOCAL_DIR" ]; then
        echo "Downloading $MODEL_NAME to $LOCAL_DIR..."
        # Use eval to correctly interpret the constructed command string with quotes
        eval $DOWNLOAD_CMD &
    else
        echo "$MODEL_NAME already downloaded, skipping..."
    fi
}

download_model "meta-llama/Llama-3.1-8B-Instruct"  "original/*"
download_model "meta-llama/Llama-3.3-70B-Instruct"  "original/*"
download_model "meta-llama/Llama-4-Scout-17B-16E-Instruct"  "original/*"

# Wait for all background processes to finish
wait
echo "All downloads completed."