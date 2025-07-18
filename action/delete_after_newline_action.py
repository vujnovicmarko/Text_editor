from __future__ import annotations
from typing import TYPE_CHECKING
from action.edit_action import EditAction
from location.location import Location

if TYPE_CHECKING:
    from text.text_editor_model import TextEditorModel


class DeleteAfterNewlineAction(EditAction):
    def __init__(self, tem: TextEditorModel, location: Location) -> None:
        self.tem: TextEditorModel = tem
        self.location: Location = location

    def executeDo(self) -> None:
        self.tem.deleteAfter(Location(self.location.row, self.location.col))

    def executeUndo(self) -> None:
        self.tem._insert_newline(self.location)
        self.tem.moveCursorLeft(None)
