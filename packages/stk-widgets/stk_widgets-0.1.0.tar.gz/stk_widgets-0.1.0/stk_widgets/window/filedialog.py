import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image
from importlib import resources as res
from . import stkmessagebox

# ---------------- Scrollable Frame ---------------- #



# ---------------- Path Tracker ---------------- #
class PathTracker:
    def __init__(self):
        self._current_path = Path.home()/"Desktop"

    def set_path(self, path):
        new_path = Path(path).resolve()
        if not new_path.exists() or not new_path.is_dir():
            raise ValueError(f"Invalid directory: {path}")
        self._current_path = new_path

    def get_path(self):
        return str(self._current_path)

    def change_path(self, child_dir):
        new_path = (self._current_path / child_dir).resolve()
        if not new_path.exists() or not new_path.is_dir():
            raise ValueError(f"Child directory does not exist: {child_dir}")
        if self._current_path not in new_path.parents and self._current_path != new_path.parent:
            raise ValueError(f"{child_dir} is not a child of {self._current_path}")
        self._current_path = new_path

    def open(self, file_name):
        file_path = self._current_path / file_name
        if not file_path.exists() or not file_path.is_file():
            raise ValueError(f"File does not exist: {file_name}")
        return str(file_path)

    def directory(self):
        try:
            return [item.name for item in self._current_path.iterdir()]
        except PermissionError:
            return [None]


def get_icons(name: str) -> ctk.CTkImage | None:
    # Fallback icons if resource package not found
    try:
        with res.open_binary("stk_widgets.window.icons", name) as image:
            pil_icon = Image.open(image)
            pil_icon.load()
            return ctk.CTkImage(pil_icon, size=(32, 32))
    except Exception:
        return None


