import customtkinter as ct


class PasswordEntry(ct.CTkFrame):
    
    def __init__(self, master, placeholder_text:int|str = "password", eye_open_img=None, eye_closed_img=None,
                 password_show_text: str = "Show", password_hide_text: str = "Hide",
                 corner_radius: int = 8, button_color: str | tuple[str] | list[str] = ("#1f6aa5", "#0d1b2a"),
                 button_hover_color: str | tuple[str] | list[str] = ("#007acc", "#1b263b"),
                 button_text_color: str | tuple[str] | list[str] = ("#0d0d0d", "#f5f5f5"),
                 radius_affects_children: bool = False, **kw):
        """
        An Entry widget for a password entry.
        :param radius_affects_children : determines if the child entry and button are affected by the corner radius given
        """
        super().__init__(master, **kw)
        self._show = False
        self._show_text = password_show_text
        self._hide_text = password_hide_text
        
        # Store icons (can be None)
        self._eye_open_img = eye_open_img
        self._eye_closed_img = eye_closed_img
        
        # Entry takes most of the space
        self._pin_entry = ct.CTkEntry(self, show="*",placeholder_text=placeholder_text
        , corner_radius=corner_radius if radius_affects_children else 0)
        self._pin_entry.pack(fill="x", expand=True, side="left")
        
        # Button: start with closed-eye image OR fallback to hide_text
        self._view_p = ct.CTkButton(
            self,
            command=self.toggle_password,
            text=self._show_text if self._eye_closed_img is None else "",
            image=self._eye_closed_img,
            width=50 if self._eye_closed_img is None else 30,
            corner_radius=corner_radius if radius_affects_children else 0,
            fg_color=button_color,
            hover_color=button_hover_color,
            text_color=button_text_color
        )
        self._view_p.pack(side="left")
    
    def get(self):
        return self._pin_entry.get()
    
    def toggle_password(self):
        """Toggle between hidden (*) and visible text"""
        if self._show:
            self._pin_entry.configure(show="*")
            if self._eye_closed_img:  # use images if available
                self._view_p.configure(image=self._eye_closed_img, text="")
            else:  # fallback to text
                self._view_p.configure(text=self._show_text)
        else:
            self._pin_entry.configure(show="")
            if self._eye_open_img:
                self._view_p.configure(image=self._eye_open_img, text="")
            else:
                self._view_p.configure(text=self._hide_text)
        self._show = not self._show
    
    def configure(self, eye_open_img=None, eye_closed_img=None,
                  password_show_text: str = None, password_hide_text: str = None,
                  corner_radius: int = None, button_color: str | tuple[str] | list[str] = None,
                  button_hover_color: str | tuple[str] | list[str] = None,
                  button_text_color: str | tuple[str] | list[str] = None,
                  radius_affects_children: bool = False, require_redraw=False, **kwargs):
        if button_color:
            self._view_p.configure(fg_color=button_color)
        if button_hover_color:
            self._view_p.configure(hover_color=button_hover_color)
        if password_show_text:
            self._show_text = password_show_text
        if password_hide_text:
            self._hide_text = password_hide_text
        if eye_open_img:
            self._eye_open_img = eye_open_img
        if eye_closed_img:
            self._eye_closed_img = eye_closed_img
        if corner_radius:
            if radius_affects_children:
                self._view_p.configure(corner_radius=corner_radius)
                self._pin_entry.configure(corner_radius=corner_radius)
        if button_text_color:
            self._view_p.configure(text_color=button_text_color)
        
        return super().configure(corner_radius if corner_radius is not None else 0,require_redraw=require_redraw, **kwargs)