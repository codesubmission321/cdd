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
        match = re.search(r'execution time:\s*(\d+)(?:\.\d+)?', line)
        if match:
            # Extract the time value and return it
            return match.group(1)
    return None


def get_token_num(file):
    cmd = "java -jar ~/cdd/tools/token_counter.jar %s" % file
    proc = os.popen(cmd)
    output = proc.read()

    # Split the output into lines and get the last line
    lines = output.strip().split('\n')
    last_line = lines[-1] if lines else ''

    # Search for a number in the last line
    match = re.search(r'(\d+)', last_line)
    if match:
        return match.group(1)
    else:
        return None


def get_test_num(log_file):
    with open(log_file, "r") as f:
        queries = f.readlines()
    return len(queries)


with open(os.path.join(RESULT_PATH, 'summary.csv'), 'w', newline='') as csvfile:
    CSV_WRITER = csv.writer(csvfile)
    CSV_WRITER.writerow(["target", "time", "token num", "test num"])

    for target in BENCHMARK_LIST:
        row = [target]  # Initialize row with target as the first column
        collect_path = os.path.join(RESULT_PATH, "result_" + target)
        if not os.path.exists(collect_path):
            print("%s is not available" % target)
            row.extend([None, None, None])
            CSV_WRITER.writerow(row)  # Write only target if not available
            continue

        final_program_path = os.path.join(collect_path, target + ".c")

        if os.path.isfile(final_program_path):
            token_num = get_token_num(final_program_path)
            log_file = os.path.join(RESULT_PATH, "log_" + target + ".txt")
            query_stat_file = os.path.join(RESULT_PATH, "query_stat_" + target + ".txt")
            time = get_time_from_log(log_file)
            test_num = get_test_num(query_stat_file)
            print("target: %s: time: %s, token num: %s, test num: %d"
                  % (target, time, token_num, test_num))
            row.extend([time, token_num, test_num])
        else:
            print("%s: result not available" % target)
            row.extend([None, None, None])

        CSV_WRITER.writerow(row)
