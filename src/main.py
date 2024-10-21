import os
import asyncio
import time
from PIL import Image
import numpy as np
import cv2
import base64
import flet as ft
import dir_control

def img_read(file_path, flags = cv2.IMREAD_COLOR, dtype = np.uint8):
    try:
        arr = np.fromfile(file_path, dtype)
        img = cv2.imdecode(arr, flags)
        return img
    except Exception as e:
        print(e)
        return None

def to_base64(img):
    base64_img = base64.b64encode(cv2.imencode('.png', img)[1]).decode()
    return base64_img

async def print_log(page, log_area, msg):
    await asyncio.sleep(0.1)
    
    log_area.controls.append(ft.Text(msg))
    page.update()
    


def main(page: ft.Page):
    # ===== Windows Settings ===== #
    page.title = "ImgConverterDesktop"
    page.window.width = 800
    page.window.height = 600
    page.padding = 20
    # ============================ #
    
    dir_control.make_dir("input")
    dir_control.make_dir("out")   
    
    init_img = np.zeros((180, 240, 3), dtype = np.uint8) + 128
    init_base64_img = to_base64(init_img)
    
    img_src = ft.Image(src_base64 = init_base64_img, width = 240, height = 180)
    
    uploaded_file_name_text = ft.Text()
    
    log_area = ft.ListView(
        expand = True,
        spacing = 5,
        padding = 10,
        auto_scroll = True
    )
    
    
    async def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_file_name_text.value = e.files[0].name
            uploaded_file_name_text.update()
            
            uploaded_file_path = e.files[0].path
            await print_log(page, log_area, f"file selected : {uploaded_file_path}")
            img = img_read(uploaded_file_path)
            base64_img = to_base64(img)
            img_src.src_base64 = base64_img
            img_src.update()
            
            fig = Image.open(uploaded_file_path)
            fig_type = fig.mode
            
            fig = fig.convert("RGB")
            fig.save(f"./out/{os.path.splitext(os.path.basename(uploaded_file_path))[0]}.eps", lossless = True)
            await print_log(page, log_area, f"Successfully converted to {os.path.splitext(os.path.basename(uploaded_file_path))[0]}.eps")


    uploaded_file_dialog = ft.FilePicker(on_result = on_file_selected)
    page.overlay.append(uploaded_file_dialog)
    
    
    page.add(
        ft.Row(
            [
                ft.Text(
                    "Convert From"
                ),
                ft.Dropdown(
                    width = 100,
                    options = [
                        ft.dropdown.Option("PNG"),
                        ft.dropdown.Option("EPS"),
                        ft.dropdown.Option("JPEG"),
                    ]
                ),
                ft.Text(
                    "To"
                ),
                ft.Dropdown(
                    width = 100,
                    options = [
                        ft.dropdown.Option("PNG"),
                        ft.dropdown.Option("EPS"),
                        ft.dropdown.Option("JPEG"),
                    ]
                ),
            ]
        ),
        ft.Row(
            [
                ft.ElevatedButton(
                    "Open the file",
                    icon = ft.icons.UPLOAD_FILE,
                    on_click = lambda _: uploaded_file_dialog.pick_files(
                        allow_multiple = False,
                        file_type = ft.FilePickerFileType.IMAGE 
                    )
                ),
                uploaded_file_name_text,
            ]
        ),
        ft.Row(
            [
                img_src
            ]
        ),
        log_area
    )
    
    # ===== File Watcher ===== #
    event_handler = dir_control.FileChangeHandler()
    observer = dir_control.Observer()
    observer.schedule(event_handler, "./input", recursive = True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()
    # ========================= # 


ft.app(main)
