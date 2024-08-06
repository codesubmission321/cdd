import os
import re
import sys

# List of benchmarks
BENCHMARK_LIST = [
    "bzip2-1.0.5", "chown-8.2", "date-8.21", "grep-2.19", 
    "gzip-1.2.4", "mkdir-5.2.1", "rm-8.4", "sort-8.16", 
    "tar-1.14", "uniq-8.16"
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
                        if re.search(r'Running .* - Size', line):
                            # Get total_size from the next line
                            match = re.search(r'Config size: (\d+)', lines[i+1])
                            if match:
                                total_size = int(match.group(1))
                            # Reset history for a new run
                            history = set()
                        if re.search(r'Selected (partition|deletion) size:', line):
                            match = re.search(r'Selected (partition|deletion) size: (\d+)', line)
                            if match:
                                delete_size = int(match.group(2))
                                complement = False  # Default assumption
                                repeated = False  # Reset repeated flag
                                idx = ''
                                # Check the next line for Try deleting information
                                match_delete = re.search(r'Try deleting\(complement of\): (\[.*?\])', lines[i+1])
                                if match_delete:
                                    complement = True
                                    idx = match_delete.group(1)
                                else:
                                    match_delete = re.search(r'Try deleting: (\[.*?\])', lines[i+1])
                                    if match_delete:
                                        idx = match_delete.group(1)
                                        repeated = idx in history
                                        history.add(idx)
                                    else:
                                        continue
                                # Check for deletion success in the line after the Try deleting line
                                if 'Deleted' in lines[i+2]:
                                    status = 'success'
                                else:
                                    status = 'fail'
                                output_file.write(f"{benchmark}, {total_size}, {delete_size}, {complement}, {repeated}, {status}\n")
            except FileNotFoundError:
                print(f"Log file for {benchmark} not found in {result_path}")

if __name__ == "__main__":
    process_log_files(BENCHMARK_LIST, RESULT_PATH)
