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
benchmark_path=${root}/benchmarks/utilitybugs-line

${root}/scripts/build_hdd.sh

# output folder
out_folder_name=$(date +"%Y%m%d%H%M%S")
out_path="${root}/results/utilitybugs-line/${out_folder_name}"
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

# save the version and args_for_tool
config_path=${out_path}/config.txt
echo "${version}" > ${config_path}

echo -n "$0 " >> ${config_path}
for arg in "$@"; do
  if [[ $arg == --args_for_tool || $arg == --benchmark || $arg == --max_jobs ]]; then
    echo -n "$arg "
  else
    echo -n "\"$arg\" "
  fi
done >> ${config_path}
echo "" >> ${config_path}


# init arguments
args_for_tool=""
benchmarks=('as-2.30' 'bison-3.0.4' 'checknr-8.1' 'ctags-8.4' 'dc-1.3' 'dc-1.4' 'flex-2.5.39' 'gdb-8.1' 'indent-5.17' 'lldb-7.1.0' 'ptx-8.32' 'spell-1.1' 'troff-1.19.2')
max_jobs=1

# --args_for_tool is mandatory
if [ $# -eq 0 ]; then
  echo "Usage: $0 --args_for_tool STRING [--benchmark benchmark_name] [--max_jobs MAX_JOBS_COUNT]"
  exit 1
fi

# parse the command line
while (( "$#" )); do
  case "$1" in
    --args_for_tool)
      args_for_tool=$2
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

# check whether --args_for_tool is set
if [ -z "$args_for_tool" ]; then
  echo "The --args_for_tool option is mandatory."
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
        result_path=${out_path}/result_${benchmark}
        query_stat_path=${out_path}/query_stat_${benchmark}.txt

        if [ -f ${log_path} ] || [ -d ${result_path} ]; then
            echo "already done ${benchmark}"
            continue
        fi	    
        echo "running ${benchmark}"

        # create tmp folder
        work_path=`mktemp -d -p ${out_path}`
        echo "created tmp folder ${work_path} for ${benchmark}"
        cp ${benchmark_path}/${benchmark}/r.sh $work_path
        # insert counter to property test
        touch $query_stat_path
        /home/coq/cdd/scripts/insert_counter.sh $work_path/r.sh $query_stat_path
        
        cp ${benchmark_path}/${benchmark}/input $work_path/input
        cd $work_path

        # record picireny version and run the benchmark
        picire --version > ${log_path}
        timeout -s 9 10800s picire -i input --test r.sh --cache none -j 1 -u 1 ${args_for_tool} >> ${log_path} 2>&1
        ret=$?
        if [ $ret -eq 137 ]; then
          echo "time out" >> "${log_path}"
          echo "execution time: 10800s" >> "${log_path}"
        fi
        # save result, cleanup
        mv input.* ${result_path}
        cd ${root}
        cleanup ${work_path}
    } &

    ((running_jobs++))
done

# wait for the last few tasks to complete
wait

python ${root}/scripts/summarize_line_reduction.py ${out_path}
python ${root}/scripts/cleanup_line_reduction.py ${out_path}
