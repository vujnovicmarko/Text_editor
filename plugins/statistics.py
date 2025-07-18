from __future__ import annotations
from typing import TYPE_CHECKING
from plugin import Plugin
from tkinter import messagebox

if TYPE_CHECKING:
    from text.text_editor_model import TextEditorModel
    from undo.undo_manager import UndoManager
    from clipboard.clipboard_stack import ClipboardStack


class Statistics(Plugin):
    def getName(self) -> str:
        return "Statistics"

    def getDescription(self) -> str:
        return "Plugin that displays the number of lines, words and characters in document."

    def execute(
        self,
        model: TextEditorModel,
        undoManager: UndoManager,
        clipboardStack: ClipboardStack,
    ) -> None:
        lines = model.getLines()
        words = [word for line in lines for word in line.split()]
        chars = [char for line in lines for char in line if not char.isspace()]

        message = (
            f"Lines: {len(lines)}\n"
            f"Words: {len(words)}\n"
            f"Characters: {len(chars)}"
        )

        messagebox.showinfo("Document Statistics", message)
