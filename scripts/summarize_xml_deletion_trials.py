import sys

BENCHMARK_LIST = ['xml-071d221-1', 'xml-071d221-2', 'xml-1e9bc83-1', 'xml-1e9bc83-2', 'xml-1e9bc83-3',
                  'xml-1e9bc83-4', 'xml-1e9bc83-5', 'xml-1e9bc83-6', 'xml-1e9bc83-7', 'xml-1e9bc83-8',
                  'xml-1e9bc83-9', 'xml-2d4ec80-1', 'xml-327c8af-1', 'xml-3398ac2-1', 'xml-3398ac2-2',
                  'xml-3398ac2-3', 'xml-3398ac2-4', 'xml-3398ac2-5', 'xml-4c99b96-1', 'xml-4c99b96-10',
                  'xml-4c99b96-11', 'xml-4c99b96-12', 'xml-4c99b96-13', 'xml-4c99b96-14', 'xml-4c99b96-15',
                  'xml-4c99b96-16', 'xml-4c99b96-17', 'xml-4c99b96-18', 'xml-4c99b96-19', 'xml-4c99b96-2',
                  'xml-4c99b96-3', 'xml-4c99b96-4', 'xml-4c99b96-5', 'xml-4c99b96-6', 'xml-4c99b96-7',
                  'xml-4c99b96-8', 'xml-4c99b96-9', 'xml-8ede045-1', 'xml-8ede045-2', 'xml-8ede045-3',
                  'xml-8ede045-4', 'xml-8ede045-5', 'xml-8ede045-6', 'xml-8ede045-7', 'xml-8ede045-8', 'xml-f053486-1']
S0 = 40

def process_results_file(result_path):
    try:
        with open(result_path, 'r') as file:
            lines = file.readlines()

        total_size_sum = 0
        delete_size_sum = 0
        delete_size_success_sum = 0
        delete_size_fail_sum = 0
        num_success = 0
        num_fail = 0
        num_complement = 0
        num_success_complement = 0
        num_repeated = 0
        num_success_repeated = 0
        num_large = 0
        num_success_large = 0
        num_all = 0
        delete_size_frequency = {}  # To keep track of the frequencies

        for line in lines:
            benchmark, total_size, delete_size, complement, repeated, status = line.strip().split(', ')
            if benchmark not in BENCHMARK_LIST:
                continue
            num_all += 1
            total_size = int(total_size)
            delete_size = int(delete_size)

            # Update delete_size frequency
            if delete_size in delete_size_frequency:
                delete_size_frequency[delete_size] += 1
            else:
                delete_size_frequency[delete_size] = 1

            total_size_sum += total_size
            delete_size_sum += delete_size

            if status == "success":
                num_success += 1
                delete_size_success_sum += delete_size
            elif status == "fail":
                num_fail += 1
                delete_size_fail_sum += delete_size

            if complement == "True" and total_size > 2:
                num_complement += 1
                if status == "success":
                    num_success_complement += 1

            if repeated == "True":
                num_repeated += 1
                if status == "success":
                    num_success_repeated += 1

            if complement == "False" and repeated == "False" and delete_size > S0:
                num_large += 1
                if status == "success":
                    num_success_large += 1


        mean_list_size = total_size_sum / num_all if num_all else 0
        mean_delete_size_all = delete_size_sum / num_all if num_all else 0
        mean_delete_size_success = delete_size_success_sum / num_success if num_success else 0
        mean_delete_size_fail = delete_size_fail_sum / num_fail if num_fail else 0

        stats = {
            "query_num_all": num_all,
            "query_num_success": num_success,
            "query_num_fail": num_fail,
            "mean_list_size": mean_list_size,
            "mean_delete_size_all": mean_delete_size_all,
            "mean_delete_size_success": mean_delete_size_success,
            "mean_delete_size_fail": mean_delete_size_fail,
            "query_complement_num_all": num_complement,
            "query_complement_num_success": num_success_complement,
            "query_complement_num_fail": num_complement - num_success_complement,
            "query_repeated_num_all": num_repeated,
            "query_repeated_num_success": num_success_repeated,
            "query_repeated_num_fail": num_repeated - num_success_repeated,
            "query_large_num_all": num_large,
            "query_large_num_success": num_success_large,
            "query_large_num_fail": num_large - num_success_large,
        }

        # Adding delete_size_frequency to the results
        stats["delete_size_frequency"] = delete_size_frequency

        return stats
    except FileNotFoundError:
        print(f"File not found: {result_path}")
        return {}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result_path = sys.argv[1]
        stats = process_results_file(result_path)
        result_string = ""
        for key, value in stats.items():
            if key != "delete_size_frequency":
                print(f"{key}: {value}")
                result_string += f"{value:.2f},"
            else:
                print("frequency of each size")
                print(f"{key}: {value}")  # Print the frequency dictionary directly
        print(result_string[:-1])  # Remove the last comma
    else:
        print("Usage: python script.py <result_path>")
