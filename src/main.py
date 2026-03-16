import base64
import asyncio
import io
import os
import flet as ft
from PIL import Image
import subprocess
from utils import make_dirs, convert_image, format_bytes, load_heif_as_pil

APP_NAME = "ImgConverterDesktop"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLACEHOLDER_IMAGE_SRC = (
    "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="
)


def app_settings(page, app_name, width, height):
    """Configures the app page settings.
    
    Args:
        page: The Flet page object to configure.
        app_name: The title of the application window.
        width: The width of the application window.
        height: The height of the application window.
    """
    
    page.title = app_name
    page.window.width = width
    page.window.height = height


def build_heif_preview_base64(file_path: str) -> tuple[str, tuple[int, int]]:
    """Builds a thumbnail preview for HEIC files and returns it as a base64 string along with dimensions.

    Args:
        file_path: Path to the HEIC image file.

    Returns:
        A tuple containing the base64-encoded thumbnail image and its dimensions (width, height).
    """
    image = load_heif_as_pil(file_path)
    size = image.size
    image.thumbnail((160, 120))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("ascii"), size


# Create UI controls for a single image item
def create_item_controls(file_path: str) -> tuple[ft.Control, dict]:
    """Creates the UI controls for a single image item in the list.
    
    Args:
        file_path: The path to the image file for which to create the controls.
        
    Returns: 
        A tuple containing the container control for the item and a dictionary of references to its sub-controls.
    """
    
    file_name = os.path.basename(file_path)

    img_control = ft.Image(
        src=PLACEHOLDER_IMAGE_SRC,
        width=160,
        height=120,
        fit=ft.BoxFit.CONTAIN,
        repeat=ft.ImageRepeat.NO_REPEAT,
        border_radius=ft.Border.all(8),
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
        border=ft.Border.all(1, ft.Colors.GREY_300),
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


def main(page: ft.Page):
    app_settings(page, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
    make_dirs()

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

    async def process_selected_files(file_paths: list[str]):
        # Process each file with per-item progress and status
        for file_path in file_paths:
            # Create UI item and add to list
            item, refs = create_item_controls(file_path)
            image_list.controls.insert(0, item)

            """
            1. Start loading image
            2. Show progress bar
            3. Image loaded, show image data
            4. Start conversion
            5. Show progress bar
            6. Show success status
            """
            refs["status_text"].value = "Loading..."
            refs["status_text"].color = ft.Colors.GREY_700
            refs["pbar"].visible = True
            refs["pbar"].value = 0
            page.update()

            # Try loading image and gathering metadata
            loading_failed = False
            width = height = None
            src_fmt = None
            preview_base64 = None
            try:
                with Image.open(file_path) as im:
                    width, height = im.size
                    src_fmt = im.format
            except Exception:
                # Try HEIC size via pillow_heif as fallback
                try:
                    preview_base64, (width, height) = build_heif_preview_base64(
                        file_path
                    )
                    src_fmt = "HEIC"
                except Exception:
                    loading_failed = True

            # File data size
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

            # Display image info
            refs["image"].src = preview_base64 if preview_base64 else file_path
            refs["dim_text"].value = f"{width} x {height} px"
            refs["status_text"].value = "Converting..."
            refs["status_text"].color = ft.Colors.GREY_700
            refs["pbar"].visible = True
            refs["pbar"].value = 0
            page.update()

            # Convert (run in background thread to keep UI responsive)
            try:
                if dd_target_select.value:
                    await asyncio.to_thread(
                        convert_image,
                        file_path,
                        dd_target_select.value,
                    )
                refs["status_text"].value = "Success"
                refs["status_text"].color = ft.Colors.GREEN_600
            except Exception:
                refs["status_text"].value = "Conversion Failed"
                refs["status_text"].color = ft.Colors.RED_600
            finally:
                refs["pbar"].visible = False
                page.update()

    # Event handler for file selection
    async def on_file_selected(_):
        files = await pick_files_dialog.pick_files(allow_multiple=True)
        if not files:
            return

        file_paths = [file.path for file in files if file.path]
        if not file_paths:
            return

        page.run_task(process_selected_files, file_paths)

    # Event handler for opening the output directory
    def on_output_dir_opened(_):
        subprocess.Popen(["explorer", os.path.abspath("output")], shell=False)

    pick_files_dialog = ft.FilePicker()
    page.services.append(pick_files_dialog)

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
                ft.Button(
                    content="Open File",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=on_file_selected,
                ),
                ft.Button(
                    content="Open Output Folder",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=on_output_dir_opened,
                ),
            ]
        ),
        image_list,
        ft.Row([ft.Text("© 2026 Yuulis")], alignment=ft.MainAxisAlignment.CENTER),
    )


ft.run(main)
