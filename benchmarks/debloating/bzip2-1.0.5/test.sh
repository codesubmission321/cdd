#!/bin/bash
export CC=clang-7
export CHISEL_BENCHMARK_HOME=/home/coq/demystifying_probdd/benchmarks/debloating
export NAME=bzip2-1.0.5
export BENCHMARK_DIR=$CHISEL_BENCHMARK_HOME/$NAME
export SRC=./$NAME.c
export ORIGIN_BIN=$BENCHMARK_DIR/$NAME.origin
export REDUCED_BIN=./$NAME.reduced
export TIMEOUT="-k 5 5"
export LOG=./log.txt

source $CHISEL_BENCHMARK_HOME/test-base.sh

function clean() {
  rm -rf -- *.bz2
  rm -rf $LOG $REDUCED_BIN *.bz2 *.rb2 *.tst log foo* bar*
  rm -f \(*\)
  return 0
}

function desired() {
  # -c
  { timeout $TIMEOUT $REDUCED_BIN -c <$BENCHMARK_DIR/references/sample1.ref >sample1.rb2; } &>$LOG || exit 1
  cmp $BENCHMARK_DIR/references/sample1.bz2.ref sample1.rb2 >&/dev/null || exit 1
  # -d
  { timeout $TIMEOUT $REDUCED_BIN -d <$BENCHMARK_DIR/references/sample1.bz2.ref >sample1.tst; } &>$LOG || exit 1
  cmp $BENCHMARK_DIR/references/sample1.ref sample1.tst >&/dev/null || exit 1
  # -f
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -f foo; } >&$LOG || exit 1
  # -t
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -t foo; } >&$LOG && exit 1
  { timeout $TIMEOUT $REDUCED_BIN -t $BENCHMARK_DIR/references/sample1.bz2.ref; } >&$LOG || exit 1
  # -k
  rm foo*
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -k foo; } >&$LOG || exit 1
  test -f foo -a -f foo.bz2 || exit 1
  return 0
}

function default_disaster_mem() {
  # -c
  { timeout $TIMEOUT $REDUCED_BIN -c <$BENCHMARK_DIR/references/sample1.ref >sample1.rb2; } &>$LOG
  grep -q -E "$1" $LOG || exit 1
  # -d
  { timeout $TIMEOUT $REDUCED_BIN -d <$BENCHMARK_DIR/references/sample1.bz2.ref >sample1.tst; } &>$LOG
  grep -q -E "$1" $LOG || exit 1
  # -f
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -f foo; } >&$LOG
  grep -q -E "$1" $LOG || exit 1
  # -t
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -t foo; } >&$LOG
  grep -q -E "$1" $LOG || exit 1

  { timeout $TIMEOUT $REDUCED_BIN -t $BENCHMARK_DIR/references/sample1.bz2.ref; } >&$LOG
  grep -q -E "$1" $LOG || exit 1
  # -k
  rm foo*
  echo "1234" >foo
  { timeout $TIMEOUT $REDUCED_BIN -k foo; } >&$LOG
  grep -q -E "$1" $LOG || exit 1
  return 0
}

function default_disaster_file() {
  # -c
  { timeout $TIMEOUT $REDUCED_BIN -c <$BENCHMARK_DIR/references/sample1.ref >sample1.rb2; } &>$LOG
  grep -q -E "$1" $LOG || exit 1
  # -d
  { timeout $TIMEOUT $REDUCED_BIN -d <$BENCHMARK_DIR/references/sample1.bz2.ref >sample1.tst; } &>$LOG
  grep -q -E "$1" $LOG || exit 1
  return 0
}

OPT1=("-h")
OPT2=("-z" "-q" "-v" "-s" "-1" "-2" "-3" "-4" "-5" "-6" "-7" "-8" "-9")
OPT3=("-L" "-V")
function undesired() {
  { timeout $TIMEOUT $REDUCED_BIN $(cat $BENCHMARK_DIR/crash_input); } &>$LOG
  crash $? && exit 1
  { timeout $TIMEOUT $REDUCED_BIN; } 2>$LOG
  crash $? && exit 1

  # keeping the output in the following cases:

  { timeout $TIMEOUT $REDUCED_BIN notexist; } 2>$LOG
  crash $? && exit 1
  diff -q $BENCHMARK_DIR/references/side0 $LOG >&/dev/null || exit 1
  rm -rf log

  for opt in ${OPT1[@]}; do
    { timeout $TIMEOUT $REDUCED_BIN $opt; } 2>$LOG
    crash $? && exit 1
    diff -q $BENCHMARK_DIR/references/side1 $LOG >&/dev/null || exit 1
    rm -rf log*
  done

  for opt in ${OPT2[@]}; do
    { timeout $TIMEOUT $REDUCED_BIN $opt; } 2>$LOG
    crash $? && exit 1
    diff -q $BENCHMARK_DIR/references/side2 $LOG >&/dev/null || exit 1
    rm -rf log*
  done

  for opt in ${OPT3[@]}; do
    { timeout $TIMEOUT $REDUCED_BIN $opt; } 2>$LOG
    crash $? && exit 1
    diff -q $BENCHMARK_DIR/references/side3 $LOG >&/dev/null || exit 1
    rm -rf log*
  done

  echo "1234" >foo
  $REDUCED_BIN -c <foo >foo.bz2 || exit 1
  for opt in ${OPT2[@]}; do
    { timeout $TIMEOUT $REDUCED_BIN -d $opt <foo.bz2 >sample1.tst; } 2>$LOG
    crash $? && exit 1
    { timeout $TIMEOUT $REDUCED_BIN -c $opt <$BENCHMARK_DIR/references/sample1.ref >sample1.rb2; } 2>$LOG
    crash $? && exit 1
  done

  return 0
}

function desired_disaster() {
  case $1 in
  memory)
    MESSAGE="couldn't allocate enough memory"
    default_disaster_mem "$MESSAGE" || exit 1
    ;;
  file)
    MESSAGE="Bad file descriptor"
    default_disaster_file "$MESSAGE" || exit 1
    ;;
  *)
    return 1
    ;;
  esac
  return 0
}

main
