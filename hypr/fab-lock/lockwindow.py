import gi, pam, fabric
from fabric import Application
gi.require_version("GtkSessionLock", "0.1")
from gi.repository import Gdk, GtkSessionLock, GLib
from fabric.widgets.window import Window
from fabric.widgets.entry import Entry
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler, get_relative_path
import os
from loguru import logger
import sys
from datetime import datetime
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from random import randint


def get_profile_picture_path() -> str | None:
    path = os.path.expanduser("~/.config/hypr/antman.png")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
            "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
  )
        path = None
    return path

def get_bg_picture_path() -> str | None:
    path = os.path.expanduser("~/.config/hypr/wallpape.jpg")
    if not os.path.exists(path):
        path = os.path.expanduser("~/.face")
    if not os.path.exists(path):
        logger.warning(
            "can't fetch a user profile picture, add a profile picture image at ~/.face or at ~/Pictures/Other/profile.jpg"
  )
        path = None
    return path









class LockScreen(Window):
    def __init__(self, lock: GtkSessionLock.Lock):
        self.lock = lock
        super().__init__(
            visible=False,
            all_visible=False,
        )



        # Enable key press and release events
        self.set_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)


        self.label = Label(name = "lbl_title", label="VERIFY YOUR IDENTITY")

        self.entry = Entry(name = "pass_entry", size = (2000, 2000),  on_activate=self.on_activate)
        
        self.pfp = Image(size= 260, image_file=get_profile_picture_path())

        self.pam_service = pam.pam()








        self.signals = Box(orientation="h", spacing = 13, name = "signals", children = [
            Box(name = "signal", size = 80),
            Box(name = "signal", size = 80),
            Box(name = "signal", size = 80),
            Box(name = "signal", size = 80),
            Box(name = "signal", size = 80)
        ])

        







        # Set up the UI
        self.box = Box(name="container", orientation="v", spacing=23, children=[self.pfp, self.label, self.signals], style=f"background-image: url(\"file://{get_bg_picture_path() or ''}\")",)
        


        self.add(Overlay(overlays=[self.box, self.entry]))


        self.active_key = 5

    def on_key_press(self, widget, event):
        print("typed")
        signal = randint(0, 4)
        self.signals.children[signal].add_style_class("typing-signal")
        self.signals.children[signal].remove_style_class("no-signal")
        self.active_key = signal


    def on_key_release(self, widget, event):
        print("released")
        for i in range(0, 5):
            self.signals.children[i].remove_style_class("typing-signal")
            self.signals.children[i].add_style_class("no-signal")



    def make_signals_red(self):
        for i in range(0, 5):
            self.signals.children[i].add_style_class("incorrect-signal")
            self.signals.children[i].remove_style_class("no-signal")
    def remove_red_signals(self):    
        for i in range(0, 5):
            self.signals.children[i].remove_style_class("incorrect-signal")
            self.signals.children[i].add_style_class("no-signal")


    def authenticate(self, password):
        return password == "1234" # placeholder dammit

    def on_activate(self, entry: Entry, *args):
        password = entry.get_text()
        if self.authenticate(password):
            self.lock.unlock_and_destroy()
            self.destroy()
        else:
            self.make_signals_red()
            self.entry.set_text("")           
            GLib.timeout_add_seconds(1, lambda: self.remove_red_signals() or False)





if __name__ == "__main__":
    unique_name = f"pylock_{os.getpid()}_{datetime.now().timestamp()}"
    app_instance_name = unique_name.replace(".", "")
    app_name = app_instance_name.replace("_", "-")
    lock = GtkSessionLock.prepare_lock()
    lock.lock_lock()
    lockscreen = LockScreen(lock)
    lock.new_surface(lockscreen, Gdk.Display.get_default().get_monitor(0))
    lockscreen.show_all()
    app = Application(app_name, lockscreen)
    app.set_stylesheet_from_file(get_relative_path("fablock.css"))




    app.run()
