"""
side panel, edited version of the side panel in fabric examples
contains info about the system and a few tools, in webviews
"""

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
from fabric.utils import invoke_repeater, get_relative_path, exec_shell_command

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
            margin="10px 0px 10px 0px",
            keyboard_mode='on-demand',
            exclusivity="auto",
            visible=False,
            all_visible=False,
            **kwargs,
        )


## STATUS BARS
#############################################################################################################################
        self.disk_progress = self.bake_disk_bar()
        self.ram_progress = self.bake_progress_bar()
        self.bat_circular = self.bake_bat_bar().build().set_value(42).unwrap()

        self.progress_container = Box(
            name="progress-bar-container",
            spacing=25,
            orientation="v",
            children=[
                Box(
                    children=[
                        Overlay(
                            child=self.disk_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icons/database.png",
                                    size=27,
                                ),
                            ],
                        ),
                    ],
                ),
                Box(
                    children=[
                        Overlay(
                            child=self.ram_progress,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                    style="margin-right: 4px; text-shadow: 0 0 10px #fff;",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icons/cpu.png",
                                    size=27,
                                ),
                            ],
                        )
                    ]
                ),
                Box(
                    children=[
                        Overlay(
                            child=self.bat_circular,
                            overlays=[
                                self.bake_progress_icon(
                                    label="",
                                    style="margin-right: 0px; text-shadow: 0 0 10px #fff, 0 0 18px #fff;",
                                ),
                                Image(
                                    name="close-svg",
                                    image_file="/home/geronimo/.config/hypr/icons/bat.png",
                                    size=27,
                                ),
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
            size = (290,680),
        )
## CHAT
#############################################################
        self.chat = WebView(
            name='chat',
            url = "https://chatgpt.com",
            size = (290,680),
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
            min_content_size=(290, 320),
            max_content_size=(290, 680),
            child=self.viewport,
        )
        self.window_apps = Window(
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
##################### TOOLS BUTTONS ########################################################################3        

        self.buttons = Box(
            orientation='v',
            children=[
            Button(name='apps',
                    child=Image(
                        name="apps",
                        image_file="/home/geronimo/.config/hypr/icons/x.svg",
                        size=27,
                    ),

                    on_clicked=lambda *_: self.window_apps.show(),
                ),
            ]
        )
         




        self.add(
            Box(
                name="window-inner",
                orientation="v",
                spacing=15,
                children=[self.progress_container,self.buttons],
            ),
        )
        self.update_status()
        self.show_all()




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
