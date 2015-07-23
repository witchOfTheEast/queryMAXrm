import os

par_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
temp_dir = os.path.join(par_dir, 'temp')

print os.path.isdir(temp_dir)
print temp_dir
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

