import tkinter as tk
import customtkinter as ct


class TypewriterEffect:
    """
    A class to apply a typewriter animation effect to any tkinter or customtkinter widget
    that supports text updating (via 'configure', 'delete/insert', or similar methods).

    Attributes:
        widget (tk.Widget or ct.CTkBaseClass): Target widget.
        text (str): Full text to reveal.
        delay (int): Milliseconds between characters.
        on_end (Callable[[], None]): Function to execute when the effect ends.
        text_color(str|list|tuple): Color of the text, only if the widget is a label or button.
        _job (str|None): Scheduled 'after' job ID.
        _index (int): Next character index.
    """
    
    def __init__(self, widget, text, delay=50, on_end=None, text_color=None):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._job = None
        self._index = 0
        self.on_end = on_end
        self.text_color = text_color if text_color else "#ffffff"
        
        # Clear existing content
        try:
            # Text-like widgets
            if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                # Text widget requires index arguments
                if isinstance(widget, tk.Text):
                    widget.delete('1.0', tk.END)
                else:
                    widget.delete(0, tk.END)
            # Label-like widgets
            elif hasattr(widget, 'configure'):
                widget.configure(text="")
        except Exception:
            pass
    
    def start(self):
        """Begin or restart the typewriter animation."""
        self.stop()
        self._index = 0
        # Defer first call to ensure widget is rendered.
        self.widget.after_idle(self._schedule_next)
    
    def stop(self):
        """Cancel the animation if running."""
        if self._job:
            try:
                self.widget.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
    
    def _schedule_next(self):
        """Insert the next character and reschedule."""
        if self._index <= len(self.text):
            current = self.text[:self._index]
            self._update_widget(current)
            self._index += 1
            self._job = self.widget.after(self.delay, self._schedule_next)
        else:
            self._job = None
            if self.on_end:
                self.on_end()
    
    def _update_widget(self, current_text):
        """Write current_text into the widget appropriately."""
        # Label-like (tk.Label, ct.CTkLabel)
        if hasattr(self.widget, 'configure'):
            try:
                
                if hasattr(self.widget, 'configure'):
                    if isinstance(self.widget, ct.CTkLabel):
                        self.widget.configure(text=current_text, text_color=self.text_color)
                    elif isinstance(self.widget, tk.Label):
                        
                        self.widget.configure(text=current_text, fg=self.text_color)
            except Exception:
                pass
        
        # Entry-like (tk.Entry, ct.CTkEntry)
        if hasattr(self.widget, 'delete') and hasattr(self.widget, 'insert'):
            try:
                # For tk.Text
                if isinstance(self.widget, tk.Text):
                    self.widget.delete('1.0', tk.END)
                    self.widget.insert(tk.END, current_text)
                else:
                    # For tk.Entry or CTkEntry
                    self.widget.delete(0, tk.END)
                    self.widget.insert(0, current_text)
                return
            except Exception:
                pass
    
    def configure(self, widget=None, text=None, on_end=None, delay=50):
        if widget:
            self.widget = widget
        if text:
            self.text = text
        if on_end:
            self.on_end = on_end
        if delay != 50:
            self.delay = delay