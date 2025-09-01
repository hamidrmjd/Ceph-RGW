#!/bin/bash

# Script to list Ceph RGW buckets sorted by size_actual (from rgw.main), with bucket name and user

# Exit on error
set -e

# Function to convert bytes to human-readable format
human_readable() {
    local size=$1
    if [ "$size" -eq 0 ]; then
        echo "0B"
    elif [ "$size" -lt 1024 ]; then
        echo "${size}B"
    elif [ "$size" -lt 1024000 ]; then
        echo "$((size / 1024))K"
    elif [ "$size" -lt 1024000000 ]; then
        echo "$((size / 1024 / 1024))M"
    else
        echo "$((size / 1024 / 1024 / 1024))G"
    fi
}

# Get list of all buckets
BUCKETS=$(radosgw-admin bucket list 2>/dev/null | jq -r '.[]')

if [ -z "$BUCKETS" ]; then
    echo "No buckets found or error fetching bucket list."
    exit 1
fi

# Array to store bucket data
declare -A bucket_data

# Loop through each bucket and get stats
for bucket in $BUCKETS; do
    STATS=$(radosgw-admin bucket stats --bucket="$bucket" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to get stats for bucket '$bucket'. Skipping."
        continue
    fi
    
    # Extract size_actual, default to 0 if usage or rgw.main.size_actual is missing
    SIZE_ACTUAL=$(echo "$STATS" | jq -r '.usage["rgw.main"].size_actual // 0')
    
    # Extract owner
    OWNER=$(echo "$STATS" | jq -r '.owner // "unknown"')
    
    # Store in associative array (key: size_actual, value: bucket|owner)
    bucket_data["$SIZE_ACTUAL"]="${bucket}|${OWNER}"
done

# Print header
echo "Bucket Name | User | Size Actual (Bytes) | Human Readable"
echo "------------|------|--------------------|---------------"

# Sort by size_actual descending and print
for size in $(printf '%s\n' "${!bucket_data[@]}" | sort -nr); do
    info="${bucket_data[$size]}"
    bucket=$(echo "$info" | cut -d'|' -f1)
    owner=$(echo "$info" | cut -d'|' -f2)
    hr_size=$(human_readable "$size")
    printf "%-20s | %-15s | %-18s | %s\n" "$bucket" "$owner" "$size" "$hr_size"
done
