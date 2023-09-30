import os
import sys

subjects = ['clang-22382','clang-22704','clang-23309','clang-23353','clang-25900','clang-26760','clang-27137','clang-27747','clang-31259','gcc-59903','gcc-60116','gcc-61383','gcc-61917','gcc-64990','gcc-65383','gcc-66186','gcc-66375','gcc-70127','gcc-70586','gcc-71626']
result_folder = sys.argv[1]

def fileCount(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        count += sum(f.endswith(extension) for f in files)
    return count

def genCMD(fname):
  return "/chisel_ProbDD/build/bin/chisel" + " " + fname

def getFiles(target):
  all_files = []
  for root, dirs, files in os.walk(target):
    for f in files:
      targetfile = str(os.path.join(root,f)).strip()
      if 'small.c' in targetfile and ('assert' not in targetfile and 'empty' not in targetfile):
        all_files.append(targetfile)
  return all_files

def getFile2Stat(subpath):
  dir_list = getFiles(subpath)
  dir_list = sorted(dir_list,key=lambda x: os.path.getmtime(os.path.join(subpath, x)))
  return dir_list[-1]

for subpath in subjects:
  collect_path = result_folder + subpath + "-hdd"
  if not os.path.exists(collect_path):
      print("%s is not available" % subpath)
      continue
  if os.path.isfile(collect_path + "/small.c"):
    proc = os.popen(genCMD(collect_path + "/small.c"))
    token_str = list(filter(lambda x : True if 'original tokens:' in x else False, proc.readlines()))
    token_num = token_str[-1].strip().split(":")[-1]
    log_file = result_folder + "/log_hdd_" + subpath 
    fopen = open(log_file,'r')
    lines = fopen.readlines()
    time_line = lines[-1]
    strtime = time_line.strip().split(":")[-1].strip().rstrip('s')
    res_path = os.path.join(collect_path, "tests")
    iteration = len(os.listdir(res_path))
    test_num = fileCount(res_path, "small.c")

    print("case: %s: time: %s, token num: %s, iteration: %d, test num: %d" % (subpath, strtime, token_num, iteration, test_num))
  else:
    print("%s: small.c not available" % subpath)
