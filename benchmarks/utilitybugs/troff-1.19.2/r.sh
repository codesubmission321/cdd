#!/bin/bash

UTILITY="troff"
VERSION="1.19.2"
BIN_PATH="/home/coq/cdd/benchmarks/utilitybugs/${UTILITY}-${VERSION}/bin/${UTILITY}"
export GROFF_FONT_PATH=/usr/local/share/groff/1.19.2/

TIMEOUT=30

timeout -s 9 $TIMEOUT valgrind $BIN_PATH input > out.txt 2>&1
ret=$?

if [ $ret != 139 ]; then
    exit 1
fi

# An array containing all the strings to check, each pattern on a new line
check_strings=(
    "Process terminating with default action of signal 11 (SIGSEGV): dumping core"
    "font_info::get_tfont(font_size, int, int, int) (node.cpp:282)"
    "special_node::special_node(macro const&, int) (node.cpp:3894)"
    "do_special (input.cpp:5457)"
    "token::next() (input.cpp:2210)"
    "process_input_stack() (input.cpp:2866)"
    "process_input_file(char const*) (input.cpp:7804)"
    "main (input.cpp:8112)"
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
exit 0
