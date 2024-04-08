#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <script_file> <log_file>"
    exit 1
fi

# Assign the paths of the script file and log file to variables
script_file=$1
log_file=$2

# Check if the script file exists
if [ ! -f "$script_file" ]; then
    echo "Script file not found: $script_file"
    exit 1
fi

# Check if the log file exists, if not, inform that a new file will be created
if [ ! -f "$log_file" ]; then
    echo "Log file not found: $log_file, a new log file will be created."
fi

# Use sed to insert 'date >> log_file' after the shebang line (#! /bin/bash or #!/bin/bash)
sed -i '1 {
    /^#!\/bin\/bash/ {
        a\
date >> '"$log_file"'
        b
    }
    /^#! \/bin\/bash/ {
        a\
date >> '"$log_file"'
    }
}' "$script_file"

# If the shebang line is not found, insert at the beginning of the file
if ! grep -qE '^#! ?/bin/bash' "$script_file"; then
    sed -i '1i date >> '"$log_file" "$script_file"
fi
