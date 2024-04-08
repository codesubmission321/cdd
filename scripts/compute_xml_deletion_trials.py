import os
import re
import sys

# List of benchmarks
BENCHMARK_LIST = ['xml-071d221-1', 'xml-071d221-2', 'xml-1e9bc83-1', 'xml-1e9bc83-2', 'xml-1e9bc83-3',
                  'xml-1e9bc83-4', 'xml-1e9bc83-5', 'xml-1e9bc83-6', 'xml-1e9bc83-7', 'xml-1e9bc83-8',
                  'xml-1e9bc83-9', 'xml-2d4ec80-1', 'xml-327c8af-1', 'xml-3398ac2-1', 'xml-3398ac2-2',
                  'xml-3398ac2-3', 'xml-3398ac2-4', 'xml-3398ac2-5', 'xml-4c99b96-1', 'xml-4c99b96-10',
                  'xml-4c99b96-11', 'xml-4c99b96-12', 'xml-4c99b96-13', 'xml-4c99b96-14', 'xml-4c99b96-15',
                  'xml-4c99b96-16', 'xml-4c99b96-17', 'xml-4c99b96-18', 'xml-4c99b96-19', 'xml-4c99b96-2',
                  'xml-4c99b96-3', 'xml-4c99b96-4', 'xml-4c99b96-5', 'xml-4c99b96-6', 'xml-4c99b96-7',
                  'xml-4c99b96-8', 'xml-4c99b96-9', 'xml-8ede045-1', 'xml-8ede045-2', 'xml-8ede045-3',
                  'xml-8ede045-4', 'xml-8ede045-5', 'xml-8ede045-6', 'xml-8ede045-7', 'xml-8ede045-8', 'xml-f053486-1']

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
