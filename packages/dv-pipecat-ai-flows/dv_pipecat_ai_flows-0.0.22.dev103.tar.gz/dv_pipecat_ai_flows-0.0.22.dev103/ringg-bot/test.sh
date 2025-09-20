#!/bin/bash
# Script to read a file, split each line at '=', and print the keys.
# Check if a filename is provided as a command-line argument.
if [ -z "$1" ]; then 
    echo "Usage: $0 <filename>" 
    exit 1
fi
# Check if the provided file exists and is readable.
if [ ! -r "$1" ]; then 
    echo "Error: File '$1' not found or not readable." 
    exit 1
fi
# Process the file line by line.
while IFS= read -r line; do 
    # Check if the current line contains an equals sign.
    if [[ "$line" == *=* ]]; then 
        # Extract the part of the line before the first '=' (the key).
        key="${line%%=*}" 
        # Print the extracted key.
        echo "$key" 
    fi
done < "$1"