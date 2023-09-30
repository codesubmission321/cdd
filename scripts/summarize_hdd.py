import os
import re
import sys
import csv

BENCHMARK_LIST = ['clang-22382', 'clang-22704', 'clang-23309', 'clang-23353',
                  'clang-25900', 'clang-26760', 'clang-27137', 'clang-27747',
                  'clang-31259', 'gcc-59903', 'gcc-60116', 'gcc-61383',
                  'gcc-61917', 'gcc-64990', 'gcc-65383', 'gcc-66186',
                  'gcc-66375', 'gcc-70127', 'gcc-70586', 'gcc-71626']
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
    cmd = "~/demystifying_probdd/build/bin/counter %s" % file
    proc = os.popen(cmd)
    output = proc.read()

    match = re.search(r'original tokens:\s*(\d+)', output)
    if match:
        return match.group(1)
    else:
        return None

def get_iteration(res_path):
    return len(os.listdir(res_path))

def get_test_num(res_path):
    return file_count(res_path, "small.c")

def file_count(path, extension):
    count = 0
    for _, _, files in os.walk(path):
        count += sum(f.endswith(extension) for f in files)
    return count

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
        final_program_path = os.path.join(collect_path, "small.c")
        if os.path.isfile(final_program_path):
            token_num = get_token_num(final_program_path)
            log_file = os.path.join(RESULT_PATH, "log_" + target + ".txt")
            time = get_time_from_log(log_file)
            intermidiate_result_path = os.path.join(collect_path, "tests")
            iteration = get_iteration(intermidiate_result_path)
            test_num = get_test_num(intermidiate_result_path)

            print("target: %s: time: %s, token num: %s, iteration: %d, test num: %d"
                  % (target, time, token_num, iteration, test_num))
            row.extend([time, token_num, iteration, test_num])
        else:
            print("%s: small.c not available" % target)
            row.extend([None, None, None, None])

        CSV_WRITER.writerow(row)
