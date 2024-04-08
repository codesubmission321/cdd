#! /bin/bash
root=$(pwd)
cd ${root}
cd ${root}/src/chisel
cmake -S . -B ${root}/build
cd ${root}/build
make
cd ${root}/benchmarks/debloating
make
cd ${root}
