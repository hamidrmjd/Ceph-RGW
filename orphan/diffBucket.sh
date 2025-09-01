#!/bin/bash

# Check if input files are provided as arguments
if [ $# -ne 2 ]; then
    echo "Error: Please provide two input files"
    echo "Usage: $0 <fileA> <fileB>"
    exit 1
fi

FILEA="$1"
FILEB="$2"
OUTPUT_FILE="final.orphan"

# Check if input files exist
if [ ! -f "$FILEA" ]; then
    echo "Error: $FILEA does not exist"
    exit 1
fi
if [ ! -f "$FILEB" ]; then
    echo "Error: $FILEB does not exist"
    exit 1
fi

# Clear the output file if it already exists
> "$OUTPUT_FILE"

# Read each line from fileA and check if it exists in fileB
while IFS= read -r line; do
    # Skip empty lines
    [ -z "$line" ] && continue
    # Use grep to check if the line exists in fileB (exact match)
    if ! grep "$line" "$FILEB" > /dev/null; then
        echo "$line" >> "$OUTPUT_FILE"
    fi
done < "$FILEA"

# Check if output file is empty
if [ -s "$OUTPUT_FILE" ]; then
    echo "Objects not found in $FILEB written to $OUTPUT_FILE"
else
    echo "No orphaned objects found. $OUTPUT_FILE is empty."
    rm "$OUTPUT_FILE"
fi
