import customtkinter as ct
from typing import Callable, Optional


# -------------------- Tooltip helper --------------------
class ToolTip:
    """Simple tooltip that adapts to CustomTkinter appearance mode."""

    def __init__(self, widget, text: str ="A widget that does something", delay_ms: int = 300):
        self._widget = widget
        self._text = text
        self._delay_ms = delay_ms
        self._tip = None
        self._after_id = None
        self._mouse_xy = (0, 0)  # store last mouse coords

        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<Motion>", self._track_mouse)  # track cursor position
        widget.bind("<ButtonPress>", self._hide)
        widget.bind("<FocusIn>", self._schedule)
        widget.bind("<FocusOut>", self._hide)

    def _track_mouse(self, event):
        self._mouse_xy = (event.x_root + 10, event.y_root + 10)
        # offset so tooltip doesn't overlap cursor

    def _schedule(self, _event=None):
        self._cancel()
        if not self._text:
            return
        self._after_id = self._widget.after(self._delay_ms, self._show)

    def _cancel(self):
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip is not None:
            return

        x, y = self._mouse_xy

        # Use CTkToplevel, but styled minimally
        tw = ct.CTkToplevel(self._widget)
        tw.overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        try:
            tw.attributes("-topmost", True)
        except Exception:
            pass

        label = ct.CTkLabel(
            tw, text=self._text,
            corner_radius=6, padx=8, pady=6
        )
        label.pack()
        self._tip = tw

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


# ----------------- Right Click ----------------------

class OptionList:
    """
    A reusable popup option list for any widget.
    Appears on Right mouse click disappears when another widget is clicked.
    """
    
    def __init__(self, parent):
        self._parent = parent
        self._opframe: Optional[ct.CTkToplevel] = None
        self._widgets = []  # store label/button configs
        
        # Right-click to trigger
        self._parent.bind("<Button-3>", self.show)
    
    def add_label(self, text: str = "Select an option", font=("Arial", 12)):
        """Add a label to the popup."""
        self._widgets.append(("label", text, font))
    
    def add_button(self, text: str = "Option",
                   color: str | list[str] | tuple[str] | None = ("#F3F4F6", "#21262D"),
                   hover: str | list[str] | tuple[str] | None = ("#21262D", "#F3F4F6"),
                   command: Optional[Callable] = None):
        """Add a button to the popup."""
        self._widgets.append(("button", text, color, hover, command))
    
    def show(self, event=None):
        if self._opframe is not None:
            return
        
        x, y = event.x_root, event.y_root
        
        tw = ct.CTkToplevel(self._parent)
        tw.overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        # dynamically create widgets
        for w in self._widgets:
            if w[0] == "label":
                _, text, font = w
                ct.CTkLabel(tw, text=text, font=font).pack(fill="x", expand=True)
            
            elif w[0] == "button":
                _, text, color, hover, cmd = w
                btn = ct.CTkButton(tw, text=text, hover_color=hover, command=cmd)
                if color:
                    btn.configure(fg_color=color)
                btn.pack(fill="x", expand=True)
                btn.bind("<Button-1>", lambda e: btn.after(1000, self.hide))
        
        self._opframe = tw
        
        self._opframe.bind("<FocusOut>", lambda e: self.hide())
        self._opframe.bind("<Leave>", lambda e: self._opframe.after(2900, self.hide))
        self._opframe.focus_set()
    
    def hide(self, event=None):
        if self._opframe is not None:
            self._opframe.destroy()
            self._opframe = None

