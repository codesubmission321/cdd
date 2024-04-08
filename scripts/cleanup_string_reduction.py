import os
import sys


def delete_non_input_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            if not file == "input":
                file_to_remove = os.path.join(root, file)
                os.remove(file_to_remove)


BENCHMARK_LIST = ['as-2.30', 'bison-3.0.4', 'checknr-8.1', 'ctags-8.4', 'dc-1.3', 'dc-1.4', 'gdb-8.1',
                  'indent-5.17', 'ptx-8.32', 'spell-1.1', 'troff-1.19.2']

RESULT_PATH = sys.argv[1]

for target in BENCHMARK_LIST:
    collect_path = os.path.join(RESULT_PATH, "result_" + target)
    if not os.path.exists(collect_path):
        print(f"{target} is not available")
        continue

    delete_non_input_files(collect_path)
