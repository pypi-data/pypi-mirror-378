import customtkinter as ctk
import tkinter as tk
from .layouts import print_red


class Utils:
    """Helper utilities for geometry parsing and constraints."""

    @staticmethod
    def parse_geometry(geometry: str):
        """Parse 'WxH+X+Y' into integers."""
        w, rest = geometry.split("x")
        h, x, y = rest.replace("+", " ").split()
        return int(w), int(h), int(x), int(y)

    @staticmethod
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))


class TitleBar(ctk.CTkFrame):
    """Custom set_title bar with optional widgets and buttons."""

    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, fg_color="gray20", **kwargs)
        self.pack(fill="x", side="top")

        # Internal state
        self._set_title_var = tk.StringVar(value="CustomTk Window")
        self._drag_start_x = None
        self._drag_start_y = None
        self._win_btns = []

        # Title label
        self.set_title_label = ctk.CTkLabel(self, textvariable=self._set_title_var, anchor="w")
        self.set_title_label.pack(side="left", padx=10)

        # Right container for custom widgets and buttons
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right")

        # Drag bindings
        self.bind("<ButtonPress-1>", self._start_move)
        self.bind("<B1-Motion>", self._on_move)
        self.set_title_label.bind("<ButtonPress-1>", self._start_move)
        self.set_title_label.bind("<B1-Motion>", self._on_move)

    def set_title(self, text: str):
        """Set window set_title text."""
        self._set_title_var.set(text)

    def add_widget(self, widget: ctk.CTkBaseClass):
        """Add custom widget to the set_title bar (right side)."""
        widget.master = self
        widget.pack(side="right", padx=5, pady=2)

    def add_default_winbtns(self):
        """Add minimize, maximize, close buttons."""
        btn_conf = {"width": 25, "height": 25, "corner_radius": 4, "fg_color": "gray30"}

        close_btn = ctk.CTkButton(self.right_container, text="✕", command=self.master.destroy, **btn_conf)
        max_btn = ctk.CTkButton(self.right_container, text="⬜", command=self.master.toggle_maximize, **btn_conf)
        min_btn = ctk.CTkButton(self.right_container, text="━", command=self.master.iconify, **btn_conf)

        for btn in (min_btn, max_btn, close_btn):
            self.add_widget(btn)
            self._win_btns.append(btn)

    def _start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_move(self, event):
        x = self.master.winfo_x() + event.x - self._drag_start_x
        y = self.master.winfo_y() + event.y - self._drag_start_y
        self.master.geometry(f"+{x}+{y}")


class ResizeHandler:
    """Handles 8 resize grips with correct cursors."""

    def __init__(self, master):
        self.master = master
        self.min_width = 150
        self.min_height = 100

        self._handles = []
        self._create_handles()

    def _create_handles(self):
        grip_conf = {"fg_color": "transparent"}

        # Edges
        top = ctk.CTkFrame(self.master, height=5, cursor="size_ns", **grip_conf)
        bottom = ctk.CTkFrame(self.master, height=5, cursor="size_ns", **grip_conf)
        left = ctk.CTkFrame(self.master, width=5, cursor="size_we", **grip_conf)
        right = ctk.CTkFrame(self.master, width=5, cursor="size_we", **grip_conf)

        # Corners
        topleft = ctk.CTkFrame(self.master, width=8, height=8, cursor="fleur", **grip_conf)
        topright = ctk.CTkFrame(self.master, width=8, height=8, cursor="fleur", **grip_conf)
        bottomleft = ctk.CTkFrame(self.master, width=8, height=8, cursor="fleur", **grip_conf)
        bottomright = ctk.CTkFrame(self.master, width=8, height=8, cursor="fleur", **grip_conf)

        handles = {
            "top": (top, "n"),
            "bottom": (bottom, "s"),
            "left": (left, "w"),
            "right": (right, "e"),
            "topleft": (topleft, "nw"),
            "topright": (topright, "ne"),
            "bottomleft": (bottomleft, "sw"),
            "bottomright": (bottomright, "se"),
        }

        for name, (frame, anchor) in handles.items():
            frame.place(relx=0 if "left" in name else 1 if "right" in name else 0.5,
                        rely=0 if "top" in name else 1 if "bottom" in name else 0.5,
                        anchor=anchor)
            frame.bind("<B1-Motion>", lambda e, a=anchor: self._do_resize(e, a))
            self._handles.append(frame)

    def _do_resize(self, event, anchor):
        x, y = self.master.winfo_pointerx(), self.master.winfo_pointery()
        geom = self.master.geometry()
        w, h, px, py = Utils.parse_geometry(geom)

        if "e" in anchor:
            w = max(self.min_width, x - px)
        if "s" in anchor:
            h = max(self.min_height, y - py)
        if "w" in anchor:
            delta = x - px
            w = max(self.min_width, w - delta)
            px = x
        if "n" in anchor:
            delta = y - py
            h = max(self.min_height, h - delta)
            py = y

        self.master.geometry(f"{w}x{h}+{px}+{py}")


class STk(ctk.CTk):
    """
    Custom window implementation, buggy af.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overrideredirect(True)  # Remove OS border
        self._is_maximized = False
        self._normal_geometry = None
        print_red("STk is a rudimentary attempt at a custom window, it is very buggy so only use if you can fix or are okay with it")

        # Title bar
        self.set_titlebar = TitleBar(self)
        self.body = ctk.CTkFrame(self, fg_color="gray15")
        self.body.pack(fill="both", expand=True)

        # Resize handler
        self.resizer = ResizeHandler(self)

    def set_title(self, text: str):
        self.set_titlebar.set_title(text)
        super().title(text)

    def add_widget_to_titlebar(self, widget):
        self.set_titlebar.add_widget(widget)

    def add_default_winbtns(self):
        self.set_titlebar.add_default_winbtns()

    def toggle_maximize(self):
        if not self._is_maximized:
            self._normal_geometry = self.geometry()
            self.state("zoomed")
            self._is_maximized = True
        else:
            if self._normal_geometry:
                self.geometry(self._normal_geometry)
            self._is_maximized = False