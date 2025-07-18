from __future__ import annotations
from typing import TYPE_CHECKING
from plugin import Plugin
from action.compound_action import CompoundAction

if TYPE_CHECKING:
    from text.text_editor_model import TextEditorModel
    from undo.undo_manager import UndoManager
    from clipboard.clipboard_stack import ClipboardStack


class Capitalize(Plugin):
    def getName(self) -> str:
        return "Capitalize"

    def getDescription(self) -> str:
        return "Plugin that capitalizes all words in document."

    def execute(
        self,
        model: TextEditorModel,
        undoManager: UndoManager,
        clipboardStack: ClipboardStack,
    ) -> None:
        lines = model.getLines()
        capitalized_text = "\n".join([self.capitalizeLine(line) for line in lines])

        delete_action = model.clear()
        insert_action = model.insert(capitalized_text)

        if delete_action and insert_action:
            undoManager.push(CompoundAction([delete_action, insert_action]))
        else:
            undoManager.push(insert_action)

    def capitalizeLine(self, line: str) -> str:
        capitalizeNext = True
        result = []

        for char in line:
            if capitalizeNext and char.isalpha():
                result.append(char.upper())
                capitalizeNext = False

            else:
                result.append(char)

            if not char.isalpha():
                capitalizeNext = True

        return "".join(result)
