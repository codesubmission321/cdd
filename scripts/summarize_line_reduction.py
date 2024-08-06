import os
import re
import subprocess
import sys
import csv

BENCHMARK_LIST = ['as-2.30', 'bison-3.0.4', 'checknr-8.1', 'ctags-8.4', 'dc-1.3', 'dc-1.4', 'flex-2.5.39',
                  'gdb-8.1', 'indent-5.17', 'lldb-7.1.0', 'ptx-8.32', 'spell-1.1', 'troff-1.19.2']
RESULT_PATH = sys.argv[1]


def get_time_from_log(log_file):
    with open(log_file, 'r') as fopen:
        lines = fopen.readlines()
    line_of_time = lines[-1]
    match = re.search(r'execution time:\s*(\d+)(?:\.\d+)?', line_of_time)
    if match:
        # keep the integer part and remove the decimal part
        return match.group(1)
    else:
        return None


def get_char_num(file):
    return os.path.getsize(file)

def get_line_num(file):
    result = subprocess.run(['wc', '-l', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error counting lines in file {file}: {result.stderr}")
        return None
    # wc -l count the number of newline character, so +1
    return int(result.stdout.strip().split()[0]) + 1

def get_char_num_from_log(file):
    with open(file, 'r') as f:
        lines = f.readlines()

    for line in reversed(lines):
        if 'Config size' in line:
            match = re.search(r'Config size: (\d+)', line)
            if match:
                return int(match.group(1))

    return None


def get_test_num(log_file):
    with open(log_file, "r") as f:
        queries = f.readlines()
    return len(queries)


with open(os.path.join(RESULT_PATH, 'summary.csv'), 'w', newline='') as csvfile:
    CSV_WRITER = csv.writer(csvfile)
    CSV_WRITER.writerow(["target", "time", "line num", "test num"])

    for target in BENCHMARK_LIST:
        row = [target]  # Initialize row with target as the first column
        collect_path = os.path.join(RESULT_PATH, "result_" + target)
        if not os.path.exists(collect_path):
            print("%s is not available" % target)
            row.extend([None, None, None, None])
            CSV_WRITER.writerow(row)  # Write only target if not available
            continue

        final_program_finish_path = os.path.join(collect_path, "input")
        final_program_timeout_path = os.path.join(collect_path, "tests", "input")

        if os.path.isfile(final_program_finish_path) or os.path.isfile(final_program_timeout_path):
            final_program_path = final_program_finish_path if os.path.isfile(final_program_finish_path) else final_program_timeout_path
            line_num = get_line_num(final_program_path)
            log_file = os.path.join(RESULT_PATH, "log_" + target + ".txt")
            query_stat_file = os.path.join(RESULT_PATH, "query_stat_" + target + ".txt")
            time = get_time_from_log(log_file)
            test_num = get_test_num(query_stat_file)
            print("target: %s: time: %s, line num: %s, test num: %d"
                  % (target, time, line_num, test_num))
            row.extend([time, line_num, test_num])
        else:
            print("%s: result not available" % target)
            row.extend([None, None, None, None])

        CSV_WRITER.writerow(row)
