# Artifact for "CDD: A Simple Yet Effective Counter-Based Model for Delta Debugging"

## Introduction

Thank you for evaluating this artifact!

To evaluate this artifact, a Linux machine with [docker](https://docs.docker.com/get-docker/) installed is needed.

### List of Claims Supported by the Artifact

- CDD simplifies ProbDD by substituting probabilities with counters, and thus ease comprehension and implementation.

- On various intial settings, CDD consistently performs comparable to ProbDD, or even better than ProbDD.

### Notes

- All the experiments take long time to finish, so it is recommended to use tools like screen and tmux to manage sessions if the experiments are run on remote server. We also provide flags for multi-processing.

- The evaluation results may not exactly the same as shown in the paper, because both ProbDD and CDD are affected by randomness. Replicating the experiments for multiple times will such impact. However, the deviation should be trivial, and the results should still support the original claims in the paper.

### Docker Environment Setup

1. If docker is not installed, install it by following the [instructions](https://docs.docker.com/get-docker/).
2. Install the docker image.

   ```bash
   docker pull codesubmission/cdd:latest
   # This step might takes a while, mainly depending on the network bandwidth. It also takes up much disk space (nearly 80GB)
   ```

3. Start a container.

   ```bash
   docker container run --cap-add SYS_PTRACE --interactive --tty codesubmission/cdd:latest /bin/bash
   # You should be at /tmp after the above command finishes
   # Your user name should be `coq` and all the following command are executed in docker

   # the root folder of the project is /home/coq/demystifying_probdd
   cd /home/coq/demystifying_probdd
   ```

### Benchmark Suites

In this project,
benchmark suite are in folder `./benchmarks`.

1. `./benchmarks/compilerbug`: 20 cases for program reduction.

2. `./benchmarks/debloating`: 10 cases for software debloating.

### Build the Tools

In the container, run the following commands to build the tools.

```bash
cd /home/coq/demystifying_probdd
./scripts/build_hdd.sh
./scripts/build_chisel.sh
```

### Reproduce RQ1 & RQ2: the Effectiveness and Efficiency of DDMIN, ProbDD and CDD.

1. Evaluate DDMIN, ProbDD and CDD on 20 programs triggering compiler bugs.

   ```bash
   cd /home/coq/demystifying_probdd

   # evaluate algorithms on 20 compiler bugs.

   # ddmin on 20 compiler bugs (around 53 hours given single process)
   ./scripts/run_hdd.sh --args_for_picireny "--dd ddmin"

   # evaluate Probdd (around 25 hours given single process)
   ./scripts/run_hdd.sh --args_for_picireny "--dd probdd"

   # evaluate CDD (around 25 hours given single process)
   ./scripts/run_hdd.sh --args_for_picireny "--dd counterdd"

   # To evaluate on multiple benchmarks concurrently, use the flag --max_jobs, for example:
   ./scripts/run_hdd.sh --args_for_picireny "--dd ddmin" --max_jobs "8"

   # To evaluate a specific benchmark, use the flag --benchmark, for example:
   ./scripts/run_hdd.sh --args_for_picireny "--dd ddmin" --benchmark "clang-22382"
   ```

2. Results and log.

   Note that every time you start `./run_chisel.sh`, a folder named by current timestamp is created in
   `~/demystifying_probdd/results/hdd`.
   For instance, if current time is 2023/09/12,23:06:25, all results produced by this run will be saved in `~/demystifying_probdd/results/hdd/20230912230625/`. Besides, there is a config.txt recording the options in this run, under the folder `20230912230625`.

   Summarize the result in this run.

   ```bash
   cd ~/demystifying_probdd/results/hdd/20230912230625/
   python ~/demystifying_probdd/script/summarize_hdd.py .
   ```

   Then, file `summary.csv` will be saved in `~/demystifying_probdd/results/hdd/20230912230625/`.
   In `summary.csv`, data such as time, final size and query number for each benchmark is displayed.

3. Evaluate DDMIN, ProbDD and CDD on 10 programs in software debloating.

   Similar to how we evaluate algorithms in `compilerbug`, just run `./script/run_chisel.sh` with correct options.

   ```bash
   # ddmin
   ./scripts/run_chisel.sh --args_for_chisel "--algorithm ddmin"
   # ProbDD
   ./scripts/run_chisel.sh --args_for_chisel "--algorithm probdd"
   # CDD
   ./scripts/run_chisel.sh --args_for_chisel "--algorithm counterdd"

   # To run multiple benchmarks concurrently, use --max_jobs
   ./scripts/run_chisel.sh --args_for_chisel "--algorithm ddmin" --max_jobs "8"
   # To run a specific benchmark, use --benchmark
   ./scripts/run_chisel.sh --args_for_chisel "--algorithm ddmin" --benchmark "mkdir-5.2.1"
   ```

   Similarly, results will be stored in a folder named by current timestamp, under `~/results/chisel`. Run `summarize_chisel.py` to generate `summary.csv`.

   ```bash
   cd ~/demystifying_probdd/results/chisel/20230912230625/
   python ~/demystifying_probdd/script/summarize_chisel.py .
   ```

### Reproduce RQ3: Performance of ProbDD and CDD with Different Initial Probabilities

In RQ1 and RQ2, the initial probability is 0.1 by default. In this RQ, we explictly specify different initial probability (0.05, 0.15, 0.2, 0.25) for evaluation. Everything else is the same as RQ1 and RQ2.

```bash
# for 20 cases about compiler bugs
./scripts/run_hdd.sh --args_for_picireny "--dd probdd --init-probability 0.05"
# foe 10 cases about software debloating
./scripts/run_chisel.sh --args_for_chisel "--algorithm ddmin --init_probability 0.05"
```
