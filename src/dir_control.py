import os

# directory path must be reatve(root is this project dir).
def make_dir(path):
    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)
