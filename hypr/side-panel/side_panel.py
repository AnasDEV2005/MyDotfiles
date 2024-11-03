"""side panel example, contains info about the system"""

import os
import time
import psutil
import operator
from collections.abc import Iterator
from loguru import logger
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.datetime import DateTime
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.webview import WebView
from fabric.widgets.stack import Stack
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path
from fabric.utils import invoke_repeater, get_relative_path


def get_profile_picture_path() -> str | None:
    path = os.path.expanduser("~/Downloads/profile.jpg")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
            "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
        )
        path = None
    return path

#### S I D E   P A N E L ####


class SidePanel(Window):
    @staticmethod
    def bake_progress_bar(name: str = "progress-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name=name, min_value=0, max_value=100, line_width=3, size=size, **kwargs
        )
    def bake_bat_bar(name: str = "bat-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name="progress-bar", min_value=0, max_value=100, line_style='butt', size=size, **kwargs
        )
    def bake_disk_bar(name: str = "disk-bar", size: int = 64, **kwargs):
        return CircularProgressBar(
            name="progress-bar", min_value=0, max_value=100, pie=True, size=size, **kwargs
        )

    @staticmethod
    def bake_progress_icon(**kwargs):
        return Label(**kwargs).build().add_style_class("progress-icon").unwrap()

    def __init__(self, **kwargs):
        super().__init__(
            layer="top",
            title="fabric-overlay",
            anchor="top left bottom",
            margin="0px 0px 0px 0px",
            keyboard_mode='on-demand',
            exclusivity="auto",
            visible=False,
            all_visible=False,
            **kwargs,
        )
## HEADER
#########################################################################################################
        self.profile_pic = Box(
            name="profile-pic",
            style=f"background-image: url(\"file://{get_profile_picture_path() or ''}\")",
        )
        self.uptime_label = Label(label=f"{self.get_current_uptime()}")

        self.header = Box(
            spacing=14,
            name="header",
            orientation="h",
            children=[
                self.profile_pic,
                Box(
                    orientation="v",
                    children=[
                        DateTime(
                            name="date-time",
                            style="margin-top: 4px; min-width: 180px;",
                        ),
                        self.uptime_label,
                    ],
                ),
            ],
        )
## GREETER
######################################################################################################
        self.greeter_label = Label(
            label="سبحان الله وبحمده \n  سبحان الله العظيم",
            style="font-size: 18px; font-family: kawkab mono;",
        )