# ---------------- Custom FileDialog ---------------- #
class StkFileDialog(ctk.CTkToplevel):
    FILE_TYPES = {
        "All": [],
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov"],
        "Audio": [".mp3", ".wav", ".ogg", ".m4a"],
        "Text": [".txt", ".md", ".csv", ".json"],
        "Code": [".c", ".cpp", ".js", ".java", ".html", ".css"],
        "Python": [".py"]
    }

    def __init__(self, parent=None, title:str="Select:", icons: dict[str,ctk.CTkImage] = None):
        """
        A custom file dialog implementation
        
        
        example usage:
            root = ctk.CTk()
            root.geometry("400x200")
            
            
            def open_dialog():
                dialog = StkFileDialog(root)
                root.wait_window(dialog)  # Wait until dialog is closed
                if dialog.result:  # File was chosen
                    print("Selected file:", dialog.result)
                else:
                    print("No file selected")
        
            btn = ctk.CTkButton(root, text="Open FileDialog", command=open_dialog)
            btn.pack(pady=40)
        
            root.mainloop()
        :param parent: parent window
        :param icons: dict of icon name to icon path format should be {
            "folder": get_icons("folder.png"),
            "file": get_icons("unknown.png"),
            "image": get_icons("image.png"),
            "video": get_icons("video.png"),
            "audio": get_icons("audio.png"),
            "text": get_icons("text.png"),
            "code": get_icons("code.png"),
            "python": get_icons("code.png"),
        }
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")
        try:
            ctk.get_appearance_mode()
        except:
            ctk.set_appearance_mode("light")

        if parent:
            self.transient(parent)
            self.attributes("-topmost", True)
            self.grab_set()  # Make modal
            #self.wait_window(parent)
        self.result = None
            
            # Path handling
        self.tracker = PathTracker()
        self.history = []
        self.last_clicked = None
        self.selected_item = None

        # Icon cache
        self.icon_cache = {}

        # Icons
        self.icons = icons or {
            "folder": get_icons("folder.png"),
            "file": get_icons("unknown.png"),
            "image": get_icons("image.png"),
            "video": get_icons("video.png"),
            "audio": get_icons("audio.png"),
            "text": get_icons("text.png"),
            "code": get_icons("code.png"),
            "python": get_icons("code.png"),
        }

        # --------- Layout --------- #
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        #"fg_color": ["#F3F4F6","#21262D"],
    #"hover_color": ["#E5E7EB","#30363D"]
        self.back_btn = ctk.CTkButton(nav_frame, text="⬅ Back", command=self.go_back, width=60,
                                      fg_color=("#F3F4F6","#21262D"), hover_color=("#E5E7EB","#30363D"))
        self.back_btn.pack(side="left", padx=2)

        self.up_btn = ctk.CTkButton(nav_frame, text="⬆ Up", command=self.go_up, width=60,
                                    fg_color=("#F3F4F6","#21262D"), hover_color=("#E5E7EB","#30363D"))
        self.up_btn.pack(side="left", padx=2)

        self.filter_var = ctk.StringVar(value="All")
        self.filter_menu = ctk.CTkOptionMenu(
            nav_frame, variable=self.filter_var,
            values=list(self.FILE_TYPES.keys()),
            command=lambda _: self.refresh_directory(),
            button_color=("#F3F4F6", "#21262D"),
            button_hover_color=("#E5E7EB", "#30363D"),
            fg_color=("#F3F4F6","#161B22"),
            text_color=("#1F2937","#E6EDF3")
        )
        self.filter_menu.pack(side="right")

        # Path breadcrumbs
        self.breadcrumb_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.breadcrumb_frame.pack(fill="x", padx=5, pady=5)

        # Quick access
        self.default_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.default_frame.pack(fill="x", padx=5, pady=5)

        # File grid (scrollable)
        self.file_frame = ctk.CTkScrollableFrame(self)
        self.file_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # storage for file buttons
        self.file_buttons = []

        # Add quick access
        self.add_quick_access()
        self.refresh_directory()

    # ----------------- Quick Access ----------------- #
    def add_quick_access(self):
        user_home = Path.home()
        common_dirs = {
            "Desktop": user_home / "Desktop",
            "Documents": user_home / "Documents",
            "Downloads": user_home / "Downloads",
            "Music": user_home / "Music",
            "Videos": user_home / "Videos",
        }
        for name, path in common_dirs.items():
            if path.exists():
                btn = ctk.CTkButton(
                    self.default_frame, text=name,
                    image=self.icons["folder"], compound="left",
                    command=lambda p=path: self.set_path(p),
                    fg_color=("#F3F4F6", "#21262D"), hover_color=("#E5E7EB", "#30363D")
                )
                btn.pack(side="left", padx=5, pady=5)

    # ----------------- File/Folder Handling ----------------- #
    # ----------------- File/Folder Handling ----------------- #
    def refresh_directory(self):
        self.update_breadcrumbs()
        
        file_filter = self.FILE_TYPES.get(self.filter_var.get(), [])
        items = [item for item in Path(self.tracker.get_path()).iterdir()
                 if not (file_filter and item.is_file() and item.suffix.lower() not in file_filter)]
        
        # hide all previous buttons
        for btn in self.file_buttons:
            btn.pack_forget()
        
        for i, item in enumerate(items):
            icon = self.get_icon(item)
            
            if i < len(self.file_buttons):
                btn = self.file_buttons[i]
                btn.configure(
                    text=item.name, image=icon,
                    command=lambda name=item.name: self.on_click(name),
                    fg_color=("#F3F4F6", "#21262D"), hover_color=("#E5E7EB", "#30363D")
                )
                btn.pack(fill="x", padx=5, pady=2)
            else:
                btn = ctk.CTkButton(
                    self.file_frame, text=item.name,
                    image=icon, compound="left",
                    height=40,
                    anchor="w",  # left-align text
                    command=lambda name=item.name: self.on_click(name),
                    fg_color=("#F3F4F6", "#21262D"), hover_color=("#E5E7EB", "#30363D")
                )
                btn.pack(fill="x", padx=5, pady=2)
                self.file_buttons.append(btn)
        
        # hide extras if there are fewer items
        for j in range(len(items), len(self.file_buttons)):
            self.file_buttons[j].pack_forget()
    
    def update_breadcrumbs(self):
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()

        parts = Path(self.tracker.get_path()).parts
        for i, part in enumerate(parts):
            btn = ctk.CTkButton(
                self.breadcrumb_frame, text=part,
                width=50,
                command=lambda p=Path(*parts[:i+1]): self.set_path(p),
                fg_color=("#F3F4F6", "#21262D"), hover_color=("#E5E7EB", "#30363D")
            )
            btn.pack(side="left", padx=2)
            if i < len(parts) - 1:
                ctk.CTkLabel(self.breadcrumb_frame, text=">").pack(side="left")

    def set_path(self, path):
        self.tracker.set_path(path)
        self.refresh_directory()

    # ----------------- Icon Handling (cached) ----------------- #
    def get_icon(self, path):
        if path.is_dir():
            return self.icons["folder"]

        ext = path.suffix.lower()
        if ext in self.icon_cache:
            return self.icon_cache[ext]

        if ext in self.FILE_TYPES["Images"]:
            icon = self.icons["image"]
        elif ext in self.FILE_TYPES["Videos"]:
            icon = self.icons["video"]
        elif ext in self.FILE_TYPES["Audio"]:
            icon = self.icons["audio"]
        elif ext in self.FILE_TYPES["Text"]:
            icon = self.icons["text"]
        elif ext in self.FILE_TYPES["Code"]:
            icon = self.icons["code"]
        elif ext in self.FILE_TYPES["Python"]:
            icon = self.icons["python"]
        else:
            icon = self.icons["file"]

        self.icon_cache[ext] = icon
        return icon

    # ----------------- Click Behavior ----------------- #
    def on_click(self, name):
        if self.last_clicked == name:  # second click → open/confirm
            new_path = Path(self.tracker.get_path()) / name
            if new_path.is_dir():
                self.history.append(self.tracker.get_path())
                self.tracker.change_path(name)
                self.refresh_directory()
            else:
                try:
                    file_path = self.tracker.open(name)
                    self.result = file_path
                    self.destroy()   # close dialog, return result
                except ValueError as e:
                    stkmessagebox.showerror("Error", message=str(e))
            self.last_clicked = None
        else:
            self.last_clicked = name
            self.selected_item = name

    # ----------------- Navigation ----------------- #
    def go_back(self):
        if self.history:
            last = self.history.pop()
            self.tracker.set_path(last)
            self.refresh_directory()

    def go_up(self):
        parent = Path(self.tracker.get_path()).parent
        if parent.exists() and parent.is_dir():
            self.history.append(self.tracker.get_path())
            self.tracker.set_path(parent)
            self.refresh_directory()


# ---------------- Example Usage ---------------- #
#if __name__ == "__main__":
#    root = ctk.CTk()
#    root.geometry("400x200")
#
#
#    def open_dialog():
#        dialog = StkFileDialog(root)
#        root.wait_window(dialog)  # Wait until dialog is closed
#        if dialog.result:  # File was chosen
#            print("Selected file:", dialog.result)
#        else:
#            print("No file selected")
#
#    btn = ctk.CTkButton(root, text="Open FileDialog", command=open_dialog)
#    btn.pack(pady=40)
#
#    root.mainloop()