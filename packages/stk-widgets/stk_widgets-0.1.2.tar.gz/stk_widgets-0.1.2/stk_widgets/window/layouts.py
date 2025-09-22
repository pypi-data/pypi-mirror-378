from PIL import ImageGrab
import os, uuid


def screenshot_frame(frame, save_path: str) -> str:
    """
    A simple helper to screenshot the contents of a frame or any tkinter container.
    :param frame: The frame, window or widget to screenshot.
    :param save_path: The path to save the screenshot.
    
    :return: The path to the screenshot.
    """
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    frame.update_idletasks()
    
    # Get the widget’s absolute position relative to the screen
    x = frame.winfo_rootx()
    y = frame.winfo_rooty()
    w = frame.winfo_width()
    h = frame.winfo_height()
    
    # Define bounding box (left, top, right, bottom)
    bbox = (x, y, x + w, y + h)
    
    # Grab image of that region
    img = ImageGrab.grab(bbox)
    #img.show()  # preview
    
    result = os.path.join(save_path, f"shot -{uuid.uuid4()}.png")

    img.save(result)
    return str(result)

class DraggableWidget:
    def __init__(self, widget, constrain_to_parent=True):
        """
        A tool that makes widgets draggable.
        :param widget: The widget to drag
        :param constrain_to_parent: If true, the widget is constrained to parent
        
        :return: None
        """
        self.widget = widget
        self.constrain = constrain_to_parent
        self.widget.update_idletasks()  # Ensure width/height are correct
        self.start_x = 0
        self.start_y = 0
        
        # Bind mouse events
        self.widget.bind("<ButtonPress-1>", self.on_start)
        self.widget.bind("<B1-Motion>", self.on_drag)
        
        # If packed or gridded, switch to place
        self._switch_to_place()
    
    def _switch_to_place(self):
        info = self.widget.pack_info() if self.widget.winfo_manager() == 'pack' else None
        info = info or (self.widget.grid_info() if self.widget.winfo_manager() == 'grid' else None)
        if info:
            self.widget.place(x=self.widget.winfo_x(), y=self.widget.winfo_y())
    
    def on_start(self, event):
        # Record the offset of the cursor in the widget
        self.start_x = event.x
        self.start_y = event.y
    
    def on_drag(self, event):
        # Calculate new position
        x = self.widget.winfo_x() + event.x - self.start_x
        y = self.widget.winfo_y() + event.y - self.start_y
        
        if self.constrain:
            parent = self.widget.master
            max_x = parent.winfo_width() - self.widget.winfo_width()
            max_y = parent.winfo_height() - self.widget.winfo_height()
            x = max(0, min(x, max_x))
            y = max(0, min(y, max_y))
        
        self.widget.place(x=x, y=y)
    
    def get_position(self):
        """
        Return the current (x, y) position of the widget.
        
        :return: The (x, y) position of the widget.
        """
        return self.widget.winfo_x(), self.widget.winfo_y()

def print_red(text: str):
    print(f"\033[91m{text}\033[0m")

def print_yellow(text: str):
    print(f"\033[93m{text}\033[0m")

def print_green(text: str):
    print(f"\033[92m{text}\033[0m")

class ListLayout:
    def __init__(self, widgets: list) -> None:
        """
        Arranges widgets in a horizontal list.
        
        Attributes:
            widgets: The list of widgets to work with.
        """
        self.widgets = widgets
        for widget in self.widgets:
            if isinstance(widget, DraggableWidget):
                print_yellow(f"widget: {widget} is draggable it may ruin layout.")
            widget.pack(fill="x", expand=True, side="left", padx=9)

class VerticalListLayout:
    def __init__(self, widgets: list) -> None:
        """
        Stacks widgets vertically.
        Attributes:
            widgets: The list of widgets to work with.
        """
        
        self.widgets = widgets
        for widget in self.widgets:
            if isinstance(widget, DraggableWidget):
                print_yellow(f"widget: {widget} is draggable it may ruin layout.")
            widget.pack(fill="x", expand=True, side="top", pady=9)

class GridLayout:
    def __init__(self, widgets: list, columns: int = 3) -> None:
        """
        Arranges widgets in a grid layout just like a calculator.
        
        Attributes:
            widgets: The list of widgets to work with.
            columns: The number of columns.
        """
        self.widgets = widgets
        self.columns = columns
        self.column = 0
        self.row = 0
        for widget in self.widgets:
            if isinstance(widget, DraggableWidget):
                print_yellow(f"widget: {widget} is draggable it may ruin layout.")
            
            if self.column == self.columns:
                self.column = 0
                self.row += 1
            widget.grid(column=self.column, row=self.row, padx=9, pady=9)
            self.column += 1

class WeightedGridLayout:
    """
    Arranges widgets in a grid with configurable row and column weights.
    Extra space is distributed proportionally based on the weights.

    :param widgets: list of widgets to layout
    :param columns: number of columns in the grid
    :param row_weights: list of floats specifying weight for each row
    :param col_weights: list of floats specifying weight for each column
    """
    
    def __init__(self, widgets: list, columns: int = 3,
                 row_weights: list | None = None,
                 col_weights: list | None = None) -> None:
        
        self.widgets = widgets
        self.columns = columns
        self.row = 0
        self.column = 0
        
        # Determine number of rows
        num_rows = (len(widgets) + columns - 1) // columns
        
        # Fill in default weights if not provided
        self.row_weights = row_weights or [1.0] * num_rows
        self.col_weights = col_weights or [1.0] * columns
        
        for widget in self.widgets:
            if isinstance(widget, DraggableWidget):
                print_yellow(f"widget: {widget} is draggable it may ruin layout.")
            
            # Place widget in grid
            widget.grid(row=self.row, column=self.column, sticky="nsew", padx=2, pady=2)
            
            # Configure grid weights
            widget.master.grid_rowconfigure(self.row, weight=self.row_weights[self.row])
            widget.master.grid_columnconfigure(self.column, weight=self.col_weights[self.column])
            
            # Move to next cell
            self.column += 1
            if self.column >= self.columns:
                self.column = 0
                self.row += 1