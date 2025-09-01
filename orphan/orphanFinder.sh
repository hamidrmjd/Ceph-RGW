#!/bin/bash

# Check if BUCKETID is provided as an argument
if [ -z "$1" ]; then
    echo "Error: Please provide BUCKETID as an argument"
    echo "Usage: $0 <BUCKETID>"
    exit 1
fi

BUCKETID=$1
OUTPUT_FILE="${BUCKETID}.orphan"

# Run the commands and store outputs in temporary files
rados ls -p HOT | grep "$BUCKETID" > /tmp/rados_ls_output.txt
radosgw-admin bucket radoslist --bucket="$BUCKETID" > /tmp/radosgw_admin_output.txt

# Compare the outputs using diff and save to OUTPUT_FILE
diff /tmp/rados_ls_output.txt /tmp/radosgw_admin_output.txt > "$OUTPUT_FILE"

# Remove "< " prefix from the output file
sed -i 's/^< //g' "$OUTPUT_FILE"

# Clean up temporary files
rm /tmp/rados_ls_output.txt /tmp/radosgw_admin_output.txt

echo "Comparison completed. Output saved to $OUTPUT_FILE"
