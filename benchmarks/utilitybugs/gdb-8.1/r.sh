#!/bin/bash

UTILITY="gdb"
VERSION="8.1"
BIN_PATH="/home/coq/cdd/benchmarks/utilitybugs/${UTILITY}-${VERSION}/bin/${UTILITY}"

TIMEOUT=30

timeout -s 9 $TIMEOUT valgrind $BIN_PATH < input > out.txt 2>&1
ret=$?

if [ $ret != 139 ]; then
    exit 1
fi

tail -n 100 out.txt > temp.txt && mv temp.txt out.txt

# An array containing all the strings to check, each pattern on a new line
check_strings=(
    "Process terminating with default action of signal 11 (SIGSEGV): dumping core"
    "strncmp (vg_replace_strmem.c:648)"
    "startswith (common-utils.h:109)"
    "is_ada_operator(char const*) (linespec.c:510)"
    "parse_linespec(ls_parser*, char const*, symbol_name_match_type) (linespec.c:2539)"
    "event_location_to_sals(ls_parser*, event_location const*) (linespec.c:3209)"
    "decode_line_1(event_location const*, int, program_space*, symtab*, int) (linespec.c:3362)"
    "decode_line_with_current_source(char const*, int) (linespec.c:3383)"
    "clear_command(char const*, int) (breakpoint.c:11474)"
    "cmd_func(cmd_list_element*, char const*, int) (cli-decode.c:1886)"
    "execute_command(char const*, int) (top.c:630)"
    "command_handler(char const*) (event-top.c:583)"
    "command_line_handler(char*) (event-top.c:774)"
    "gdb_readline_no_editing_callback(void*) (event-top.c:849)"
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
