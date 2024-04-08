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
benchmark_path=${root}/benchmarks/xmlprocessorbugs

${root}/scripts/build_hdd.sh

# output folder
out_folder_name=$(date +"%Y%m%d%H%M%S")
out_path="${root}/results/xmlprocessorbugs/${out_folder_name}"
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
benchmarks=('xml-071d221-1' 'xml-071d221-2' 'xml-1e9bc83-1' 'xml-1e9bc83-2' 'xml-1e9bc83-3' 'xml-1e9bc83-4' 'xml-1e9bc83-5' 'xml-1e9bc83-6' 'xml-1e9bc83-7' 'xml-1e9bc83-8' 'xml-1e9bc83-9' 'xml-2d4ec80-1' 'xml-327c8af-1' 'xml-3398ac2-1' 'xml-3398ac2-2' 'xml-3398ac2-3' 'xml-3398ac2-4' 'xml-3398ac2-5' 'xml-4c99b96-1' 'xml-4c99b96-10' 'xml-4c99b96-11' 'xml-4c99b96-12' 'xml-4c99b96-13' 'xml-4c99b96-14' 'xml-4c99b96-15' 'xml-4c99b96-16' 'xml-4c99b96-17' 'xml-4c99b96-18' 'xml-4c99b96-19' 'xml-4c99b96-2' 'xml-4c99b96-3' 'xml-4c99b96-4' 'xml-4c99b96-5' 'xml-4c99b96-6' 'xml-4c99b96-7' 'xml-4c99b96-8' 'xml-4c99b96-9' 'xml-8ede045-1' 'xml-8ede045-2' 'xml-8ede045-3' 'xml-8ede045-4' 'xml-8ede045-5' 'xml-8ede045-6' 'xml-8ede045-7' 'xml-8ede045-8' 'xml-f053486-1')
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
        
        cp ${benchmark_path}/${benchmark}/input.xml $work_path/input.xml
        cp ${benchmark_path}/XMLLexer.g4 $work_path
        cp ${benchmark_path}/XMLParser.g4 $work_path
        cd $work_path

        # record picireny version and run the benchmark
        picire --version > ${log_path}
        timeout -s 9 10800s picireny -i input.xml --test r.sh --grammar XMLLexer.g4 XMLParser.g4 --start document --cache none --sys-recursion-limit 10000000 ${args_for_tool} >> ${log_path} 2>&1
        ret=$?
        if [ $ret -eq 137 ]; then
          echo "time out" >> "${log_path}"
          echo "execution time: 10800s" >> "${log_path}"
        fi
        # save result, cleanup
        mv input.xml.* ${result_path}
        cd ${root}
        cleanup ${work_path}
    } &

    ((running_jobs++))
done

# wait for the last few tasks to complete
wait

python ${root}/scripts/summarize_xml_reduction.py ${out_path}
python ${root}/scripts/cleanup_xml_reduction.py ${out_path}
