#!/bin/bash

# Get the command and the test folder from the arguments
cmd=$1
test_folder=$2

# Check if the correct number of arguments was provided
if [[ -z "$cmd" || -z "$test_folder" ]]; then
    echo "Usage: $0 <cmd> <test_folder>"
    exit 1
fi

# Check if the test folder exists
if [ ! -d "$test_folder" ]; then
    echo "Test folder $test_folder does not exist."
    exit 1
fi

# Iterate over each file in the test folder
for file in "$test_folder"/*; do
    # Check if it is a file
    if [ -f "$file" ]; then
        echo "Running command on file: $file"

        # Run the command with a timeout of 60 seconds
        timeout 60s $cmd "$file"
        exit_status=$?

        # Check the exit status
        if [ $exit_status -eq 138 ] || [ $exit_status -eq 139 ]; then
            echo "Command returned $exit_status on file: $file"
        elif [ $exit_status -eq 124 ]; then
            echo "Command timed out on file: $file"
        fi
    fi
done

