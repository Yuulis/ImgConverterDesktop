import flet as ft
import dir_control


def main(page: ft.Page):    
    dir_control.make_dir("input")
    dir_control.make_dir("out")
    
    page.title = "ImgConverterDesktop"
    page.window.width = 400
    page.window.height = 300
    page.padding = 20
    
    uploaded_file_name_text = ft.Text()
    
    
    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_file_name_text.value = e.files[0].name
            uploaded_file_name_text.update()


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
                        allow_multiple = False
                    )
                ),
                uploaded_file_name_text,
            ]
        ),
        ft.Row(
            [
                ft.ElevatedButton(
                    "Download the file",
                    icon = ft.icons.DOWNLOAD
                )
            ]
        ),
    )


ft.app(main)
