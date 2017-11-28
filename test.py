import os
this_path = os.path.dirname(os.path.realpath(__file__))
curfile_path = os.path.abspath(__file__)
cur_dir = os.path.abspath(os.path.join(curfile_path,os.pardir)) # this will return current directory in which python file resides.
parent_dir = os.path.abspath(os.path.join(cur_dir,os.pardir)) # this will return parent directory.

print(this_path)
print(curfile_path)
print(cur_dir)
print(parent_dir)

