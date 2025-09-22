# STkWidgets

A collection of custom Tkinter widgets that extend the standard toolkit with modern UI features.
Useful for building desktop apps with a cleaner and more functional interface.


---

## Installation

pip install .



---

## Example:

import customtkinter as ct
from stk_widgets import ToolTip, OptionList, PasswordEntry, Spinner, ArcSpinner, VerticalTab, ClickableLabel, \
    CircleButton,  stkmessagebox, StkFileDialog, layouts,STk, screenshot_frame

from stk_widgets.window.layouts import DraggableWidget

### STk is a rudimentary attempt at a custom window, it is very buggy so only use if you can fix or are okay with it
### It's preferable to use regular tk, ttk or ctk
root = STk()

root.set_title("Test Application")
root.geometry("500x500")

### Adds the default buttons for window control
root.add_default_winbtns()

entry = PasswordEntry(root.set_titlebar.right_container)

x =ct.CTkSegmentedButton(root.set_titlebar.right_container, values=["system", "light", "dark"], command=lambda e:   ct.set_appearance_mode(e))

#add widgets to title bar
root.add_widget_to_titlebar(entry)
root.add_widget_to_titlebar(x)

### Vertical tabview
tabview = VerticalTab(root, width=600, height=400)
tabview.pack(fill="both", expand=True)

button = ct.CTkButton(root, text="take screenshot",
                      command=lambda: screenshot_frame(root, "screenshots"))
button.pack()
ToolTip(button, "hey, I can take screenshots.")

### Add tabs
tab1 = tabview.add_tab("Home", button_style="circular")#button styles [circular, regular]
ct.CTkLabel(tab1, text="This is the Home tab").pack(pady=20)

tab2 = tabview.add_tab("Settings")
ct.CTkLabel(tab2, text="This is the Settings tab").pack(pady=20)

tab3 = tabview.add_tab("About")
ct.CTkLabel(tab3, text="This is the About tab").pack(pady=20)



frame = ct.CTkFrame(tab1)
frame.pack(padx=20, pady=20, fill="both", expand=True)

### Appears on left click and displays a group of options
options = OptionList(frame)
### Adds a label to the widget, also takes in a font argument
options.add_label("File Options")

#add buttons, buttons also take in argument like hover and color
options.add_button("Open", command=lambda: print("open clicked"))
options.add_button("Delete", color="red", command=lambda: print("delete clicked"))
options.add_button("Restore", command=lambda: print("restore clicked"))
lab = ct.CTkLabel(tab3)
lab.pack()

### A password entry with show and hide
p = PasswordEntry(tab3, password_hide_text="hide", password_show_text="show")
p.pack()

### A circular button
CircleButton(tab2, text="Click me", command=lambda: StkFileDialog(root, "just testing")).pack(pady=20)

#a clickable label, can be used for links or anything of the sort
ClickableLabel(tab3, text="This is the About tab",
               command=lambda :stkmessagebox.showinfo("Info", "This is a messagebox")).pack(pady=20)

### Loading animations
Spinner(root).pack(pady=20, expand=True, fill="both")
ArcSpinner(root).pack(pady=20, expand=True, fill="both")

btn = ct.CTkButton(tab3, text="testing layout and drag")
btn2 = ct.CTkButton(tab3,text="testing layout")
btn3 = ct.CTkButton(tab3, text="testing layout")

### Arranges widgets in a list, other layouts include:
#layouts.WeightedGridLayout
#layouts.VerticalListLayout
#layouts.GridLayout
layouts.ListLayout([btn, btn2, btn3])

### Makes widgets draggable
DraggableWidget(
    btn,
    constrain_to_parent=False #detemines if the widget should be constrained to its parent/master
)



root.mainloop()


---

## Available Widgets

CirularButton → a completely circular button

PasswordEntry → Entry widget with show and hide functionality

ClickableLabel → A label that can be clicked, useful for links

Spinner & ArcSpinner → loading animations

Tooltip → a tooltip that appears on hover

OptionList → appears on left-click and displays options

TyperWriterEffect → not a widget but simulates typewiter effect on given widget

VerticalTab → like ctktabview but vertical

stkmessagebox → a themed messagebox

STkMenuBar → a custom themed implementation of the menubar

STkFileDialog → a custom filedialog implementation

---

## Requirements

Python 3.8+

Tkinter

CustomTkinter

Pillow

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE] file for details


---
