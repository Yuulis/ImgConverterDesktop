import flet as ft


def main(page: ft.Page):
    def on_file_selected(e: ft.FilePickerResultEvent):
        file_paths = []
        if e.files:
            file_paths = [file.path for file in e.files]
            print(file_paths)
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
