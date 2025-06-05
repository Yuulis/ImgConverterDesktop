import os
import flet as ft
import pillow_heif
from PIL import Image

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


# Convert the uploaded image to the target format
def convert_image(file_path, target_format):
    file_base_name, file_ext = os.path.splitext(os.path.basename(file_path))

    # Save the original image to the input directory
    img = Image.open(file_path)
    img.save(f"input/{file_base_name}{file_ext}")

    # If the file is HEIC, use convert_heic function
    if file_ext == ".heic" or file_ext == ".HEIC":
        convert_heic(file_path, file_base_name, dd_target_select.value)

    # If the file is not HEIC, use Pillow to convert it
    else:
        img = Image.open(file_path)
        img.save(f"output/{file_base_name}.{target_format}")


# Convert HEIC file to target format
def convert_heic(file_path, file_base_name, target_format):
    convert_target_file = pillow_heif.read_heif(file_path)
    for img in convert_target_file:
        image = Image.frombytes(
            img.mode,
            img.size,
            img.data,
            "raw",
            img.mode,
            img.stride,
        )
    image.save(f"output/{file_base_name}.{target_format}")


# Display a preview image
def display_preview_image(container, file_path):
    container.controls.append(
        ft.Image(
            src=file_path,
            width=100,
            height=100,
            fit=ft.ImageFit.CONTAIN,
            repeat=ft.ImageRepeat.NO_REPEAT,
            border_radius=ft.border_radius.all(10),
        )
    )


# Dropdown menu for selecting the target format
dd_target_select = ft.Dropdown(
    width=150,
    label="Target Format",
    autofocus=True,
    options=[
        ft.dropdown.Option("blp"),
        ft.dropdown.Option("bmp"),
        ft.dropdown.Option("dds"),
        ft.dropdown.Option("dib"),
        ft.dropdown.Option("eps"),
        ft.dropdown.Option("gif"),
        ft.dropdown.Option("icns"),
        ft.dropdown.Option("ico"),
        ft.dropdown.Option("im"),
        ft.dropdown.Option("jpg"),
        ft.dropdown.Option("jp2"),
        ft.dropdown.Option("mpo"),
        ft.dropdown.Option("msp"),
        ft.dropdown.Option("pcx"),
        ft.dropdown.Option("pfm"),
        ft.dropdown.Option("png"),
        ft.dropdown.Option("ppm"),
        ft.dropdown.Option("sgi"),
        ft.dropdown.Option("spider"),
        ft.dropdown.Option("tga"),
        ft.dropdown.Option("tiff"),
        ft.dropdown.Option("webp"),
        ft.dropdown.Option("xbm"),
        ft.dropdown.Option("palm"),
        ft.dropdown.Option("pdf"),
        ft.dropdown.Option("xv"),
    ],
)


def main(page: ft.Page):
    app_settings(page, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    make_dirs()

    def on_file_selected(e: ft.FilePickerResultEvent):
        file_paths = []
        if e.files:
            file_paths = [file.path for file in e.files]

            # Check each file
            for file_path in file_paths:
                display_preview_image(uploaded_images, file_path)
                page.update()

                convert_image(file_path, dd_target_select.value)

            upload_file_path_text.value = "\n".join(file_paths)

        upload_file_path_text.update()

    pick_files_dialog = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(pick_files_dialog)

    uploaded_images = ft.Row(
        expand=1,
        wrap=False,
        scroll=ft.ScrollMode.ALWAYS,
    )

    upload_file_path_text = ft.Text()

    page.add(
        ft.Row([ft.Text("Convert target format : "), dd_target_select]),
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
        ft.Row([uploaded_images]),
        ft.Row([upload_file_path_text]),
        ft.Row(
            [
                ft.Text("© 2025 Yuulis"),
            ]
        ),
    )


ft.app(main)
