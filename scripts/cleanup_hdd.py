import os
import sys

def delete_non_c_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith('.c'):
                file_to_remove = os.path.join(root, file)
                os.remove(file_to_remove)

BENCHMARK_LIST = ['clang-22382', 'clang-22704', 'clang-23309', 'clang-23353',
                  'clang-25900', 'clang-26760', 'clang-27137', 'clang-27747',
                  'clang-31259', 'gcc-59903', 'gcc-60116', 'gcc-61383',
                  'gcc-61917', 'gcc-64990', 'gcc-65383', 'gcc-66186',
                  'gcc-66375', 'gcc-70127', 'gcc-70586', 'gcc-71626']

RESULT_PATH = sys.argv[1]

for target in BENCHMARK_LIST:
    collect_path = os.path.join(RESULT_PATH, "result_" + target)
    if not os.path.exists(collect_path):
        print(f"{target} is not available")
        continue

    delete_non_c_files(collect_path)
