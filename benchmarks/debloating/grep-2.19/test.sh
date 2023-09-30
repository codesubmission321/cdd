#!/bin/bash
export CC=clang-7
export CHISEL_BENCHMARK_HOME=/home/coq/demystifying_probdd/benchmarks/debloating
export NAME=grep-2.19
export BENCHMARK_DIR=$CHISEL_BENCHMARK_HOME/$NAME/
export SRC=./$NAME.c
export ORIGIN_BIN=$BENCHMARK_DIR/$NAME.origin
export REDUCED_BIN=./$NAME.reduced
export TIMEOUT="-k 5 5"
export LOG=./log.txt

source $CHISEL_BENCHMARK_HOME/test-base.sh

function clean() {
  rm -f $REDUCED_BIN $LOG file log2
  rm -rf gt-*
  rm -f lists.txt
  return 0
}

function compile() {
  if [[ $1 == "-fsanitize=memory -fsanitize-memory-use-after-dtor" ]]; then
    CFLAGS="-w $1 -lpcre"
  else
    CFLAGS="-w $1 -D __msan_unpoison(s,z) -lpcre"
  fi
  $CC $SRC $CFLAGS -o $REDUCED_BIN >&$LOG || exit 1
  return 0
}

function desired() {
  { timeout $TIMEOUT $REDUCED_BIN "a" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  $ORIGIN_BIN "a" $BENCHMARK_DIR/input2 >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "a" -v -H -r $BENCHMARK_DIR/input_dir; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "a" -v -H -r $BENCHMARK_DIR/input_dir; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -h -r $BENCHMARK_DIR/input_dir; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "1" -h -r $BENCHMARK_DIR/input_dir; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -n "si" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -n "si" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -l; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "1" -r $BENCHMARK_DIR/input_dir -l; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -L; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "1" -r $BENCHMARK_DIR/input_dir -L; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "randomtext" -r $BENCHMARK_DIR/input_dir -c; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "randomtext" -r $BENCHMARK_DIR/input_dir -c; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -o [r][a][n][d]* $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -o [r][a][n][d]* $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -q; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "1" -r $BENCHMARK_DIR/input_dir -q; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -s; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "1" -r $BENCHMARK_DIR/input_dir -s; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -v "a" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -v "a" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -i "Si" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -i "Si" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -w "Si" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -w "Si" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -x "Don't" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -x "Don't" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -F "randomtext*" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -F "randomtext*" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E "randomtext*" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -E "randomtext*" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "ye " $BENCHMARK_DIR/input; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "ye " $BENCHMARK_DIR/input; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "cold" $BENCHMARK_DIR/input; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN "cold" $BENCHMARK_DIR/input; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "not exist" $BENCHMARK_DIR/input; } >&$LOG
  { timeout $TIMEOUT $ORIGIN_BIN "not exist" $BENCHMARK_DIR/input; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^D $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN ^D $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN .$ $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN .$ $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN \^ $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN \^ $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN \^$ $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN \^$ $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^[AEIOU] $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN ^[AEIOU] $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^[^AEIOU] $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN ^[^AEIOU] $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E "free[^[:space:]]+" $BENCHMARK_DIR/input2; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -E "free[^[:space:]]+" $BENCHMARK_DIR/input2; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E '\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' $BENCHMARK_DIR/input; } >&$LOG || exit 1
  { timeout $TIMEOUT $ORIGIN_BIN -E '\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' $BENCHMARK_DIR/input; } >&log2
  diff -q $LOG log2 >&/dev/null || exit 1
  return 0
}

function desired_disaster() {
  case $1 in
  memory)
    MESSAGE="memory exhausted"
    ;;
  file)
    MESSAGE="write error"
    ;;
  *)
    return 1
    ;;
  esac

  { timeout $TIMEOUT $REDUCED_BIN "a" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "a" -v -H -r $BENCHMARK_DIR/input_dir; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -h -r $BENCHMARK_DIR/input_dir; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -n "si" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -l; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -L; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "randomtext" -r $BENCHMARK_DIR/input_dir -c; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -o [r][a][n][d]* $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -q; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "1" -r $BENCHMARK_DIR/input_dir -s; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -v "a" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -i "Si" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -w "Si" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -x "Don't" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -F "randomtext*" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E "randomtext*" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "ye " $BENCHMARK_DIR/input; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "cold" $BENCHMARK_DIR/input; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN "not exist" $BENCHMARK_DIR/input; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^D $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN .$ $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN \^ $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN \^$ $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^[AEIOU] $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN ^[^AEIOU] $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E "free[^[:space:]]+" $BENCHMARK_DIR/input2; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -E '\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' $BENCHMARK_DIR/input; } >&$LOG
  grep -q -E "$MESSAGE" $LOG || exit 1

  return 0
}

function infinite() {
  r=$1
  /bin/grep "Sanitizer" $LOG >&/dev/null && return 0
  if [[ $r -eq 124 ]]; then # timeout
    return 0
  else
    return 1
  fi
}

function outputcheckerror() {
  r="$1"
  if grep -q -E "$r" $LOG; then
    return 1
  fi
  return 0
}

OPT=("-G" "--basic-regexp" "-P" "--perl-regexp" "-e" "-z" "--null-data"
  "-V" "--version" "--help" "-b" "--byte-offset" "--line-buffered"
  "-a" "--text" "-I" "-R" "--dereference-recursive"
  "-T" "--initial-tab" "-Z" "--null" "-U"
  "-binary" "-u" "--unix-byte-offsets")
function undesired() {
  { timeout $TIMEOUT $REDUCED_BIN; } >&$LOG
  err=$?
  outputcheckerror "OPTION" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN notexist; } >&$LOG # infite loop
  infinite $r && exit 1
  { $timeout $REDUCED_BIN notexist1 notexit2 notexist3; } >&$LOG
  err=$?
  outputcheckerror "No such file or directory" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN "weird"; } >&$LOG
  infinite $r && exit 1
  # cheap
  for opt in ${OPT[@]}; do
    { timeout 0.2 $REDUCED_BIN a $opt $BENCHMARK_DIR/input; } >&$LOG
    crash $? && exit 1
  done
  # expensive
  { timeout 0.5 $REDUCED_BIN a -f $BENCHMARK_DIR/input; } >&$LOG
  crash $? && exit 1

  { timeout $TIMEOUT $REDUCED_BIN a -A $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "input: invalid context length argument" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN a -B $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "input: invalid context length argument" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN a -C $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "input: invalid context length argument" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN a -m $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "invalid max count" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN a -d $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "invalid argument" && exit 1
  crash $err && exit 1
  { timeout $TIMEOUT $REDUCED_BIN a -D $BENCHMARK_DIR/input; } >&$LOG
  outputcheckerror "unknown devices method" && exit 1
  crash $err && exit 1

  export srcdir=$BENCHMARK_HOME/tests
  export abs_top_srcdir=$BENCHMARK_HOME
  export PATH_BK=$PATH
  export PATH="$(pwd):$PATH"
  for t in $(find $BENCHMARK_DIR/tests/ -maxdepth 1 -perm -100 -type f); do
    { timeout 1 $t; } >&$LOG
    crash $? && exit 1
  done
  export PATH=$PATH_BK
  return 0
}

main
