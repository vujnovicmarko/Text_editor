from __future__ import annotations
from typing import TYPE_CHECKING
from action.edit_action import EditAction

if TYPE_CHECKING:
    from location.location import Location
    from location.location_range import LocationRange
    from text.text_editor_model import TextEditorModel


class DeleteRangeAction(EditAction):
    def __init__(
        self,
        tem: TextEditorModel,
        text: str,
        locationRange: LocationRange,
        cursorLoaciton: Location,
    ) -> None:
        self.tem: TextEditorModel = tem
        self.text: str = text
        self.locationRange: LocationRange = locationRange
        self.cursorLoaciton: Location = cursorLoaciton

    def executeDo(self) -> None:
        self.tem.deleteRange(self.locationRange)

    def executeUndo(self) -> None:
        self.tem._undo_delete_range(self.text, self.locationRange, self.cursorLoaciton)
