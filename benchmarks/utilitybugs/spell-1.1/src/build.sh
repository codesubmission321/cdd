#! /bin/bash
mkdir -p build/
./configure --prefix=$(pwd)/build/
make -j8
make install
