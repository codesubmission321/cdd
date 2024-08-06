import os
import shutil
import subprocess
import tempfile
import argparse
import concurrent.futures
import random
import threading

lock = threading.Lock()

def copy_files_to_tmp(input_file, script_file):
    tmp_dir = tempfile.mkdtemp()
    shutil.copy(input_file, os.path.join(tmp_dir, 'input'))
    shutil.copy(script_file, os.path.join(tmp_dir, 'r.sh'))
    return tmp_dir

def run_script(script_path, cwd):
    result = subprocess.run(['bash', script_path], capture_output=True, cwd=cwd)
    return result.returncode

def remove_lines(input_path, start_line, num_lines):
    with open(input_path, 'r', encoding='latin1') as file:
        lines = file.readlines()

    modified_lines = [line for i, line in enumerate(lines) if i < start_line or i >= start_line + num_lines]

    with open(input_path, 'w', encoding='latin1') as file:
        file.writelines(modified_lines)

def remove_random_lines(input_path, num_lines, total_lines):
    with open(input_path, 'r', encoding='latin1') as file:
        lines = file.readlines()

    if num_lines >= total_lines:
        raise ValueError("num_lines must be less than the total number of lines in the file")

    random_indices = random.sample(range(total_lines), num_lines)

    random_indices_set = set(random_indices)
    modified_lines = [line for i, line in enumerate(lines) if i not in random_indices_set]

    with open(input_path, 'w', encoding='latin1') as file:
        file.writelines(modified_lines)

    return random_indices

def remove_chars(input_path, start_char, num_chars):
    with open(input_path, 'r', encoding='latin1') as file:
        content = file.read()

    modified_content = content[:start_char] + content[start_char + num_chars:]

    with open(input_path, 'w', encoding='latin1') as file:
        file.write(modified_content)

def remove_random_chars(input_path, num_chars, total_chars):
    with open(input_path, 'r', encoding='latin1') as file:
        content = file.read()

    if num_chars >= total_chars:
        raise ValueError("num_chars must be less than the total number of chars in the file")

    random_indices = random.sample(range(total_chars), num_chars)

    modified_content = ''.join(char for i, char in enumerate(content) if i not in set(random_indices))

    with open(input_path, 'w', encoding='latin1') as file:
        file.write(modified_content)

    return random_indices

def log_result(log_path, removed_units, success, unit_type):
    with lock:
        with open(log_path, 'a') as log_file:
            log_file.write(f"Removed {len(removed_units)} {unit_type}: {'Success' if success else 'Failure'}\n")

def process_window(input_file, script_file, num_units, total_units, log_file, unit_type):
    tmp_dir = copy_files_to_tmp(input_file, script_file)
    input_tmp_path = os.path.join(tmp_dir, 'input')

    if unit_type == 'lines':
        start_unit = random.randint(0, total_units - num_units)
        remove_lines(input_tmp_path, start_unit, num_units)
        removed_units = list(range(start_unit + 1, start_unit + num_units + 1))
    elif unit_type == 'chars':
        start_unit = random.randint(0, total_units - num_units)
        remove_chars(input_tmp_path, start_unit, num_units)
        removed_units = list(range(start_unit, start_unit + num_units))

    script_path = os.path.join(tmp_dir, 'r.sh')

    result = run_script(script_path, cwd=tmp_dir)
    success = result == 0

    log_result(log_file, removed_units, success, unit_type)

    shutil.rmtree(tmp_dir)

    return removed_units, success

def process_random_units(input_file, script_file, num_units, total_units, log_file, unit_type):
    tmp_dir = copy_files_to_tmp(input_file, script_file)
    input_tmp_path = os.path.join(tmp_dir, 'input')

    if unit_type == 'lines':
        removed_units = remove_random_lines(input_tmp_path, num_units, total_units)
    elif unit_type == 'chars':
        removed_units = remove_random_chars(input_tmp_path, num_units, total_units)

    script_path = os.path.join(tmp_dir, 'r.sh')

    result = run_script(script_path, cwd=tmp_dir)
    success = result == 0

    log_result(log_file, removed_units, success, unit_type)

    shutil.rmtree(tmp_dir)

    return removed_units, success

def main(input_file, script_file, num_units, jobs, attempts, mode, unit_type):
    log_file = f"{num_units}_{unit_type}_{jobs}_jobs_{attempts}_attempts_{mode}_mode.log"

    with open(log_file, 'w') as log_file_clear:
        log_file_clear.write("Log of removed units and results:\n")

    if unit_type == 'lines':
        with open(input_file, 'r', encoding='latin1') as file:
            original_units = file.readlines()
    elif unit_type == 'chars':
        with open(input_file, 'r', encoding='latin1') as file:
            original_units = file.read()

    total_units = len(original_units)

    if total_units < num_units:
        print(f"File has fewer than {num_units} {unit_type}. Exiting.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = []
        for _ in range(attempts):
            if mode == 'slide':
                futures.append(executor.submit(process_window, input_file, script_file, num_units, total_units, log_file, unit_type))
            elif mode == 'random':
                futures.append(executor.submit(process_random_units, input_file, script_file, num_units, total_units, log_file, unit_type))

        try:
            for future in concurrent.futures.as_completed(futures):
                removed_units, success = future.result()
                print(f"Progress: {'Success' if success else 'Failure'}")
        except KeyboardInterrupt:
            print("Process interrupted by user. Cleaning up...")
            executor.shutdown(wait=False)
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process input file and script with random or sliding window removal.')
    parser.add_argument('input_file', type=str, help='Path to the input file')
    parser.add_argument('script_file', type=str, help='Path to the r.sh file')
    parser.add_argument('num_units', type=int, help='Number of lines or chars to remove')
    parser.add_argument('--jobs', type=int, default=1, help='Number of threads to use')
    parser.add_argument('--attempts', type=int, default=10, help='Number of attempts to make')
    parser.add_argument('--mode', choices=['slide', 'random'], required=True, help='Mode of removal: "slide" for sliding window, "random" for random units')
    parser.add_argument('--unit_type', choices=['lines', 'chars'], required=True, help='Type of units to remove: "lines" or "chars"')

    args = parser.parse_args()

    main(args.input_file, args.script_file, args.num_units, args.jobs, args.attempts, args.mode, args.unit_type)

