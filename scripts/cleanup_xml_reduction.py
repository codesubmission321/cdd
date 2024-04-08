import os
import sys


def delete_non_xml_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith('.xml'):
                file_to_remove = os.path.join(root, file)
                os.remove(file_to_remove)


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

for target in BENCHMARK_LIST:
    collect_path = os.path.join(RESULT_PATH, "result_" + target)
    if not os.path.exists(collect_path):
        print(f"{target} is not available")
        continue

    delete_non_xml_files(collect_path)
