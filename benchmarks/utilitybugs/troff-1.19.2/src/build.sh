#! /bin/bash
mkdir -p build/
./configure --prefix=$(pwd)/build/ "CFLAGS=-g -O0"
make -j8
make install
