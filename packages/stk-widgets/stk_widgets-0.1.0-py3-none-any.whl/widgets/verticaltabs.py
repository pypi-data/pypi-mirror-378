import customtkinter as ct
from .buttons import CircleButton
from typing import Literal


class VerticalTab(ct.CTkFrame):
    """
    Vertical tabs for custom tkinter
    
    Attributes:
        parent (tk.Frame|ct.CTkFrame|ct.CTk): parent frame.
        width (int): width of the vertical tab.
        height(int): height of the vertical tab.
        sidebar_width: the width of the sidebar.
    """
    def __init__(self, parent, width:int=None, height:int=None, sidebar_width=120, **kwargs):
        width = width if width is not None else parent.winfo_width()
        height = height if height is not None else parent.winfo_height()
        super().__init__(parent, width=width, height=height, **kwargs)

        self._sidebar_width = sidebar_width
        self._tabs = {}
        self._current_tab = None

        # Sidebar for buttons
        self._sidebar = ct.CTkFrame(self, width=self._sidebar_width)
        self._sidebar.pack(side="left", fill="y")

        # Content area for tab frames
        self._content_area = ct.CTkFrame(self)
        self._content_area.pack(side="right", fill="both", expand=True)
        

    def add_tab(self, tab_name: str = "Tab", diameter: int = 60,
                button_style:Literal["circular", "regular"] = "circular", **btn_kwargs):
        """
        Adds a new tab with a circular button.

        :param tab_name: Name of the tab
        :param button_style: Button style(can either be "circular" or "regular")
        :param diameter: Diameter of the circle button if button is circular
        :param btn_kwargs: Extra kwargs passed to Button (fg_color, image, etc.)
        """
        if button_style not in ["circular", "regular"]:
            raise ValueError("button_style must be 'circular' or 'regular'")
        
        if button_style == "circular":
            # Create circular tab button
            btn = CircleButton(
                self._sidebar,
                diameter=diameter,
                text=tab_name,
                command=lambda name=tab_name: self.open_tab(name),
                # fg_color="red",
                **btn_kwargs
            )
            btn.pack(pady=8, padx=5)
        
        elif button_style == "regular":
            btn = ct.CTkButton(
                self._sidebar,
                text=tab_name,
                command=lambda name=tab_name: self.open_tab(name),
                **btn_kwargs
            )
            btn.pack(pady=8, padx=5)

        # Create corresponding frame
        frame = ct.CTkFrame(self._content_area)
        self._tabs[tab_name] = frame

        # Show first tab by default
        if self._current_tab is None:
            self.open_tab(tab_name)

        return frame  # allow user to add widgets inside the tab

    def open_tab(self, tab_name: str):
        # Hide current
        if self._current_tab is not None:
            self._tabs[self._current_tab].pack_forget()

        # Show new
        self._tabs[tab_name].pack(fill="both", expand=True)
        self._current_tab = tab_name
