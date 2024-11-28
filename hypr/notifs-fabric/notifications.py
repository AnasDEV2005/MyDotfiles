from typing import cast

from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.image import Image
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow
from fabric.notifications import Notifications, Notification
from fabric.utils import invoke_repeater, get_relative_path

from gi.repository import GdkPixbuf
from gi.repository import Gtk, Gdk
from gi.repository import GObject


#############################################################################################################################
NOTIFICATION_WIDTH = 360
NOTIFICATION_IMAGE_SIZE = 64
NOTIFICATION_TIMEOUT = 7 * 1000  # 10 seconds


def capture_widget_as_image(widget):
    """
    Captures the given widget as a GdkPixbuf.
    """
    offscreen_window = Gtk.OffscreenWindow()
    offscreen_window.add(widget)
    offscreen_window.show_all()

    # Ensure the widget is rendered
    while Gtk.events_pending():
        Gtk.main_iteration()

    # Capture the widget as a GdkPixbuf
    allocation = widget.get_allocation()
    width, height = allocation.width, allocation.height
    pixbuf = Gdk.pixbuf_get_from_window(offscreen_window.get_window(), 0, 0, width, height)
    offscreen_window.destroy()
    return pixbuf


def animate_image_off_screen(image_widget, target_x, target_y, duration=500):
    """
    Animates the image widget to move off-screen.
    """
    initial_x, initial_y = image_widget.get_allocation().x, image_widget.get_allocation().y
    dx = (target_x - initial_x) / duration
    dy = (target_y - initial_y) / duration

    def on_timeout():
        nonlocal initial_x, initial_y
        initial_x += dx
        initial_y += dy
        image_widget.set_margin_start(int(initial_x))
        image_widget.set_margin_top(int(initial_y))

        if abs(initial_x - target_x) < 1 and abs(initial_y - target_y) < 1:
            image_widget.hide()
            return False
        return True

    from gi.repository import GLib
    GLib.timeout_add(10, on_timeout)


def show_notification(notification_widget):
    """
    Captures the widget as an image and animates it off-screen.
    """
    pixbuf = capture_widget_as_image(notification_widget)
    if not pixbuf:
        print("Failed to capture widget.")
        return

    # Create an image widget from the captured pixbuf
    image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
    image_window = Gtk.Window()
    image_window.set_decorated(False)
    image_window.set_position(Gtk.WindowPosition.CENTER)
    image_window.add(image_widget)
    image_window.show_all()

    # Start animation
    animate_image_off_screen(image_window, target_x=800, target_y=-200)


##################################################################################################################

applist=['vesktop', 'flameshot', 'pipewire-pulse', 'pipewire', 'brave']
class NotificationWidget(Box):
    def __init__(self, notification: Notification, **kwargs):
        super().__init__(
            size=(NOTIFICATION_WIDTH, -1),
            name="notification",
            spacing=0,
            orientation="h",
            **kwargs,
        )

        self._notification = notification


        if image_pixbuf := self._notification.image_pixbuf:
            if self._notification.app_name == "vesktop":
                self.bodconbox.add(Image(
                        name="notificationvesktop",
                        pixbuf=image_pixbuf.scale_simple(
                            NOTIFICATION_IMAGE_SIZE,
                            NOTIFICATION_IMAGE_SIZE,
                            GdkPixbuf.InterpType.BILINEAR,
                        )))
        if image_pixbuf := self._notification.image_pixbuf:
            if self._notification.app_name == "brave":
                self.bodconbox.add(Image(
                        name="notificationbrave",
                        pixbuf=image_pixbuf.scale_simple(
                            NOTIFICATION_IMAGE_SIZE,
                            NOTIFICATION_IMAGE_SIZE,
                            GdkPixbuf.InterpType.BILINEAR,
                        )))
        if image_pixbuf := self._notification.image_pixbuf:
            if self._notification.app_name == "flameshot":
                self.bodconbox.add(Image(
                        name="notificationflameshot",
                        pixbuf=image_pixbuf.scale_simple(
                            NOTIFICATION_IMAGE_SIZE,
                            NOTIFICATION_IMAGE_SIZE,
                            GdkPixbuf.InterpType.BILINEAR,
                        )))
            
            

        self.body = Box(                
                name='notificationbox',
                spacing=4,
                orientation="v",
                children=[
                    # a box for holding both the "summary" label and the "close" button
                    Box(
                        orientation="h",
                        children=[
                            Label(
                                label=self._notification.summary,
                                ellipsization="middle",
                            )
                            .build()
                            .add_style_class("summary")
                            .unwrap(),
                        ],
                        h_expand=True,
                        v_expand=True,
                    ),

                    Label(
                        label=self._notification.body,
                        line_wrap="word-char",
                        v_align="start",
                        h_align="start",
                    )
                

                    .build()
                    .add_style_class("body")
                    .unwrap(),
                ],
                h_expand=True,
                v_expand=True,
            )
        if self._notification.app_name in applist:
            for i in applist:
                if self._notification.app_name == i: self.body.set_name('notification'+i)
        if len(self._notification.body)>25: 
                        self.body.children[1].set_label(self._notification.body[:25]+'...')
        self.add(self.body)
##############################################################
####################################################
        # destroy this widget once the notification is closed
        self._notification.connect(
            "closed",
            lambda *_: (
                parent.remove(self) if (parent := self.get_parent()) else None,  # type: ignore
                self.destroy(),
            ),
        )
########################################################################
###########################################################
        # automatically close the notification after the timeout period
        invoke_repeater(
            NOTIFICATION_TIMEOUT,
            lambda: self._notification.close("expired"),
            initial_call=False,
        )
    def notif_close(self):
            pass

if __name__ == "__main__":
    app = Application(
        "notifications",
        WaylandWindow(
            margin="8px 8px 8px 8px",
            anchor="top right",
            child=Box(
                size=2,  # so it's not ignored by the compositor
                spacing=4,
                orientation="v",
            ).build(
                lambda viewport, _: Notifications(
                    on_notification_added=lambda notifs_service, nid: viewport.add(
                        NotificationWidget(
                            cast(
                                Notification,
                                notifs_service.get_notification_from_id(nid),
                            )
                        )
                    )
                )
            ),
            visible=True,
            all_visible=True,
        ),
    )

    app.set_stylesheet_from_file(get_relative_path("./style.css"))

    app.run()
