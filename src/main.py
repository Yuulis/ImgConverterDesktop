import flet as ft
import dir_control


def main(page: ft.Page):
    dir_control.make_dir("input")
    dir_control.make_dir("out")
    
    def button_clicked(e):
        t.value = f"Dropdown value is:  {dd.value}"
        page.update()

    t = ft.Text()
    b = ft.ElevatedButton(text="Submit", on_click=button_clicked)
    dd = ft.Dropdown(
        width=100,
        options=[
            ft.dropdown.Option("PNG"),
            ft.dropdown.Option("EPS"),
            ft.dropdown.Option("JPEG"),
        ],
    )
    page.add(dd, b, t)


ft.app(main)
