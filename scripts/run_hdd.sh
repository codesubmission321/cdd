#!/bin/bash
# deletes the temp directory
function cleanup {
  echo "Deleting $1"
  rm -rf $1
}

function clean_unfinished(){
  cleanup $log_path
  cleanup $work_path
}

function handle_interrupt(){
  echo "Interrupt received. Cleaning up and exiting."
  clean_unfinished
  exit 1
}

trap handle_interrupt INT

root=$(pwd)
benchmark_path=${root}/benchmarks/compilerbug

${root}/scripts/build_hdd.sh

# output folder
out_folder_name=$(date +"%Y%m%d%H%M%S")
out_path="${root}/results/hdd/${out_folder_name}"
echo "out_path is ${out_path}"
if [ ! -d "$out_path" ]; then
    mkdir -p $out_path
fi

# check the git version
echo "Checking the current git version."
version="Current git version: $(git rev-parse --short HEAD)."
if [ $? -eq 0 ]; then
  echo "${version}"
else
  echo "No git version available."
fi

# save the version and args_for_picireny
config_path=${out_path}/config.txt
echo "${version}" > ${config_path}

echo -n "$0 " >> ${config_path}
for arg in "$@"; do
  if [[ $arg == --args_for_picireny || $arg == --benchmark || $arg == --max_jobs ]]; then
    echo -n "$arg "
  else
    echo -n "\"$arg\" "
  fi
done >> ${config_path}
echo "" >> ${config_path}


# init arguments
args_for_picireny=""
benchmarks=('clang-22382' 'clang-22704' 'clang-23309' 'clang-23353' 'clang-25900' 'clang-26760' 'clang-27137' 'clang-27747' 'clang-31259' 'gcc-59903' 'gcc-60116' 'gcc-61383' 'gcc-61917' 'gcc-64990' 'gcc-65383' 'gcc-66186' 'gcc-66375' 'gcc-70127' 'gcc-70586' 'gcc-71626')
max_jobs=1

# --args_for_picireny is mandatory
if [ $# -eq 0 ]; then
  echo "Usage: $0 --args_for_picireny STRING [--benchmark benchmark_name] [--max_jobs MAX_JOBS_COUNT]"
  exit 1
fi

# parse the command line
while (( "$#" )); do
  case "$1" in
    --args_for_picireny)
      args_for_picireny=$2
      shift 2
      ;;
    --benchmark)
      benchmarks=($2)
      shift 2
      ;;
    --max_jobs)
      max_jobs=$2
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# check whether --args_for_picireny is set
if [ -z "$args_for_picireny" ]; then
  echo "The --args_for_picireny option is mandatory."
  exit 1
fi

# init the task counter
running_jobs=0

# all benchmarks
for benchmark in "${benchmarks[@]}"; do
    # If the maximum number of concurrent tasks has been reached, wait for one of the tasks to complete.
    while [ $running_jobs -ge $max_jobs ]; do
        wait -n
        ((running_jobs--))
    done

    {
        # init log and data path
        log_path=${out_path}/log_${benchmark}.txt
        data_path=${out_path}/result_${benchmark}

        if [ -d ${log_path} ] || [ -f ${data_path} ]; then
            echo "already done ${benchmark}"
            continue
        fi	    
        echo "running $benchmark"

        # create tmp folder
        work_path=`mktemp -d -p ${out_path}`
        echo "created tmp folder ${work_path} for ${benchmark}"
        cp ${benchmark_path}/$benchmark/r.sh $work_path
        cp ${benchmark_path}/$benchmark/small.c $work_path/small.c
        cp ${benchmark_path}/C.g4 $work_path
        cd $work_path

        # record picireny version and run the benchmark
        picireny --version > ${log_path}
        picireny -i small.c --test r.sh --grammar C.g4 --start compilationUnit --disable-cleanup --cache none --sys-recursion-limit 10000000 ${args_for_picireny} >> ${log_path} 2>&1
        # save result, cleanup
        mv small.c.* ${data_path}
        cd ${root}
        cleanup ${work_path}
    } &

    ((running_jobs++))
done

# wait for the last few tasks to complete
wait

python ${root}/scripts/summarize_hdd.py ${out_path}
python ${root}/scripts/cleanup_hdd.py ${out_path}
