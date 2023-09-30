#!/bin/bash
# deletes the temp directory
function cleanup {
  rm -rf $1
  echo "Deleted $work_dir"
}

function clean_unfinished (){
  cleanup $log_path
  cleanup $data_path
}

cwd=$(pwd)
root="/benchmarks/chisel-bench/"

# generate the folder name
version=$(git rev-parse --short HEAD)
options=$1
find="[ |-]+"
replace="_"
option_str=$(echo $options | sed -r "s/${find}/${replace}/g")
out_folder_name="${version}${option_str}"
out_dir="${root}/${out_folder_name}"
echo "out_dir is ${out_dir}"

log_path="init"
data_path="init"
if [ ! -d "$out_dir" ]; then
    mkdir $out_dir
fi

# all cases
 for i in 'bzip2-1.0.5' 'chown-8.2' 'date-8.21' 'gzip-1.2.4' 'mkdir-5.2.1' 'rm-8.4' 'sort-8.16' 'uniq-8.16';
do
    version=$(git rev-parse --short HEAD)
    target=$i
    if [ -d "${out_dir}/${target}-chisel" ] || [ -f "${out_dir}/log_chisel_${target}" ]; then
	echo "already done ${target}"
        continue
    fi	    
    echo "running $target"

    # create tmp folder
    work_dir=`mktemp -d -p "$cwd"`
    echo "created tmp dir ${work_dir}"
    cp -r $root/$target/* $work_dir
    cd $work_dir

    # init log and data path
    log_path=${out_dir}/log_chisel_${target}
    data_path=${out_dir}/${target}-chisel
    echo $version > $log_path
    /chisel_ProbDD/build/bin/chisel --skip_local_dep --skip_global_dep --skip_dce --output_dir ./output_dir $1 ./test.sh ./${target}.c 2>  /dev/null
    # save result, cleanup
    cat ./output_dir/full_log.txt >> $log_path
    mv ${target}.c.chisel.c ${out_dir}/${target}.c
    cd $cwd
    cleanup $work_dir
done


# register the cleanup function to be called on the EXIT signal
#trap "cleanup '${log_path}'" INT
#trap "cleanup '${data_path}'" INT
