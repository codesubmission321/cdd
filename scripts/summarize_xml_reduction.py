import os
import re
import sys
import csv

BENCHMARK_LIST = ['xml-071d221-1', 'xml-071d221-2', 'xml-1e9bc83-1', 'xml-1e9bc83-2', 'xml-1e9bc83-3',
                  'xml-1e9bc83-4', 'xml-1e9bc83-5', 'xml-1e9bc83-6', 'xml-1e9bc83-7', 'xml-1e9bc83-8',
                  'xml-1e9bc83-9', 'xml-2d4ec80-1', 'xml-327c8af-1', 'xml-3398ac2-1', 'xml-3398ac2-2',
                  'xml-3398ac2-3', 'xml-3398ac2-4', 'xml-3398ac2-5', 'xml-4c99b96-1', 'xml-4c99b96-10',
                  'xml-4c99b96-11', 'xml-4c99b96-12', 'xml-4c99b96-13', 'xml-4c99b96-14', 'xml-4c99b96-15',
                  'xml-4c99b96-16', 'xml-4c99b96-17', 'xml-4c99b96-18', 'xml-4c99b96-19', 'xml-4c99b96-2',
                  'xml-4c99b96-3', 'xml-4c99b96-4', 'xml-4c99b96-5', 'xml-4c99b96-6', 'xml-4c99b96-7',
                  'xml-4c99b96-8', 'xml-4c99b96-9', 'xml-8ede045-1', 'xml-8ede045-2', 'xml-8ede045-3',
                  'xml-8ede045-4', 'xml-8ede045-5', 'xml-8ede045-6', 'xml-8ede045-7', 'xml-8ede045-8', 'xml-f053486-1']
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


def get_iteration(log_file):
    pattern = re.compile(r"Iteration #(\d+)")
    with open(log_file, 'r') as file:
        lines = file.readlines()
        for line in reversed(lines):
            match = pattern.search(line)
            if match:
                return int(match.group(1)) + 1

    return None


def get_test_num(log_file):
    with open(log_file, "r") as f:
        queries = f.readlines()
    return len(queries)


with open(os.path.join(RESULT_PATH, 'summary.csv'), 'w', newline='') as csvfile:
    CSV_WRITER = csv.writer(csvfile)
    CSV_WRITER.writerow(["target", "time", "token num", "iteration", "test num"])

    for target in BENCHMARK_LIST:
        row = [target]  # Initialize row with target as the first column
        collect_path = os.path.join(RESULT_PATH, "result_" + target)
        if not os.path.exists(collect_path):
            print("%s is not available" % target)
            row.extend([None, None, None, None])
            CSV_WRITER.writerow(row)  # Write only target if not available
            continue

        final_program_finish_path = os.path.join(collect_path, "input.xml")
        final_program_timeout_path = os.path.join(collect_path, "tests", "input.xml")

        if os.path.isfile(final_program_finish_path) or os.path.isfile(final_program_timeout_path):
            final_program_path = final_program_finish_path if os.path.isfile(final_program_finish_path) else final_program_timeout_path
            token_num = get_token_num(final_program_path)
            log_file = os.path.join(RESULT_PATH, "log_" + target + ".txt")
            query_stat_file = os.path.join(RESULT_PATH, "query_stat_" + target + ".txt")
            time = get_time_from_log(log_file)
            iteration = get_iteration(log_file)
            test_num = get_test_num(query_stat_file)
            print("target: %s: time: %s, token num: %s, iteration: %d, test num: %d"
                  % (target, time, token_num, iteration, test_num))
            row.extend([time, token_num, iteration, test_num])
        else:
            print("%s: result not available" % target)
            row.extend([None, None, None, None])

        CSV_WRITER.writerow(row)
