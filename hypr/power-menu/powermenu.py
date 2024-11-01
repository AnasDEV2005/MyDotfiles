import psutil
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.overlay import Overlay
from fabric.widgets.eventbox import EventBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.window import Window
from fabric.hyprland.widgets import Language, ActiveWindow, Workspaces, WorkspaceButton
from fabric.utils import (
    FormattedString,
    bulk_replace,
    invoke_repeater,
    get_relative_path,
    exec_shell_command
)




class PowerMenu(Window):
    def power_off(self, *_):
        exec_shell_command('shutdown now')
    def logout(self, *_):
        exec_shell_command('loginctl terminate-user geronimo')
    def sleep(self, *_):
        exec_shell_command('systemctl sleep')
    def restart(self, *_):
        exec_shell_command('reboot')
    
    def __init__(
        self,
    ):
        super().__init__(
            name="pwrmenu",
            title='power-menu',
            type="popup",
            exclusivity="none",
            visible=True,
            all_visible=True,
        )
        self.top_group = Box(
            name="top-container",
            orientation="h",
            spacing=12,
            children=[
                Button(
                    child=Label(label="⏻", style="font-size: 9px;"),
                    on_clicked= lambda *_: self.power_off(),),
                Button(
                    child=Label(label="↤", style="font-size: 9px;"),
                    on_clicked= lambda *_: self.logout(),),
                Button(
                    child=Label(label="⏾", style="font-size: 9px;"),
                    on_clicked= lambda *_: self.sleep(),),
                Button(
                    child=Label(label="⟲", style="font-size: 9px;"),
                    on_clicked= lambda *_: self.restart(),),
            ],)
        self.bottom_group = Box(
            name="bottom-container",
            orientation="h",
            spacing=12,
            children=[
                Button(
                    child=Label(label="Cancel", style="font-size: 9px;"),
                    on_clicked= lambda *_: self.cancel(),),

            ],)
        self.add(Box(
            name='menu',
            orientation='v',
            spacing=24,
            children=[self.top_group, self.bottom_group,],

        ))
        self.show_all()

        
if __name__ == "__main__":
    pwr = PowerMenu()
    app = Application("power-menu", pwr)
    app.set_stylesheet_from_file(get_relative_path("powermenu.css"))

    app.run()
