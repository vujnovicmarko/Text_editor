from __future__ import annotations
from typing import TYPE_CHECKING
from tkinter import Canvas, filedialog, messagebox
from cursor.cursor_observer import CursorObserver
from text.text_observer import TextObserver
from text.select_observer import SelectObserver
from location.location import Location
from location.location_range import LocationRange
from clipboard.clipboard_observer import ClipboardObserver
from undo.undo_observer import UndoObserver
from undo.redo_observer import RedoObserver

if TYPE_CHECKING:
    from text.text_editor_model import TextEditorModel
    from clipboard.clipboard_stack import ClipboardStack
    from undo.undo_manager import UndoManager
    from menu.menu_bar import MenuBar
    from toolbar.toolbar import Toolbar
    from statusbar.statusbar import Statusbar
    from tkinter import Tk
    from plugin import Plugin

SELECT_COLOR: str = "#257AFD"


class TextEditor(
    Canvas,
    CursorObserver,
    TextObserver,
    ClipboardObserver,
    UndoObserver,
    RedoObserver,
    SelectObserver,
):
    def __init__(
        self,
        master: Tk,
        textEditorModel: TextEditorModel,
        clipboardStack: ClipboardStack,
        undoManager: UndoManager,
        menuBar: MenuBar,
        toolbar: Toolbar,
        statusbar: Statusbar,
    ) -> None:
        super().__init__(master)
        self.master = master

        self.menuBar: MenuBar = menuBar
        self.master.config(menu=self.menuBar)

        self.toolbar: Toolbar = toolbar
        self.toolbar.pack(side="top", fill="x")

        self.statusbar: Statusbar = statusbar
        self.statusbar.pack(side="bottom", fill="x")

        self.textEditorModel: TextEditorModel = textEditorModel
        self.textEditorModel.addCursorObserver(self)
        self.textEditorModel.addTextObserver(self)
        self.textEditorModel.addSelectObserver(self)

        self.clipboardStack: ClipboardStack = clipboardStack
        self.clipboardStack.addClipboardObserver(self)

        self.undoManager: UndoManager = undoManager
        self.undoManager.addUndoObserver(self)
        self.undoManager.addRedoObserver(self)

        self.cursor_id: int = 0
        self.line_ids: list[int | list[int]] = []

        self._setBinds()
        self._setMenuCommands()
        self._setToolbarCommands()

        self.drawText()
        self.updateCursorLocation(self.textEditorModel.getCursorLocation())
        self.textEditorModel.notifySelectObservers()
        self.clipboardStack.notifyClipboardObservers()
        self.undoManager.notifyUndoObservers()
        self.undoManager.notifyRedoObservers()

        self.pack(fill="both", expand=True)
        self.config(background="white")
        self.focus_set()

    def drawText(self) -> None:
        tem = self.textEditorModel

        for i in range(len(self.line_ids)):
            self._deleteLine(i)
        self.line_ids = []

        for i, line in enumerate(tem.allLines()):
            line_id = self.create_text(
                5, 5 + i * 20, text=line, anchor="nw", font=("Arial", 16)
            )
            self.line_ids.append(line_id)

        sr = tem.getSelectionRange()

        if sr:
            self._drawSelect(sr, tem)

    def _drawSelect(self, sr: LocationRange, tem: TextEditorModel) -> None:
        s_row, s_col, e_row, e_col = sr.getCoords()

        if s_row == e_row:
            line = tem.lines[s_row]
            self._editLine(line, s_row, s_col, e_col)

        else:
            line = tem.lines[s_row]
            self._editLine(line, s_row, s_col, len(line))

            for i, line in enumerate(tem.linesRange(s_row + 1, e_row)):
                self._editLine(line, s_row + 1 + i, 0, len(line))

            line = tem.lines[e_row]
            self._editLine(line, e_row, 0, e_col)

    def _editLine(self, line: str, row: int, s_col: int, e_col: int) -> None:
        self._deleteLine(row)
        self.line_ids.pop(row)
        self._drawSelectLine(line, row, s_col, e_col)

    def _deleteLine(self, index: int) -> None:
        line_id = self.line_ids[index]
        if isinstance(line_id, list):
            for id in line_id:
                self.delete(id)
        else:
            self.delete(line_id)

    def _drawSelectLine(self, line: str, row: int, s_col: int, e_col: int) -> None:
        before = line[:s_col]
        selected = line[s_col:e_col]
        after = line[e_col:]
        y = 5 + row * 20
        new_ids = []

        line_id = self.create_text(5, y, text=before, anchor="nw", font=("Arial", 16))
        new_ids.append(line_id)

        bbox = self.bbox(line_id)
        x = bbox[2]

        temp_id = self.create_text(
            x, y, text=selected, anchor="nw", font=("Arial", 16), fill="white"
        )
        bbox = self.bbox(temp_id)
        self.delete(temp_id)

        rect_id = self.create_rectangle(bbox, fill=SELECT_COLOR, width=0)
        new_ids.append(rect_id)

        line_id = self.create_text(
            x, y, text=selected, anchor="nw", font=("Arial", 16), fill="white"
        )
        new_ids.append(line_id)

        x = bbox[2]

        line_id = self.create_text(x, y, text=after, anchor="nw", font=("Arial", 16))
        new_ids.append(line_id)

        self.line_ids.insert(row, new_ids)

    def updateCursorLocation(self, loc: Location) -> None:
        if self.cursor_id:
            self.delete(self.cursor_id)

        line = self.textEditorModel.lines[loc.row]
        text_before_cursor = line[: loc.col]

        temp_id = self.create_text(
            5, 5, text=text_before_cursor, anchor="nw", font=("Arial", 16)
        )

        bbox = self.bbox(temp_id)
        self.delete(temp_id)

        cursor_x = bbox[2]
        cursor_y = 5 + loc.row * 20

        self.cursor_id = self.create_line(
            cursor_x, cursor_y, cursor_x, cursor_y + 20, fill="black", width=2
        )

        self.statusbar.setCursorLabel(str(loc.row + 1), str(loc.col + 1))
        lines = self.textEditorModel.getLines()
        self.statusbar.setLinesLabel(str(loc.row + 1), str(len(lines)))

    def updateText(self) -> None:
        self.drawText()

    def updateClipboard(self, isEmpty: bool) -> None:
        if isEmpty:
            self.menuBar.disableCommand("Edit", "Paste")
            self.menuBar.disableCommand("Edit", "Paste and Take")
            self.toolbar.disableCommand("paste")
        else:
            self.menuBar.enableCommand("Edit", "Paste")
            self.menuBar.enableCommand("Edit", "Paste and Take")
            self.toolbar.enableCommand("paste")

    def updateUndoStack(self, isEmpty: bool) -> None:
        if isEmpty:
            self.menuBar.disableCommand("Edit", "Undo")
            self.toolbar.disableCommand("undo")
        else:
            self.menuBar.enableCommand("Edit", "Undo")
            self.toolbar.enableCommand("undo")

    def updateRedoStack(self, isEmpty: bool) -> None:
        if isEmpty:
            self.menuBar.disableCommand("Edit", "Redo")
            self.toolbar.disableCommand("redo")
        else:
            self.menuBar.enableCommand("Edit", "Redo")
            self.toolbar.enableCommand("redo")

    def updateSelect(self, isSelected: bool) -> None:
        if isSelected:
            self.menuBar.enableCommand("Edit", "Cut")
            self.menuBar.enableCommand("Edit", "Copy")
            self.menuBar.enableCommand("Edit", "Delete selection")
            self.toolbar.enableCommand("cut")
            self.toolbar.enableCommand("copy")
        else:
            self.menuBar.disableCommand("Edit", "Cut")
            self.menuBar.disableCommand("Edit", "Copy")
            self.menuBar.disableCommand("Edit", "Delete selection")
            self.toolbar.disableCommand("cut")
            self.toolbar.disableCommand("copy")

    def _setBinds(self) -> None:
        self.bind("<Left>", self.textEditorModel.moveCursorLeft)
        self.bind("<Right>", self.textEditorModel.moveCursorRight)
        self.bind("<Up>", self.textEditorModel.moveCursorUp)
        self.bind("<Down>", self.textEditorModel.moveCursorDown)

        self.bind(
            "<BackSpace>",
            lambda event: self.undoManager.push(self.textEditorModel.deleteBefore()),
        )
        self.bind(
            "<Delete>",
            lambda event: self.undoManager.push(self.textEditorModel.deleteAfter()),
        )

        self.bind("<Shift-Left>", self.textEditorModel.selectLeft)
        self.bind("<Shift-Right>", self.textEditorModel.selectRight)
        self.bind("<Shift-Up>", self.textEditorModel.selectUp)
        self.bind("<Shift-Down>", self.textEditorModel.selectDown)

        self.bind(
            "<Control-c>",
            lambda event: self.textEditorModel.copy(event, self.clipboardStack),
        )
        self.bind(
            "<Control-x>",
            lambda event: self.undoManager.push(
                self.textEditorModel.cut(event, self.clipboardStack)
            ),
        )
        self.bind(
            "<Control-v>",
            lambda event: self.undoManager.push(
                self.textEditorModel.paste(self.clipboardStack)
            ),
        )
        self.bind(
            "<Control-Shift-V>",
            lambda event: self.undoManager.push(
                self.textEditorModel.pasteAndTake(self.clipboardStack)
            ),
        )

        self.bind(
            "<Key>",
            lambda event: self.undoManager.push(self.textEditorModel.keyPress(event)),
        )

        self.bind("<Control-z>", self.undoManager.undo)
        self.bind("<Control-y>", self.undoManager.redo)

    def openFile(self) -> None:
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.undoManager.undoStack = []
                self.undoManager.redoStack = []

                self.undoManager.notifyUndoObservers()
                self.undoManager.notifyRedoObservers()

                content = file.read().splitlines()
                self.textEditorModel.setLines(content)

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def saveFile(self) -> None:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(self.textEditorModel.getLines()))

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def _setMenuCommands(self) -> None:
        self.menuBar.setCommand("File", "Open", self.openFile)
        self.menuBar.setCommand("File", "Save", self.saveFile)
        self.menuBar.setCommand("File", "Exit", self.master.quit)
        self.menuBar.setCommand("Edit", "Undo", lambda: self.undoManager.undo(None))
        self.menuBar.setCommand("Edit", "Redo", lambda: self.undoManager.redo(None))
        self.menuBar.setCommand(
            "Edit",
            "Cut",
            lambda: self.undoManager.push(
                self.textEditorModel.cut(None, self.clipboardStack)
            ),
        )
        self.menuBar.setCommand(
            "Edit", "Copy", lambda: self.textEditorModel.copy(None, self.clipboardStack)
        )
        self.menuBar.setCommand(
            "Edit",
            "Paste",
            lambda: self.undoManager.push(
                self.textEditorModel.paste(self.clipboardStack)
            ),
        )
        self.menuBar.setCommand(
            "Edit",
            "Paste and Take",
            lambda: self.undoManager.push(
                self.textEditorModel.pasteAndTake(self.clipboardStack)
            ),
        )
        self.menuBar.setCommand(
            "Edit",
            "Delete selection",
            lambda: self.undoManager.push(self.textEditorModel.deleteBefore()),
        )
        self.menuBar.setCommand(
            "Edit",
            "Clear document",
            lambda: self.undoManager.push(self.textEditorModel.clear()),
        )
        self.menuBar.setCommand(
            "Move",
            "Cursor to document start",
            self.textEditorModel.moveCursorStart,
        )
        self.menuBar.setCommand(
            "Move", "Cursor to document end", self.textEditorModel.moveCursorEnd
        )

    def setPlugins(self, plugins: list[Plugin]) -> None:
        for plugin in plugins:
            self.menuBar.pluginsMenu.add_command(
                label=plugin.getName(),
                command=lambda p=plugin: p.execute(
                    self.textEditorModel, self.undoManager, self.clipboardStack
                ),
            )

    def _setToolbarCommands(self) -> None:
        self.toolbar.setCommand("undo", lambda: self.undoManager.undo(None))
        self.toolbar.setCommand("redo", lambda: self.undoManager.redo(None))
        self.toolbar.setCommand(
            "cut",
            lambda: self.undoManager.push(
                self.textEditorModel.cut(None, self.clipboardStack)
            ),
        )
        self.toolbar.setCommand(
            "copy", lambda: self.textEditorModel.copy(None, self.clipboardStack)
        )
        self.toolbar.setCommand(
            "paste",
            lambda: self.undoManager.push(
                self.textEditorModel.paste(self.clipboardStack)
            ),
        )
