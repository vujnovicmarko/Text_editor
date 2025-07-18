from tkinter import Menu
from tkinter import Tk
from collections.abc import Callable


class MenuBar(Menu):
    def __init__(
        self,
        master: Tk,
    ) -> None:
        super().__init__(master)

        self.fileMenu: Menu = Menu(self, tearoff=0)
        self.fileMenu.add_command(label="Open")
        self.fileMenu.add_command(label="Save")
        self.fileMenu.add_command(label="Exit")
        self.add_cascade(label="File", menu=self.fileMenu)

        self.editMenu: Menu = Menu(self, tearoff=0)
        self.editMenu.add_command(label="Undo")
        self.editMenu.add_command(label="Redo")
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Cut")
        self.editMenu.add_command(label="Copy")
        self.editMenu.add_command(label="Paste")
        self.editMenu.add_command(label="Paste and Take")
        self.editMenu.add_command(label="Delete selection")
        self.editMenu.add_command(
            label="Clear document",
        )
        self.add_cascade(label="Edit", menu=self.editMenu)

        self.moveMenu: Menu = Menu(self, tearoff=0)
        self.moveMenu.add_command(label="Cursor to document start")
        self.moveMenu.add_command(label="Cursor to document end")
        self.add_cascade(label="Move", menu=self.moveMenu)

        self.pluginsMenu: Menu = Menu(self, tearoff=0)
        self.add_cascade(label="Plugins", menu=self.pluginsMenu)

    def setCommand(self, menu: str, label: str, command: Callable[[], None]) -> None:
        menu_obj = {
            "File": self.fileMenu,
            "Edit": self.editMenu,
            "Move": self.moveMenu,
        }[menu]

        index = menu_obj.index(label)

        assert isinstance(index, int)

        menu_obj.entryconfig(index, command=command)

    def enableCommand(self, menu: str, label: str) -> None:
        menu_obj = {
            "File": self.fileMenu,
            "Edit": self.editMenu,
            "Move": self.moveMenu,
        }[menu]

        index = menu_obj.index(label)

        assert isinstance(index, int)

        menu_obj.entryconfig(index, state="normal")

    def disableCommand(self, menu: str, label: str) -> None:
        menu_obj = {
            "File": self.fileMenu,
            "Edit": self.editMenu,
            "Move": self.moveMenu,
        }[menu]

        index = menu_obj.index(label)

        assert isinstance(index, int)

        menu_obj.entryconfig(index, state="disabled")