## STATUS BARS
#############################################################################################################################
        self.disk_progress = self.bake_disk_bar()
        self.ram_progress = self.bake_progress_bar()
        self.bat_circular = self.bake_bat_bar().build().set_value(42).unwrap()

        self.progress_container = Box(
            name="progress-bar-container",
            spacing=12,
            children=[
                Box(
                    children=[
                        Overlay(
                            child=self.disk_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                )
                            ],
                        ),
                    ],
                ),
                Box(name="progress-bar-sep"),
                Box(
                    children=[
                        Overlay(
                            child=self.ram_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="󰘚",
                                    style="margin-right: 4px; text-shadow: 0 0 10px #fff;",
                                )
                            ],
                        )
                    ]
                ),
                Box(name="progress-bar-sep"),
                Box(
                    children=[
                        Overlay(
                            child=self.bat_circular,
                            overlays=[
                                self.bake_progress_icon(
                                    label="󱊣",
                                    style="margin-right: 0px; text-shadow: 0 0 10px #fff, 0 0 18px #fff;",
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )
##################### TOOLS STACK ########################################################################3        

## NOTES
############################################################
        self.note = WebView(
            name='notes',
            url = "https://www.rapidtables.com/tools/notepad.html",
            size = (190,680),
        )
## CHAT
#############################################################
        self.chat = WebView(
            name='chat',
            url = "https://www.chatgpt.com",
            size = (190,680),
        )
## APP LAUNCHER
##############################################################
        self._arranger_handler: int = 0
        self._all_apps = get_desktop_applications()

        self.viewport = Box(name='viewport', spacing=15, orientation="v")
        self.search_entry = Entry(
            name='search',
            placeholder="Search Apps...",
            h_expand=True,
            notify_text=lambda entry, *_: self.arrange_viewport(entry.get_text()),
            on_button_press_event=print,
        )
        self.scrolled_window = ScrolledWindow(
            min_content_size=(190, 320),
            max_content_size=(190, 680),
            child=self.viewport,
        )
        self.box_apps = Box(
                name="appslauncher",
                spacing=10,
                orientation="v",
                style="margin: 2px",
                children=[
                    # the header with the search entry
                    Box(
                        spacing=2,
                        orientation="h",
                        children=[
                            self.search_entry
                            ,
                        ],
                    ),
                    # the actual slots holder
                    self.scrolled_window,
                ],
            )
            

## STACK OBJECT
##############################################################
        self.tools = Stack(
            name = "toolstack",
            transition_type="slide-left-right",
            transition_duration=500,
            children=[self.note, self.chat, self.box_apps],

        )
## STACK CHILD SWITCH BUTTONS
#############################################################
        self.switch_tool = Box(
            name = 'stack_buttons',
            orientation = 'h',
            spacing = 7,
            children = [
                Button(name="zebuttons",label=" ", on_clicked=lambda *_: self.tools.set_visible_child(self.note),),
                Button(name="zebuttons",label=" ", on_clicked=lambda *_: self.tools.set_visible_child(self.chat),),
                Button(name="zebuttons",label=" ", on_clicked=lambda *_: self.tools.set_visible_child(self.box_apps),)
            ]
        )


## idk lol
        self.update_status()
        invoke_repeater(
            15 * 60 * 1000,  # every 15min
            lambda: (self.uptime_label.set_label(self.get_current_uptime()), True)[1],
        )
        invoke_repeater(1000, self.update_status)
        self.add(
            Box(
                name="window-inner",
                orientation="v",
                spacing=15,
                children=[self.header, self.greeter_label, self.progress_container, self.switch_tool, self.tools],
            ),
        )
        self.show_all()

## APP LAUNCHER FUNTIONS

    def arrange_viewport(self, query: str = ""):
        # reset everything so we can filter current viewport's slots...
        # remove the old handler so we can avoid race conditions
        remove_handler(self._arranger_handler) if self._arranger_handler else None

        # remove all children from the viewport
        self.viewport.children = []

        # make a new iterator containing the filtered apps
        filtered_apps_iter = iter(
            [
                app
                for app in self._all_apps
                if query.casefold()
                in (
                    (app.display_name or "")
                    + (" " + app.name + " ")
                    + (app.generic_name or "")
                ).casefold()
            ]
        )
        should_resize = operator.length_hint(filtered_apps_iter) == len(self._all_apps)

        # all aboard...
        # start the process of adding slots with a lazy executor
        # using this method makes the process of adding slots way more less
        # resource expensive without blocking the main thread and resulting in a lock
        self._arranger_handler = idle_add(
            lambda *args: self.add_next_application(*args)
            or (self.resize_viewport() if should_resize else False),
            filtered_apps_iter,
            pin=True,
        )

        return False

    def add_next_application(self, apps_iter: Iterator[DesktopApp]):
        if not (app := next(apps_iter, None)):
            return False

        self.viewport.add(self.bake_application_slot(app))
        return True

    def resize_viewport(self):
        self.scrolled_window.set_min_content_width(
            self.viewport.get_allocation().width  # type: ignore
        )
        return False

    def bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
        return Button(
            name='appslot',
            child=Box(
                orientation="h",
                spacing=12,
                children=[
                    Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
                    Label(
                        label=app.display_name or "Unknown",
                        v_align="center",
                        h_align="center",
                    ),
                ],
            ),
            tooltip_text=app.description,
            on_clicked=lambda *_: (app.launch()),
            **kwargs,
        )




## some more functiona
    def update_status(self):
        self.disk_progress.value = psutil.disk_usage('/home').percent
        self.ram_progress.value = psutil.virtual_memory().percent
        if not (bat_sen := psutil.sensors_battery()):
            self.bat_circular.value = 42
        else:
            self.bat_circular.value = bat_sen.percent

        return True

    def get_current_uptime(self):
        uptime = time.time() - psutil.boot_time()
        uptime_days, remainder = divmod(uptime, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        # uptime_minutes, _ = divmod(remainder, 60)
        return f"{int(uptime_days)} {'days' if uptime_days > 1 else 'day'}, {int(uptime_hours)} {'hours' if uptime_hours > 1 else 'hour'}"


if __name__ == "__main__":
    side_panel = SidePanel()
    app = Application("side-panel", side_panel)
    app.set_stylesheet_from_file(get_relative_path("side_panel.css"))

    app.run()
