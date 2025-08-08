#!/bin/bash

check_replicas_status() {
    local status_url="$1"
    local engine="$2"
    local replicas_not_ready=""
    local replicas_ready=""

    # Fetch application status JSON
    response_json=$(curl -s -X GET "$status_url")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to fetch application status from $status_url"
        return 1
    fi

    # Extract the deployments section
    deployments_json=$(echo "$response_json" | jq -r '.applications.default.deployments')
    if [ "$deployments_json" == "null" ] || [ -z "$deployments_json" ]; then
        echo "Error: No deployments found in the response."
        return 1
    fi

    # Filter deployments with names starting with $engine
    engine_deployments=$(echo "$deployments_json" | jq --arg eng $engine -c 'with_entries(select(.key | startswith($eng)))')

    # Get the key for the target deployment
    engine_key=$(echo "$deployments_json" | jq --arg eng $engine -r 'keys[] | select(startswith($eng))')

    if [ -z "$engine_key" ]; then
        echo "Error: No deployment starting with $engine found."
        return 1
    fi

    # Extract the deployment info using the dynamic key
    deployment_info=$(echo "$engine_deployments" | jq --arg key "$engine_key" -r '.[$key]')

    # Loop through replicas
    while read -r replica_json; do
        replica_id=$(echo "$replica_json" | jq -r '.replica_id')
        replica_state=$(echo "$replica_json" | jq -r '.state')

        if [[ "$replica_state" != "RUNNING" ]]; then
            replicas_not_ready+="$replica_id "
        else
            replicas_ready+="$replica_id "
        fi
    done < <(echo "$deployment_info" | jq -c '.replicas[]')

    # Output results
    {
        replicas_not_ready=$(IFS=,; echo "${replicas_not_ready[*]}")
        replicas_ready=$(IFS=,; echo "${replicas_ready[*]}")
        echo "Not ready replicas id:"
        echo -e "    $replicas_not_ready"
        echo "Ready replicas id:"
        echo -e "    $replicas_ready"
    }

    if [ -z "$replicas_not_ready" ] && [ -n "$replicas_ready" ]; then
        echo "✅ All replicas are ready."
        return 0
    fi
    return 1
}
