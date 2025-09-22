import customtkinter as ctk

class STkMenuBar(ctk.CTkFrame):
    def __init__(self, master, dropdown_radius: int = 6, **kwargs):
        """
        A custom dropdown menu with light and dark themes.
        Arguments:
            master  -- The master window.
            dropdown_radius(int) -- The corner radius of the dropdown menu.
        """
        super().__init__(master, height=30, **kwargs)
        self.pack(fill="x", side="top")
        
        self.dropdown_radius = dropdown_radius
        self.menus = {}
    
    def add_menu(self, label, items, text_color: str | list[str,] | tuple[str, str] = ("gray10", "#DCE4EE")):
        """Create a menu with dropdown items.

        Args:
            label (str): Text on the menubar.
            items (dict): { "Label": command, ... } for dropdown.
            text_color (str|list|tuple): Color of the menu item text.
        """
        menu_button = ctk.CTkButton(
            self,
            text=label,
            text_color=text_color,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            width=80,
            height=30,
            anchor="w",
            command=lambda: self._toggle_dropdown(label),
        )
        menu_button.pack(side="left", padx=2, pady=2)
        menu_button.bind("<Enter>", lambda e: self._toggle_dropdown(label))
        
        # Dropdown frame
        dropdown = ctk.CTkFrame(self.master, corner_radius=self.dropdown_radius)
        dropdown_items = []
        for text, cmd in items.items():
            btn = ctk.CTkButton(
                dropdown,
                text=text,
                fg_color="transparent",
                text_color=text_color,
                hover_color=("gray70", "gray20"),
                width=120,
                anchor="w",
                command=lambda c=cmd, l=label: self._run_command(c, l),
            )
            btn.pack(fill="x", padx=2, pady=1)
            dropdown_items.append(btn)
        
        self.menus[label] = {"button": menu_button, "dropdown": dropdown, "items": dropdown_items}
    
    def _toggle_dropdown(self, label):
        menu = self.menus[label]
        dropdown = menu["dropdown"]
        
        # Hide all other dropdowns first
        for m_label, m in self.menus.items():
            if m_label != label:
                m["dropdown"].place_forget()
        
        # Show this dropdown
        if not dropdown.winfo_ismapped():
            x = menu["button"].winfo_rootx() - self.master.winfo_rootx()
            y = self.winfo_height()
            dropdown.place(x=x, y=y)
            
            # --- Auto-hide on leave ---
            #def schedule_hide():
            #    dropdown._hide_job = self.after(300, dropdown.place_forget)
            
            def check_leave(event):
                # Get current mouse position
                mx, my = event.x_root, event.y_root
                dx, dy = dropdown.winfo_rootx(), dropdown.winfo_rooty()
                dw, dh = dropdown.winfo_width(), dropdown.winfo_height()
                if not (dx <= mx <= dx + dw and dy <= my <= dy + dh):
                    dropdown.place_forget()
            
            def cancel_hide(event=None):
                if hasattr(dropdown, "_hide_job"):
                    self.after_cancel(dropdown._hide_job)
                    del dropdown._hide_job
            
            dropdown.bind("<Leave>", lambda e: check_leave(e))
            dropdown.bind("<Enter>", cancel_hide)
            
            # --- Auto-hide on outside click ---
            def outside_click(event):
                dx, dy = dropdown.winfo_rootx(), dropdown.winfo_rooty()
                dw, dh = dropdown.winfo_width(), dropdown.winfo_height()
                if not (dx <= event.x_root <= dx + dw and dy <= event.y_root <= dy + dh):
                    dropdown.place_forget()
                    self.master.unbind("<Button-1>")
            
            self.master.bind("<Button-1>", outside_click)
    
    def _run_command(self, cmd, label):
        self.menus[label]["dropdown"].place_forget()
        if cmd:
            cmd()

