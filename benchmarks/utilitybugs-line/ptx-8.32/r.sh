#! /bin/bash
UTILITY="ptx"
VERSION="8.32"
BIN_PATH="/home/coq/cdd/benchmarks/utilitybugs/${UTILITY}-${VERSION}/bin/${UTILITY}"

TIMEOUT=30

timeout -s 9 $TIMEOUT $BIN_PATH -G -r < input > out.txt 2>&1
ret=$?
if [ $ret != 137 ]; then
	exit 1
fi

exit 0
