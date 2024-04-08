import os
import re
import sys

# List of benchmarks
BENCHMARK_LIST = [
    'clang-22382', 'clang-22704', 'clang-23309', 'clang-23353',
    'clang-25900', 'clang-26760', 'clang-27137', 'clang-27747',
    'clang-31259', 'gcc-59903', 'gcc-60116', 'gcc-61383',
    'gcc-61917', 'gcc-64990', 'gcc-65383', 'gcc-66186',
    'gcc-66375', 'gcc-70127', 'gcc-70586', 'gcc-71626'
]

# The path to the results directory
RESULT_PATH = sys.argv[1]

def process_log_files(benchmark_list, result_path):
    # Open file to write all trials
    with open('all_deletion_trials.txt', 'w') as output_file:
        for benchmark in benchmark_list:
            log_file_path = os.path.join(result_path, f'log_{benchmark}.txt')
            history = set()  # Track deletion attempts for each benchmark
            try:
                with open(log_file_path, 'r') as file:
                    lines = file.readlines()
                    total_size = 0
                    delete_size = 0
                    complement = False  # Default value for complement
                    repeated = False  # Default value for repeated
                    status = 'fail'  # Default status
                    for i, line in enumerate(lines):
                        if 'Run #0' in line:
                            # Get total_size from the next line
                            match = re.search(r'Config size: (\d+)', lines[i+1])
                            if match:
                                total_size = int(match.group(1))
                            # Reset history for a new run
                            history = set()
                        if 'Try deleting' in line:
                            match = re.search(r'Try deleting (\d+) elements. Idx: (\[.*?\])', line)
                            idx = ''
                            if match:
                                delete_size = int(match.group(1))
                                idx = match.group(2)
                                complement = False  # Default assumption
                                repeated = idx in history
                                history.add(idx)
                            else:
                                match = re.search(r'Try deleting\(complement of\) (\d+) elements', line)
                                if match:
                                    delete_size = total_size - int(match.group(1))
                                    complement = True
                                    repeated = False
                            # Check for deletion success before the next deletion attempt
                            for j in range(i+1, len(lines)):
                                if 'Deleted' in lines[j]:
                                    status = 'success'
                                    break
                                if 'Try deleting' in lines[j]:
                                    status = 'fail'
                                    break
                            output_file.write(f"{benchmark}, {total_size}, {delete_size}, {complement}, {repeated}, {status}\n")
            except FileNotFoundError:
                print(f"Log file for {benchmark} not found in {result_path}")

if __name__ == "__main__":
    process_log_files(BENCHMARK_LIST, RESULT_PATH)
