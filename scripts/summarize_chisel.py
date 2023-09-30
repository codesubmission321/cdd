import os
import re
import sys
import csv

BENCHMARK_LIST = ['bzip2-1.0.5', 'chown-8.2', 'date-8.21', 'grep-2.19',
                  'gzip-1.2.4', 'mkdir-5.2.1', 'rm-8.4', 'sort-8.16',
                  'tar-1.14', 'uniq-8.16']
RESULT_PATH = sys.argv[1]

def get_time_from_log(log_file):
    with open(log_file, 'r') as fopen:
        lines = fopen.readlines()

    # Start from the last line and go upwards
    for line in reversed(lines):
        match = re.search(r'Total Time :\s*(\d+)(?:\.\d+)?s', line)
        if match:
            # Extract the time value and return it
            return match.group(1)
    return None

def get_test_num_from_log(log_file):
    with open(log_file, 'r') as fopen:
        lines = fopen.readlines()

    # Start from the last line and go upwards
    for line in reversed(lines):
        match = re.search(r'TestTimes:\s*(\d+)', line)
        if match:
            # Extract the time value and return it
            return match.group(1)
    return None

def get_token_num(file):
    cmd = "~/demystifying_probdd/build/bin/counter %s" % file
    proc = os.popen(cmd)
    output = proc.read()

    match = re.search(r'original tokens:\s*(\d+)', output)
    if match:
        return match.group(1)
    else:
        return None

with open(os.path.join(RESULT_PATH, 'summary.csv'), 'w', newline='') as csvfile:
    CSV_WRITER = csv.writer(csvfile)
    CSV_WRITER.writerow(["target", "time", "token num", "test num"])

    for target in BENCHMARK_LIST:
        row = [target]  # Initialize row with target as the first column
        final_program_path = os.path.join(RESULT_PATH, "%s.c" % target)
        log_file_path = os.path.join(RESULT_PATH, "%s_log.txt" % target)
        if not os.path.isfile(final_program_path) or not os.path.isfile(log_file_path):
            print("%s is not available" % target)
            row.extend([None, None, None])
            CSV_WRITER.writerow(row)  # Write only target if not available
            continue

        token_num = get_token_num(final_program_path)
        time = get_time_from_log(log_file_path)
        test_num = get_test_num_from_log(log_file_path)

        print("target: %s: time: %s, token num: %s, test num: %s"
              % (target, time, token_num, test_num))
        row.extend([time, token_num, test_num])

        CSV_WRITER.writerow(row)
