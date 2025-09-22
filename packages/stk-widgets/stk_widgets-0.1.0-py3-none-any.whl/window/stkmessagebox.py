import customtkinter as ctk
from PIL import Image
from importlib import resources as res


class STkMessageBox(ctk.CTkToplevel):
    def __init__(self, parent=None, title="Message", message="",
                 option_1="OK", option_2=None, icon=None):
        super().__init__(parent)

        self.choice = None
        self.title(title)
        self.geometry("360x180")
        self.resizable(False, False)

        if parent:
            self.transient(parent)

        self.grab_set()  # Modal

        # Main frame
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Content frame
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(15, 20))

        # Icon
        if icon:
            icon_size = (64, 64)
            if isinstance(icon, str):
                img = ctk.CTkImage(dark_image=Image.open(icon), size=icon_size)
            elif isinstance(icon, Image.Image):
                img = ctk.CTkImage(dark_image=icon, size=icon_size)
            elif isinstance(icon, ctk.CTkImage):
                img = icon
            else:
                img = None
            if img:
                ctk.CTkLabel(content_frame, image=img, text="").pack(
                    side="left", padx=(0, 15), pady=5
                )

        # Message
        ctk.CTkLabel(
            content_frame, text=message, wraplength=260, justify="left"
        ).pack(side="left", expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(side="bottom", pady=10)

        b1 = ctk.CTkButton(
            button_frame, text=option_1,
            command=lambda: self._set_choice(option_1)
        )
        b1.pack(side="left", padx=5)

        if option_2:
            b2 = ctk.CTkButton(
                button_frame, text=option_2,
                command=lambda: self._set_choice(option_2)
            )
            b2.pack(side="left", padx=5)

    def _set_choice(self, choice):
        self.choice = choice
        self.destroy()



def get_icon(name: str) -> ctk.CTkImage | None:
    """Return a CTkImage icon for message boxes."""
    ICON_MAP = {
        "info": "info.png",
        "warning": "warning.png",
        "error": "error.png",
        "confirm": "question.png",
    }

    file_name = ICON_MAP.get(name.lower())
    if not file_name:
        return None

    try:
        with res.open_binary("stk_widgets.window.icons", file_name) as f:
            pil_icon = Image.open(f)
            pil_icon.load()
            return ctk.CTkImage(pil_icon, size=(64, 64))
    except Exception as e:
        print(f"Icon load failed: {e}")
        return None

        


# -------------------
# Drop-in functions
# -------------------
def showinfo(title="Info", message="", icon=None):
    icon = icon or get_icon("info")
    box = STkMessageBox(title=title, message=message, option_1="OK", icon=icon)
    box.wait_window()
    return box.choice


def showwarning(title="Warning", message="", icon=None):
    icon = icon or get_icon("warning")
    box = STkMessageBox(title=title, message=message, option_1="OK", icon=icon)
    box.wait_window()
    return box.choice


def showerror(title="Error", message="", icon=None):
    icon = icon or get_icon("error")
    box = STkMessageBox(title=title, message=message, option_1="OK", icon=icon)
    box.wait_window()
    return box.choice


def askyesno(title="Confirm", message="", icon=None):
    icon = icon or get_icon("confirm")
    box = STkMessageBox(title=title, message=message,
                        option_1="Yes", option_2="No", icon=icon)
    box.wait_window()
    return box.choice == "Yes"


#def askokcancel(title="Confirm", message="", icon=None):
#    box = STkMessageBox(title=title, message=message,
#                        option_1="OK", option_2="Cancel", icon=icon)
#    return box.choice == "OK"


#def askretrycancel(title="Retry", message="", icon=None):
#    box = STkMessageBox(title=title, message=message,
#                        option_1="Retry", option_2="Cancel", icon=icon)
#    return box.choice == "Retry"

#if __name__ == "__main__":
#    root = ctk.CTk()
#    root.geometry("400x200")
#
#
#    def test_messageboxes():
#        # Info box
#        result_info = showinfo(title="Information", message="This is an info message")
#        print("Info returned:", result_info)
#
#        # Warning box
#        result_warn = showwarning(title="Warning", message="This is a warning message")
#        print("Warning returned:", result_warn)
#
#        # Error box
#        result_error = showerror(title="Error", message="This is an error message")
#        print("Error returned:", result_error)
#
#        # Yes/No confirmation
#        result_yesno = askyesno(title="Confirm", message="Do you want to continue?")
#        print("Yes/No returned:", result_yesno)
#
#
#    # Button to trigger tests
#    btn = ctk.CTkButton(root, text="Test MessageBoxes", command=test_messageboxes)
#    btn.pack(pady=40)
#
#    root.mainloop()