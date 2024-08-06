import sys
from collections import defaultdict

def parse_file(input_file, output_file):
    id_stats = defaultdict(lambda: {'success': 0, 'total': 0})

    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 2:
                id_part, status = parts
                if 'Removed' in id_part and 'lines' in id_part and status.strip() in ('Success', 'Failure'):
                    try:
                        ids = id_part.split('[')[1].split(']')[0]
                        ids = [int(x.strip()) for x in ids.split(',')]
                        status = status.strip()
                        for line_id in ids:
                            id_stats[line_id]['total'] += 1
                            if status == 'Success':
                                id_stats[line_id]['success'] += 1
                    except (ValueError, IndexError):
                        print(f"Skipping invalid line: {line.strip()}")
                        continue

    with open(output_file, 'w') as f:
        for line_id in sorted(id_stats.keys()):
            success_rate = id_stats[line_id]['success'] / id_stats[line_id]['total']
            f.write(f"{line_id}: {id_stats[line_id]['success']}/{id_stats[line_id]['total']}={success_rate:.4f}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python count.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    parse_file(input_file, output_file)

