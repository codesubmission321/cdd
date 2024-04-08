import sys

BENCHMARK_LIST = ['clang-22382', 'clang-23353',
                  'clang-25900', 'clang-27747',
                  'gcc-61917', 'gcc-65383', 'gcc-71626']

S0 = 10

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
