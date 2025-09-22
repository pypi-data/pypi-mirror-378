import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk, ImageFont


def _normalize_ctk_color(value):
    """
    Convert a CTk color representation to a single color string for the
    current appearance mode. Handles:
      - tuple/list like ("light","dark")
      - stringified CTkColor like "light dark"
      - single color string like "#ffffff" or "gray20"
    """
    mode_is_dark = str(ctk.get_appearance_mode()).lower() == "dark"
    
    # tuple/list form
    if isinstance(value, (tuple, list)) and len(value) >= 2:
        return value[1] if mode_is_dark else value[0]
    
    # string (maybe "light dark" or just one token)
    s = str(value).strip()
    parts = s.split()
    if len(parts) >= 2:
        # pick appropriate token according to mode
        return parts[1] if mode_is_dark else parts[0]
    
    # fallback: return the string as-is
    return s


def get_parent_bg(widget):
    """
    Return a single color string for the widget's background.
    Tries, in order: widget.cget("fg_color"), widget.cget("bg"), parent's fg_color, toplevel's fg_color,
    ThemeManager defaults. Always returns a single token string.
    """
    # try a sequence of candidate widgets to query
    candidates = [widget, getattr(widget, "master", None)]
    try:
        # widget.winfo_toplevel() may raise if widget not yet fully realized, handle safely
        candidates.append(widget.winfo_toplevel())
    except Exception:
        pass
    
    for w in candidates:
        if w is None:
            continue
        # try fg_color first (CTk widgets)
        try:
            raw = w.cget("fg_color")
            return _normalize_ctk_color(raw)
        except Exception:
            # not a CTk-style widget or no fg_color — try plain bg
            try:
                raw = w.cget("bg")
                return _normalize_ctk_color(raw)
            except Exception:
                continue
    
    # final fallback: theme defaults (CTk top-level theme values)
    theme_default = ctk.ThemeManager.theme.get("CTk", {}).get("fg_color", "#ffffff")
    return _normalize_ctk_color(theme_default)


class CircleButton(ctk.CTkCanvas):
    """
    Circular button widget.
    
    Attributes:
        master: The parent widget.
        diameter: The circular button diameter.
        fg_color: The foreground color.
        hover_color: The hover color.
        text: Text to be displayed.
        text_color: color of text.
        image: Image to be displayed.
        command: command to be executed.
    """
    def __init__(self, master=None, diameter=100, fg_color: str | tuple[str] | list[str] = ("#1f6aa5", "#0d1b2a"),
                 hover_color: str | tuple[str] | list[str] = ("#007acc", "#1b263b"), text="",
                 text_color: str | tuple[str, str] | list[str] = ("#0d0d0d", "#f5f5f5"),
                 image=None, command=None, **kwargs):
        parent_bg = get_parent_bg(master)
        super().__init__(master, width=diameter, height=diameter,
                         highlightthickness=0, bg=parent_bg, **kwargs)
        
        self._diameter = diameter
        self.parent_bg = parent_bg
        
        self._pre_fg = fg_color
        self._last_mode = ctk.get_appearance_mode()
        self.fg_color = _normalize_ctk_color(fg_color)
        self._pre_hover = hover_color
        self.hover_color = _normalize_ctk_color(hover_color)
        self._text = text
        self._pre_text = text_color
        self._text_color = _normalize_ctk_color(text_color)
        self._command = command
        
        self._user_image = None
        if image:
            if isinstance(image, str):
                self._user_image = Image.open(image).convert("RGBA")
            else:
                self._user_image = image.convert("RGBA")
        
        self._tk_image = None
        
        self._draw_circle(self.fg_color)
        
        self.bind("<Enter>", lambda e: self._draw_circle(self.hover_color))
        self.bind("<Leave>", lambda e: self._draw_circle(self.fg_color))
        self.bind("<Button-1>", lambda e: self._command() if self._command else None)
        self.bind("<Configure>", self._resize)
        self.update_bg()
    
    def _draw_circle(self, color):
        size = min(self.winfo_width(), self.winfo_height()) or self._diameter
        # Use higher-resolution temporary image to smooth edges
        scale_factor = 4
        high_res_size = size * scale_factor
        
        img = Image.new("RGBA", (high_res_size, high_res_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw smooth circular background
        draw.ellipse((0, 0, high_res_size, high_res_size), fill=color)
        
        # Draw user image if provided
        if self._user_image:
            img_resized = self._user_image.resize((high_res_size, high_res_size), Image.LANCZOS)
            mask = Image.new("L", (high_res_size, high_res_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, high_res_size, high_res_size), fill=255)
            img.paste(img_resized, (0, 0), mask)
        
        # Draw text if provided
        if self._text:
            font_size = max(10, high_res_size // 4)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = None
            draw.text((high_res_size // 2, high_res_size // 2),
                      self._text, fill=self._text_color,
                      anchor="mm", font=font)
        
        # Downscale to actual size for anti-aliased edges
        img = img.resize((size, size), Image.LANCZOS)
        
        self._tk_image = ImageTk.PhotoImage(img)
        self.delete("all")
        self.create_image(size // 2, size // 2, image=self._tk_image)
    
    def _resize(self, event):
        self._draw_circle(self.fg_color)
    
    def update_bg(self, event=None):
        self.parent_bg = get_parent_bg(self.master)
        
        self.configure()
        
        current_mode = ctk.get_appearance_mode()
        if current_mode != self._last_mode:
            self._last_mode = current_mode
            self.fg_color = _normalize_ctk_color(self._pre_fg)
            self.hover_color = _normalize_ctk_color(self._pre_hover)
            self._text_color = _normalize_ctk_color(self._pre_text)
            
            self._draw_circle(self.fg_color)
        self.after(250, self.update_bg)
    
    def configure(self, diameter: int = None, fg_color: str | tuple[str] | list[str] = None,
                  hover_color: str | tuple[str] | list[str] = None, text: str = None,
                  text_color: str | tuple[str] | list[str] = None, image = None, command=None,
                  **kwargs):
        if diameter:
            self._diameter = diameter
        if fg_color:
            self._pre_fg = fg_color
            self.fg_color = _normalize_ctk_color(fg_color)
        if hover_color:
            self._pre_hover = hover_color
            self.hover_color = _normalize_ctk_color(hover_color)
        if text:
            self._text = text
        if text_color:
            self._pre_text = text_color
            self._text_color = _normalize_ctk_color(text_color)
        if image:
            try:
                if isinstance(image, str):
                    self._user_image = Image.open(image).convert("RGBA")
                else:
                    self._user_image = image.convert("RGBA")
            except Exception as e:
                print(e)
        if command:
            self._command = command
        self._draw_circle(self.fg_color)
        super().configure(bg  = self.parent_bg)
    
    ctk.ThemeManager.theme_change_callback = update_bg


# === Example Usage ===
#if __name__ == "__main__":
#    ctk.set_appearance_mode("dark")
#    ctk.set_default_color_theme("blue")
#
#    root = ctk.CTk()
#    root.geometry("400x400")
#
#    # Button with text only
#    btn1 = CircleButton(root, text="Agnosia", fg_color="#1f6aa5",
#                        hover_color="#144870", command=lambda: print("Go clicked"))
#    btn1.pack(expand=True, padx=20, pady=20)
#
#    root.mainloop()
#