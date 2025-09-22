import customtkinter as ct
from typing import Tuple, Any


class ClickableLabel(ct.CTkLabel):
    """
    A label that can be clicked.
    Use it for links or whatever.
    """
    
    def __init__(self, master,
                 text_color: Tuple[str, str] | Any = ("#1F6AA5", "#60A5FA"),
                 text_hover_color: Tuple[str, str] | Any = ("#144870", "#3B82F6"),
                 command=None, **kwargs):
        
        super().__init__(master, text_color=text_color, **kwargs)
        self._normal_color = text_color
        self._hover_color = text_hover_color
        self._command = command
        
        self.bind("<Enter>", lambda e: self.configure(text_color=self._hover_color))
        self.bind("<Leave>", lambda e: self.configure(text_color=self._normal_color))
        
        if self._command:
            self.bind("<Button-1>", self._run)
    
    def _run(self, event=None):
        if self._command:
            self._command()
