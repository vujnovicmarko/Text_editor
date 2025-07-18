from __future__ import annotations
from typing import TYPE_CHECKING
from action.edit_action import EditAction

if TYPE_CHECKING:
    from location.location import Location
    from text.text_editor_model import TextEditorModel


class InsertNewlineAction(EditAction):
    def __init__(self, tem: TextEditorModel, location: Location) -> None:
        self.tem: TextEditorModel = tem
        self.location: Location = location

    def executeDo(self) -> None:
        self.tem._insert_newline(self.location)

    def executeUndo(self) -> None:
        self.tem._undo_insert_newline(self.location)
