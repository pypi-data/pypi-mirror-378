import customtkinter as ct
import math



class Spinner(ct.CTkCanvas):
    """
    A canvas drawn spinner for loading animations.
    """
    def __init__(self, parent, size=50, line_width=5, line_count=12, color="skyblue", speed=100, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        
        self.parent = parent
        self._size = size
        self._line_width = line_width
        self.line_count = line_count
        self._color = color
        self._speed = speed
        self._angle = 0
        
        self._lines = []
        self._create_lines()
        self._animate()
        self.update_bg()
    
    def _create_lines(self):
        self.delete("all")
        radius = self._size // 2 - self._line_width
        center = self._size // 2
        for i in range(self.line_count):
            angle = (2 * math.pi / self.line_count) * i
            x1 = center + radius * math.cos(angle)
            y1 = center + radius * math.sin(angle)
            x2 = center + (radius - self._line_width * 2) * math.cos(angle)
            y2 = center + (radius - self._line_width * 2) * math.sin(angle)
            line = self.create_line(x1, y1, x2, y2, width=self._line_width, fill=self._color, capstyle="round")
            self._lines.append(line)
    
    def _animate(self):
        self._angle = (self._angle + 1) % self.line_count
        for i, line in enumerate(self._lines):
            alpha = (i - self._angle) % self.line_count
            brightness = int(200 * (alpha / self.line_count)) + 55
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            self.itemconfig(line, fill=color)
        self.after(self._speed, self._animate)
    
    def update_bg(self):
        bg=self.parent.cget("bg")
        self.configure(bg=bg)
        self.after(250, self.update_bg)


class ArcSpinner(ct.CTkCanvas):
    def __init__(self, parent, size=60, arc_length=90, line_width=8, color="skyblue", speed=10, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        
        self.parent = parent
        self._size = size
        self._arc_length = arc_length
        self._line_width = line_width
        self._color = color
        self._speed = speed  # smaller = faster
        self._angle = 0
        
        # Draw initial arc
        self._arc = self.create_arc(
            self._line_width, self._line_width,
            self._size - self._line_width, self._size - self._line_width,
            start=self._angle, extent=self._arc_length,
            style="arc", width=self._line_width, outline=self._color
        )
        
        self._animate()
        self.update_bg()
    
    def _animate(self):
        self._angle = (self._angle + self._speed) % 360
        self.itemconfig(self._arc, start=self._angle)
        self.after(20, self._animate)
    
    def update_bg(self):
        bg=self.parent.cget("bg")
        self.configure(bg=bg)
        self.after(250, self.update_bg)