import os
import flet as ft
import pillow_heif
from PIL import Image
import subprocess

APP_NAME = "ImgConverterDesktop"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


# Set the app name and window size
def app_settings(page, app_name, width, height):
    page.title = app_name
    page.window.width = width
    page.window.height = height


from utils import make_dirs, convert_image, format_bytes


# format_bytes is imported from utils


def create_item_controls(file_path: str) -> tuple[ft.Control, dict]:
    file_name = os.path.basename(file_path)

    img_control = ft.Image(
        src=None,
        width=160,
        height=120,
        fit=ft.ImageFit.CONTAIN,
        repeat=ft.ImageRepeat.NO_REPEAT,
        border_radius=ft.border_radius.all(8),
    )

    name_text = ft.Text(file_name, weight=ft.FontWeight.BOLD)
    format_text = ft.Text("", color=ft.Colors.GREY_700)
    dim_text = ft.Text("", color=ft.Colors.GREY_700)
    size_text = ft.Text("", color=ft.Colors.GREY_700)
    status_text = ft.Text("", color=ft.Colors.GREY_700)
    pbar = ft.ProgressBar(width=400, visible=False, value=0)

    # Image on the left, details on the right
    details_col = ft.Column(
        tight=True,
        spacing=4,
        controls=[name_text, format_text, dim_text, size_text, pbar, status_text],
        expand=True,
    )

    item = ft.Container(
        padding=10,
        content=ft.Row(
            controls=[img_control, details_col],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
    )

    refs = {
        "image": img_control,
        "format_text": format_text,
        "dim_text": dim_text,
        "size_text": size_text,
        "status_text": status_text,
        "pbar": pbar,
    }

    return item, refs


# Dropdown menu for selecting the target format
dd_target_select = ft.Dropdown(
    width=150,
    label="Target Format",
    autofocus=True,
    value="png",
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

    # Event handler for file selection
    def on_file_selected(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file_paths = [file.path for file in e.files]

        # Process each file with per-item progress and status
        for file_path in file_paths:
            # Create UI item and add to list
            item, refs = create_item_controls(file_path)
            image_list.controls.append(item)
            page.update()

            # 1) 画像読み込み開始 -> 2) プログレスバー表示
            refs["status_text"].value = "Loading..."
            refs["status_text"].color = ft.Colors.GREY_700
            refs["pbar"].visible = True
            refs["pbar"].value = 0
            page.update()

            # Try loading image and gathering metadata
            loading_failed = False
            width = height = None
            src_fmt = None
            try:
                with Image.open(file_path) as im:
                    width, height = im.size
                    src_fmt = im.format
            except Exception:
                # Try HEIC size via pillow_heif as fallback
                try:
                    heif = pillow_heif.read_heif(file_path)
                    first = None
                    for img in heif:
                        first = img
                        break
                    if first is not None:
                        width, height = first.size
                        src_fmt = "HEIC"
                except Exception:
                    loading_failed = True

            # File size (data size)
            try:
                file_size = os.path.getsize(file_path)
                refs["size_text"].value = f"Data size: {format_bytes(file_size)}"
            except Exception:
                refs["size_text"].value = "Data size: -"

            # Show source -> target format info (even if may fail)
            ext = os.path.splitext(file_path)[1].lstrip(".")
            src_disp = (src_fmt or ext or "?").upper()
            tgt_disp = (
                (dd_target_select.value or "-").upper()
                if dd_target_select.value
                else "-"
            )
            refs["format_text"].value = f"{src_disp} -> {tgt_disp}"

            if loading_failed or width is None or height is None:
                refs["pbar"].visible = False
                refs["status_text"].value = "Loading Failed"
                refs["status_text"].color = ft.Colors.RED_600
                page.update()
                # Skip conversion if loading failed
                continue

            # 3) 画像読み込み完了、画像データの表示
            refs["image"].src = file_path
            refs["dim_text"].value = f"{width} x {height} px"
            refs["pbar"].visible = False
            refs["status_text"].value = ""
            page.update()

            # 4) 画像形式変換開始 -> 5) プログレスバー表示
            refs["status_text"].value = "Converting..."
            refs["status_text"].color = ft.Colors.GREY_700
            refs["pbar"].visible = True
            refs["pbar"].value = 0
            page.update()

            # Convert
            try:
                if dd_target_select.value:
                    convert_image(file_path, dd_target_select.value)
                # 6) 成功ステータス表示
                refs["status_text"].value = "Success"
                refs["status_text"].color = ft.Colors.GREEN_600
            except Exception:
                refs["status_text"].value = "Conversion Failed"
                refs["status_text"].color = ft.Colors.RED_600
            finally:
                refs["pbar"].visible = False
                page.update()

    # Event handler for opening the output directory
    def on_output_dir_opened(e: ft.FilePickerResultEvent):
        subprocess.Popen(["explorer", r"output"], shell=True)

    pick_files_dialog = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(pick_files_dialog)

    # Scrollable vertical list of items (image + file name + size)
    image_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=10,
        auto_scroll=False,
    )

    page.add(
        ft.Row(
            [
                ft.Text("Convert target format : ", size=20, weight=ft.FontWeight.BOLD),
                dd_target_select,
            ]
        ),
        ft.Row(
            [
                ft.ElevatedButton(
                    text="Open File",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                ft.ElevatedButton(
                    text="Open Output Folder",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda _: on_output_dir_opened(None),
                ),
            ]
        ),
        image_list,
        ft.Row([ft.Text("© 2025 Yuulis")], alignment=ft.MainAxisAlignment.CENTER),
    )


ft.app(main)
