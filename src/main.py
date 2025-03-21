import os
import flet as ft

APP_NAME = "ImgConverterDesktop"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 450


# Set the app name and window size
def app_settings(page, app_name, width, height):
    page.title = app_name
    page.window.width = width
    page.window.height = height


# Make directories to store the uploaded and converted files
def make_dirs():
    if not os.path.exists("input"):
        os.makedirs("input")

    if not os.path.exists("output"):
        os.makedirs("output")


def main(page: ft.Page):
    app_settings(page, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    make_dirs()

    def on_file_selected(e: ft.FilePickerResultEvent):
        file_paths = []
        if e.files:
            file_paths = [file.path for file in e.files]
            upload_file_path_text.value = "\n".join(file_paths)
        upload_file_path_text.update()

    pick_files_dialog = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(pick_files_dialog)
    upload_file_path_text = ft.Text()

    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    text="Open File",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                )
            ]
        ),
        upload_file_path_text,
    )


ft.app(main)
