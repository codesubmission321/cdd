#!/bin/bash

UTILITY="indent"
VERSION="5.17"
BIN_PATH="/home/coq/cdd/benchmarks/utilitybugs/${UTILITY}-${VERSION}/bin/${UTILITY}"

TIMEOUT=30

timeout -s 9 $TIMEOUT valgrind $BIN_PATH -troff input > out.txt 2>&1
ret=$?

if [ $ret != 139 ]; then
    exit 1
fi

tail -n 100 out.txt > temp.txt && mv temp.txt out.txt

# An array containing all the strings to check, each pattern on a new line
check_strings=(
    "Process terminating with default action of signal 11 (SIGSEGV): dumping core"
    "dump_line (io.c:168)"
    "main (indent.c:501)"
    # Add more patterns here if needed
)

# Index of the current string we are looking for
current_index=0

# Reading each line of the log file
while IFS= read -r line
do
    # Check if the current line contains the string at the current index
    if [[ "$line" == *"${check_strings[$current_index]}"* ]]; then
        ((current_index++))

        # Exit if all strings have been found
        if [ $current_index -ge ${#check_strings[@]} ]; then
            break
        fi
    fi
done < out.txt

# If not all strings were found, output a message and exit with code 1
if [ $current_index -lt ${#check_strings[@]} ]; then
    exit 1
fi

rm vgcore.*
rm out.txt
exit 0
