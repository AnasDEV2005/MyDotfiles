import fabric
from fabric import Application
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.webview import WebView 
from fabric.utils import get_relative_path


class window_(Window):
    def __init__(self, **kwargs):
        super().__init__(
            title="webvu",
            name="container",
            layer="overlay",
            exclusivity="auto",
            keyboard_mode="on-demand",
            **kwargs
        )
        self.webv = WebView(
            url = "https://chatgpt.com",
            size = 1000,
        )

        self.add(self.webv)
        self.show_all()

if __name__ == "__main__":
    bar = window_()
    app = Application("webvu", bar)
    app.set_stylesheet_from_file(get_relative_path("./webv.css"))
    app.run()



