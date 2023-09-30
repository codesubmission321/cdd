This is a guidance to introduce structure of Chisel benchmark and how to run Perses on it.

Makefile:
	Commands to build dependencies and original binaries for comparasion.

test-base.sh:
	The framework for property test shared by each case.

lib:
	Dependencies of test cases.

software-version (e.g., date-8.21):
	The folder containing the software to be debloated.
	date-8.21.c contains the compressed source code of date-8.21, i.e., the authors of this benchmark manually merged all files into a single one to facilitate debloating. For original version, please check https://github.com/aspire-project/chisel-bench/tree/master/benchmark.
	test.sh contains the properties to test the functionalities of debloated code.
	datefile is the input file or oracle file required by test.sh. Each test case requires specific inputs/oracles.

Before reduction tasks, run `make` to build the dependencies and original binaries.
