from __future__ import annotations
from typing import TYPE_CHECKING
from action.edit_action import EditAction
from location.location import Location

if TYPE_CHECKING:
    from text.text_editor_model import TextEditorModel


class DeleteAfterCharAction(EditAction):
    def __init__(self, tem: TextEditorModel, text: str, location: Location) -> None:
        self.tem: TextEditorModel = tem
        self.text: str = text
        self.location: Location = location

    def executeDo(self) -> None:
        self.tem.deleteAfter(Location(self.location.row, self.location.col))

    def executeUndo(self) -> None:
        self.tem._insert_char(self.text, self.location)
        self.tem.moveCursorLeft(None)
