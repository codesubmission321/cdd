#! /bin/bash
root=/home/coq/demystifying_probdd
cd ${root}/src/chisel
cmake -S . -B ${root}/build
cd ${root}/build
make
cd ${root}/benchmarks/debloating
make
cd ${root}
