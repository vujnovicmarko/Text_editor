from tkinter import Frame, Button, PhotoImage, Tk
from collections.abc import Callable


class Toolbar(Frame):
    def __init__(
        self,
        master: Tk,
    ) -> None:
        super().__init__(master)

        self.undoIcon: PhotoImage = PhotoImage(file="icons/undo.png")
        self.redoIcon: PhotoImage = PhotoImage(file="icons/redo.png")
        self.cutIcon: PhotoImage = PhotoImage(file="icons/cut.png")
        self.copyIcon: PhotoImage = PhotoImage(file="icons/copy.png")
        self.pasteIcon: PhotoImage = PhotoImage(file="icons/paste.png")

        self.buttons: dict[str, Button] = {
            "undo": Button(self, image=self.undoIcon),
            "redo": Button(self, image=self.redoIcon),
            "cut": Button(self, image=self.cutIcon),
            "copy": Button(self, image=self.copyIcon),
            "paste": Button(self, image=self.pasteIcon),
        }

        for btn in self.buttons.values():
            btn.pack(side="left")

    def setCommand(self, name: str, command: Callable[[], None]) -> None:
        if name in self.buttons:
            self.buttons[name].config(command=command)

    def enableCommand(self, name: str) -> None:
        if name in self.buttons:
            self.buttons[name].config(state="normal")

    def disableCommand(self, name: str) -> None:
        if name in self.buttons:
            self.buttons[name].config(state="disabled")
