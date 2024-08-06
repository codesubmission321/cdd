#! /bin/bash
UTILITY="flex"
VERSION="2.5.39"
BIN_PATH="/home/coq/cdd/benchmarks/utilitybugs/${UTILITY}-${VERSION}/bin/${UTILITY}"

TIMEOUT=30

timeout -s 9 $TIMEOUT $BIN_PATH < input > out.txt 2>&1
ret=$?
if [ $ret != 139 ]; then
	exit 1
fi

exit 0
