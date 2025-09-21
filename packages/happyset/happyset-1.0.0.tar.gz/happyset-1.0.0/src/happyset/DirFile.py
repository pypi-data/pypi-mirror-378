import os
import shutil

# Clear
def Clear_dir(path):
    shutil.rmtree(path)
    os.mkdir(path)
    
def Clear_file(path):
    with open(path, "r+") as f:
        f.truncate(0)

# Copy
def Copy_dir(targetPath, createPath):
    shutil.copytree(targetPath, createPath, dirs_exist_ok=True)

# Move
def Move_file(srcpath, dstpath):
    shutil.move(srcpath, dstpath)
