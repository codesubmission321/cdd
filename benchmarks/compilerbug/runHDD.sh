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
root="/benchmarks/compilerbugs/"

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
 for i in 'clang-22382' 'clang-22704' 'clang-23309' 'clang-23353' 'clang-25900' 'clang-26760' 'clang-27137' 'clang-27747' 'clang-31259' 'gcc-59903' 'gcc-60116' 'gcc-61383' 'gcc-61917' 'gcc-64990' 'gcc-65383' 'gcc-66186' 'gcc-66375' 'gcc-70127' 'gcc-70586' 'gcc-71626';
do
    version=$(git rev-parse --short HEAD)
    target=$i
    if [ -d "${out_dir}/${target}-hdd" ] || [ -f "${out_dir}/log_hdd_${target}" ]; then
	echo "already done ${target}"
        continue
    fi	    
    echo "running $target"

    # create tmp folder
    work_dir=`mktemp -d -p "$cwd"`
    echo "created tmp dir ${work_dir}"
    cp $root/$target/r.sh $work_dir
    cp $root/$target/small.c.origin.c $work_dir/small.c
    cp $root/C.g4 $work_dir
    cd $work_dir

    # init log and data path
    log_path=${out_dir}/log_hdd_${target}
    data_path=${out_dir}/${target}-hdd
    echo $version > $log_path
    /hdd_ProbDD/anaconda2/bin/picireny -i small.c --test r.sh --srcml:language C --grammar C.g4 --start compilationUnit --disable-cleanup --cache none $1 >> $log_path 2>&1
    # save result, cleanup
    mv small.c.* $data_path
    cd $cwd
    cleanup $work_dir
done


# register the cleanup function to be called on the EXIT signal
#trap "cleanup '${log_path}'" INT
#trap "cleanup '${data_path}'" INT
