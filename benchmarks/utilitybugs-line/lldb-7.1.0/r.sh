#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/coq/anaconda3/lib

UTILITY="lldb"
VERSION="7.1.0"
BIN_PATH="${UTILITY}"

TIMEOUT=30

timeout -s 9 $TIMEOUT $BIN_PATH < input > out.txt 2>&1
ret=$?

if [ $ret != 139 ]; then
    exit 1
fi

exit 0
