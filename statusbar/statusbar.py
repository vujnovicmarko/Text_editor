from tkinter import Frame, Label, Tk


class Statusbar(Frame):
    def __init__(
        self,
        master: Tk,
    ) -> None:
        super().__init__(master)

        self.cursorLabel: Label = Label(self)
        self.cursorLabel.pack(side="right", fill="x")

        self.linesLabel: Label = Label(self)
        self.linesLabel.pack(side="right", fill="x")

    def setCursorLabel(self, row: str, col: str) -> None:
        self.cursorLabel.config(text=f"Cursor Location:[{row}:{col}]")

    def setLinesLabel(self, currLine: str, allLines: str) -> None:
        self.linesLabel.config(text=f"Lines:[{currLine}/{allLines}]")
