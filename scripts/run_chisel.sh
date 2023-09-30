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
benchmark_path=${root}/benchmarks/debloating

${root}/scripts/build_chisel.sh

# output folder
out_folder_name=$(date +"%Y%m%d%H%M%S")
out_path="${root}/results/chisel/${out_folder_name}"
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

# save the version and args_for_chisel
config_path=${out_path}/config.txt
echo "${version}" > ${config_path}

echo -n "$0 " >> ${config_path}
for arg in "$@"; do
  if [[ $arg == --args_for_chisel || $arg == --benchmark || $arg == --max_jobs ]]; then
    echo -n "$arg "
  else
    echo -n "\"$arg\" "
  fi
done >> ${config_path}
echo "" >> ${config_path}


# init arguments
args_for_chisel=""
benchmarks=('bzip2-1.0.5' 'chown-8.2' 'date-8.21' 'grep-2.19' 'gzip-1.2.4' 'mkdir-5.2.1' 'rm-8.4' 'tar-1.14' 'sort-8.16' 'uniq-8.16')
max_jobs=1

# --args_for_chisel is mandatory
if [ $# -eq 0 ]; then
  echo "Usage: $0 --args_for_chisel STRING [--benchmark benchmark_name] [--max_jobs MAX_JOBS_COUNT]"
  exit 1
fi

# parse the command line
while (( "$#" )); do
  case "$1" in
    --args_for_chisel)
      args_for_chisel=$2
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

# check whether --args_for_chisel is set
if [ -z "$args_for_chisel" ]; then
  echo "The --args_for_chisel option is mandatory."
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
        log_path=${out_path}/${benchmark}_log.txt
        data_path=${out_path}/${benchmark}.c

        if [ -f ${log_path} ] || [ -f ${data_path} ]; then
            echo "already done ${benchmark}"
            continue
        fi	    
        echo "running $benchmark"

        # create tmp folder
        work_path=`mktemp -d -p ${out_path}`
        echo "created tmp folder ${work_path} for ${benchmark}"
        cp -r ${benchmark_path}/$benchmark/* $work_path
        cd $work_path
        mkdir ./output_dir

        /home/coq/demystifying_probdd/build/bin/chisel --skip_local_dep --skip_global_dep --skip_dce --output_dir ./output_dir ${args_for_chisel} ./test.sh ./${benchmark}.c

        # save result, cleanup
        mv ./output_dir/full_log.txt ${log_path} 
        mv ${benchmark}.c.chisel.c ${data_path}
        cd ${root}
        cleanup ${work_path}
    } &

    ((running_jobs++))
done

# wait for the last few tasks to complete
wait

python ${root}/scripts/summarize_chisel.py ${out_path}
