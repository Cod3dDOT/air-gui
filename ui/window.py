import gi

# pylint: disable=wrong-import-position

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

# pylint: enable=wrong-import-position

from ui.interface import InterfacePage


@Gtk.Template(filename="data/ui/compiled/window.ui")
class MainWindow(Adw.ApplicationWindow):
    """Starting window"""

    __gtype_name__ = "MainWindow"

    main_stack = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
        Adw.ApplicationWindow.__init__(self, *args, **kwargs)
        self.style_manager = Adw.StyleManager().get_default()
        self.style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)

        # pylint: disable=no-member
        self.main_stack.add_titled(InterfacePage(), "Interfaces", "Interfaces")  # type: ignore
        # self.main_stack.add_child(self.aircrack_page)  # type: ignore