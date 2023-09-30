#! /bin/bash
root=$(pwd)
cd ${root}/src/antlerinator
pip install .
cd ${root}/src/picire
pip install .
cd ${root}/src/picireny
pip install .
cd ${root}