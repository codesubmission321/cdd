import os, re, sys, glob

class Delete(object):
  """docstring for Delete"""
  def __init__(self, log_path, iteration, level, orig_size, current_size_after_deletion, 
    indices, success, continuous, complement, line_no):
    self.log_path = log_path
    self.iteration = iteration
    self.level = level
    self.orig_size = orig_size
    self.current_size_after_deletion = current_size_after_deletion
    self.indices = indices
    self.success = success
    self.continuous = continuous
    self.complement = complement
    if complement:
      self.deleted_size = orig_size - len(indices)
    else:
      self.deleted_size = len(indices)
    self.line_no = line_no

def computeContinuous(current_list, deleted_indices):
  if (len(deleted_indices) == 1):
    return True
  deleted_indices.sort()
  idx_min = deleted_indices[0]
  idx_max = deleted_indices[-1]
  for idx in range(idx_min, idx_max+1):
    if (idx not in deleted_indices and current_list[idx] == True):
      return False
  return True

def computeCurrentSize(current_list):
  count = 0
  for item in current_list:
    if (item == True):
      count = count + 1
  return count

def analyze_file(log_path):
  file = open(log_path, "r")
  lines = file.readlines()
  file.close()

  # count delete size
  orig_size = 0
  orig_list = []
  current_list = []
  delete_set = []
  continuous = True

  idx = 0
  while(idx < len(lines)):
    current_line = lines[idx].strip()
    # print(current_line, idx)
    # match iteration
    match_iteration = re.match(r"Iteration #(\d)+", current_line)
    if (match_iteration):
      iteration = match_iteration.group(1)

    # match level
    match_level = re.match(r"Checking level (\d)+ / \d+", current_line)
    if (match_level):
      level = match_level.group(1)

      # match orig size
      line_with_orig_size = lines[idx+2].strip()
      # print(line_with_orig_size)
      orig_size = int(re.match(r"Config size: (\d+)", line_with_orig_size).group(1))
      orig_list = list(range(orig_size))
      current_list = [True for item in orig_list]

    # match trail
    match_trail = re.match(r"Try deleting(.*): (\[.*\])", current_line)
    if (match_trail):
      complement = match_trail.group(1) != ""
      trail = eval(match_trail.group(2))
      if (complement):
        # subtract
        to_be_deleted = [item for item in orig_list if item not in trail]
      else:
        to_be_deleted = trail

      # compute continuous
      continuous = computeContinuous(current_list, to_be_deleted)

      # match property
      line_with_property = lines[idx+1].strip()
      if(re.match(r"Deleted", line_with_property)):
        success = True
        # delete elements
        for deleted_idx in to_be_deleted:
          current_list[deleted_idx] = False
        
      else:
        success = False

      current_size_after_deletion = computeCurrentSize(current_list)

      # collect Delete
      delete_obj = Delete(
        log_path=log_path, iteration=iteration, level=level,
        orig_size=orig_size, current_size_after_deletion=current_size_after_deletion,
        indices=to_be_deleted, success=success, continuous=continuous,
        complement=complement, line_no=idx
        )

      delete_set.append(delete_obj)

    idx = idx + 1

  return delete_set


# start here
path = sys.argv[1]
if (os.path.isdir(path)):
  log_paths = glob.glob('./log_*')
else:
  log_paths = [path]

delete_set_all = []
for log_path in log_paths:
  delete_set = analyze_file(log_path)
  delete_set_all = delete_set_all + delete_set


print("all trails: %d" % len(delete_set_all))

max_deleted_size = max([delete.deleted_size for delete in delete_set_all])

# consider continuous
print("if consider continuous")
for continuous in [True, False]:
  for deleted_size in range(1, max_deleted_size + 1):
    print("(deleted_size, continuous): (%d, %d)" % (deleted_size, continuous))
    success_num = len([delete for delete in delete_set_all if delete.deleted_size == deleted_size and delete.continuous == continuous and delete.success == True])
    total_num = len([delete for delete in delete_set_all if delete.deleted_size == deleted_size and delete.continuous == continuous])
    print("success/total: %d/%d" % (success_num, total_num))

# do not consider continuous
print("if do not consider continuous")
for deleted_size in range(1, max_deleted_size + 1):
  print("deleted_size: %d" % (deleted_size))
  success_num = len([delete for delete in delete_set_all if delete.deleted_size == deleted_size and delete.success == True])
  total_num = len([delete for delete in delete_set_all if delete.deleted_size == deleted_size])
  print("success/total: %d/%d" % (success_num, total_num))










