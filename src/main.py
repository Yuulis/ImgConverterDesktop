import os
import asyncio
import time
from PIL import Image
import numpy as np
import cv2
import base64
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import flet as ft
import dir_control


# File Watcher class
class FileWatcher:
    def __init__(self, page, log_area, img_src):
        self.observer = Observer()
        self.page = page
        self.log_area = log_area
        self.img_src = img_src

    def run(self, watch_dir_path):
        event_handler = FileChangeHandler(self.page, self.log_area, self.img_src)
        self.observer.schedule(event_handler, watch_dir_path, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            asyncio.run(print_log(self.page, self.log_area, "File Watcher stopped."))

        self.observer.join()


# File Change Handler class
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, page, log_area, img_src):
        self.page = page
        self.log_area = log_area
        self.img_src = img_src

    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            file_path = event.src_path
            img_convert(self.page, self.log_area, self.img_src, event.src_path)


# Convert image file
def img_convert(page, log_area, img_src, file_path):
    asyncio.new_event_loop().run_in_executor(
        None, print_log(page, log_area, f"Loaded : {file_path}")
    )

    img = img_read(file_path)
    base64_img = to_base64(img)
    img_src.src_base64 = base64_img
    img_src.update()

    fig = Image.open(file_path)

    # for converting .eps
    fig = fig.convert("RGB")

    fig.save(
        f"./out/{os.path.splitext(os.path.basename(file_path))[0]}.eps", lossless=True
    )

    asyncio.new_event_loop().run_in_executor(
        None,
        print_log(
            page,
            log_area,
            f"Successfully converted to {os.path.splitext(os.path.basename(file_path))[0]}.eps",
        ),
    )


# Read image file
def img_read(file_path, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        arr = np.fromfile(file_path, dtype)
        img = cv2.imdecode(arr, flags)
        return img
    except Exception as e:
        print(e)
        return None


# Convert image to base64
def to_base64(img):
    base64_img = base64.b64encode(cv2.imencode(".png", img)[1]).decode()
    return base64_img


# Display log message to log_area
def print_log(page, log_area, msg):
    log_area.controls.append(ft.Text(msg))
    page.update()


def main(page: ft.Page):
    # ===== Windows Settings ===== #
    page.title = "ImgConverterDesktop"
    page.window.width = 600
    page.window.height = 450
    page.padding = 20
    # ============================ #

    # ===== Create dirextory to save image files ===== #
    dir_control.make_dir("input")
    dir_control.make_dir("out")
    # ================================================= #

    # ===== Initialize preview image ===== #
    init_img = np.zeros((180, 240, 3), dtype=np.uint8) + 128
    init_base64_img = to_base64(init_img)
    img_src = ft.Image(src_base64=init_base64_img, width=240, height=180)
    # ===================================== #

    # ===== Controls ===== #
    # Log area
    log_area = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)

    # File picker dialog
    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_file_path = e.files[0].path
            asyncio.new_event_loop().run_in_executor(
                None, print_log(page, log_area, f"file selected : {uploaded_file_path}")
            )

            img_convert(page, log_area, img_src, uploaded_file_path)

    uploaded_file_dialog = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(uploaded_file_dialog)

    # Dropdown Menu
    def on_dropdown_changed(e):
        asyncio.new_event_loop().run_in_executor(
            None, print_log(page, log_area, f"Convert target : {dd.value}")
        )

    dd = ft.Dropdown(
        width=150,
        label="Target Format",
        on_change=on_dropdown_changed,
        autofocus=True,
        options=[ft.dropdown.Option("EPS")],
    )
    # =================== #

    # Add controls to the page
    page.add(
        ft.Row([ft.Text("Convert target format : "), dd]),
        ft.Row(
            [
                ft.ElevatedButton(
                    "Open the file",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: uploaded_file_dialog.pick_files(
                        allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
                    ),
                )
            ]
        ),
        ft.Row([img_src]),
        log_area,
    )

    # ===== File Watcher ===== #
    watcher = FileWatcher(page, log_area, img_src)
    watcher.run("input")
    # ========================= #


ft.app(main)
