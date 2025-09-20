#!/bin/bash

# Script to convert an environment variable file to JSON.

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

# Output the opening brace for JSON.
echo "{"

# Process the file line by line, storing output in a variable.
output=""
while IFS= read -r line; do
    # Check if the current line contains an equals sign and is not a comment.
    if [[ "$line" == *=* ]] && [[ ! "$line" =~ ^# ]]; then
        # Extract the key (part before '=').
        key="${line%%=*}"
        # Extract the value (part after '=').
        value="${line#*=}"
        # Append the key-value pair in JSON format to the output variable.
        output+="  \"$key\": \"$value\",\n"
    fi
done < "$1"

# Remove the trailing comma from the last key-value pair.
output="${output%,
}"


# Output the JSON content.
echo "$output"

# Output the closing brace for JSON.
echo "}"