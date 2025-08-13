import requests
import sys
from datetime import datetime
from dateutil.parser import isoparse
import subprocess

DOCKER_REPO = "rocm/vllm-dev"
PAGE_SIZE = 100
URL = f"https://hub.docker.com/v2/repositories/{DOCKER_REPO}/tags?page_size={PAGE_SIZE}"

def get_latest_rc_tag():
    try:
        response = requests.get(URL)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch tags: {e}")
        sys.exit(1)

    tags = response.json().get("results", [])
    rc_tags = [
        {
            "name": tag["name"],
            "last_updated": isoparse(tag["last_updated"])
        }
        for tag in tags
        # if "nightly_main" in tag["name"]
        if "rc" in tag["name"] and "base" not in tag["name"]
    ]

    if not rc_tags:
        print("No 'rc' tags found.")
        sys.exit(1)

    latest = max(rc_tags, key=lambda x: x["last_updated"])
    return latest["name"]

if __name__ == "__main__":
    latest_rc = get_latest_rc_tag()
    
    try:
        # run the docker pull command
        subprocess.run(["docker", "pull", f"{DOCKER_REPO}:{latest_rc}"], check=True,
            stdout=sys.stdout, stderr=sys.stderr,)
        print(f"{DOCKER_REPO}:{latest_rc}")
    except subprocess.CalledProcessError as e:
        print(f"Docker pull failed with error code {e.returncode}:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    
    
    