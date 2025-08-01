import requests
import sys
from datetime import datetime
from dateutil.parser import isoparse
import subprocess

# SGLang Docker repository URL
DOCKER_REPO = "rocm/sgl-dev"
PAGE_SIZE = 100
URL = f"https://hub.docker.com/v2/repositories/{DOCKER_REPO}/tags?page_size={PAGE_SIZE}"

def get_latest_mi30x_srt_tag():
    """
    Fetches the latest SGLang Docker image tag with 'mi30x' and 'srt' substrings.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch tags from {URL}: {e}", file=sys.stderr)
        sys.exit(1)

    tags = response.json().get("results", [])
    
    # Filter for tags that contain both 'mi30x' and 'srt'
    filtered_tags = [
        {
            "name": tag["name"],
            "last_updated": isoparse(tag["last_updated"])
        }
        for tag in tags
        if "mi30x" in tag["name"] and "srt" in tag["name"]
    ]

    if not filtered_tags:
        print("No tags with both 'mi30x' and 'srt' found.", file=sys.stderr)
        sys.exit(1)

    # Find the latest tag based on the 'last_updated' timestamp
    latest = max(filtered_tags, key=lambda x: x["last_updated"])
    return latest["name"]

if __name__ == "__main__":
    latest_tag = get_latest_mi30x_srt_tag()
    full_image_name = f"{DOCKER_REPO}:{latest_tag}"

    try:
        subprocess.run(["docker", "pull", full_image_name], check=True, capture_output=True, text=True)
        print(f"{full_image_name}")
    except subprocess.CalledProcessError as e:
        print(f"Docker pull failed with error code {e.returncode}:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)