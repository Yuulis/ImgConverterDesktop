import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# directory path must be reatve(root is this project dir).
def make_dir(path):
    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)
        
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        
    def on_created(self, event):
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        print(f"created: {file_name}")
        
    def on_modified(self, event):
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        print(f"modified: {file_name}")
        
    def on_deleted(self, event):
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        print(f"deleted: {file_name}")
        
    def on_moved(self, event):
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        print(f"moved: {file_name}")        
