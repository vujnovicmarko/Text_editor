from __future__ import annotations
from typing import TYPE_CHECKING
from location.location import Location
from location.location_range import LocationRange
from action.insert_char_action import InsertCharAction
from action.insert_multiline_action import InsertMultilineAction
from action.insert_newline_action import InsertNewlineAction
from action.delete_before_char_action import DeleteBeforeCharAction
from action.delete_after_char_action import DeleteAfterCharAction
from action.delete_before_newline_action import DeleteBeforeNewlineAction
from action.delete_after_newline_action import DeleteAfterNewlineAction
from action.delete_range_action import DeleteRangeAction
from action.compound_action import CompoundAction
from tkinter import Event

if TYPE_CHECKING:
    from cursor.cursor_observer import CursorObserver
    from collections.abc import Iterator
    from text.text_observer import TextObserver
    from action.edit_action import EditAction
    from clipboard.clipboard_stack import ClipboardStack
    from text.select_observer import SelectObserver


class TextEditorModel:
    def __init__(self, text: str) -> None:
        self.lines: list[str] = text.split("\n")
        self.selectionRange: LocationRange | None = None
        self.cursorLocation: Location = Location()

        self.cursorObservers: list[CursorObserver] = []
        self.textObservers: list[TextObserver] = []
        self.selectObservers: list[SelectObserver] = []

    def allLines(self) -> Iterator[str]:
        for line in self.lines:
            yield line

    def linesRange(self, index1: int, index2: int) -> Iterator[str]:
        for line in self.lines[index1:index2]:
            yield line

    def addCursorObserver(self, cursorObserver: CursorObserver) -> None:
        self.cursorObservers.append(cursorObserver)

    def removeCursorObserver(self, cursorObserver: CursorObserver) -> None:
        self.cursorObservers.remove(cursorObserver)

    def notifyCursorObservers(self) -> None:
        for cursorObserver in self.cursorObservers:
            cursorObserver.updateCursorLocation(self.cursorLocation)

    def addTextObserver(self, textObserver: TextObserver) -> None:
        self.textObservers.append(textObserver)

    def removeTextObserver(self, textObserver: TextObserver) -> None:
        self.textObservers.remove(textObserver)

    def notifyTextObservers(self) -> None:
        for textObserver in self.textObservers:
            textObserver.updateText()

    def addSelectObserver(self, selectObserver: SelectObserver) -> None:
        self.selectObservers.append(selectObserver)

    def removeSelectObserver(self, selectObserver: SelectObserver) -> None:
        self.selectObservers.remove(selectObserver)

    def notifySelectObservers(self) -> None:
        for selectObserver in self.selectObservers:
            selectObserver.updateSelect(self.selectionRange is not None)

    def moveCursorLeft(self, event: Event | None) -> None:
        if event:
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifySelectObservers()

        if self.cursorLocation.col > 0:
            self.cursorLocation.col -= 1
            self.notifyCursorObservers()

        elif self.cursorLocation.row > 0:
            self.cursorLocation.row -= 1
            self.cursorLocation.col = len(self.lines[self.cursorLocation.row])
            self.notifyCursorObservers()

    def moveCursorRight(self, event: Event | None) -> None:
        if event:
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifySelectObservers()

        if self.cursorLocation.col < len(self.lines[self.cursorLocation.row]):
            self.cursorLocation.col += 1
            self.notifyCursorObservers()

        elif self.cursorLocation.row < len(self.lines) - 1:
            self.cursorLocation.row += 1
            self.cursorLocation.col = 0
            self.notifyCursorObservers()

    def moveCursorUp(self, event: Event | None) -> None:
        if event:
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifySelectObservers()

        if self.cursorLocation.row > 0:
            self.cursorLocation.row -= 1
            self.cursorLocation.col = min(
                len(self.lines[self.cursorLocation.row]), self.cursorLocation.col
            )
            self.notifyCursorObservers()

    def moveCursorDown(self, event: Event | None) -> None:
        if event:
            self.selectionRange = None
            self.notifyTextObservers()
            self.notifySelectObservers()

        if self.cursorLocation.row < len(self.lines) - 1:
            self.cursorLocation.row += 1
            self.cursorLocation.col = min(
                len(self.lines[self.cursorLocation.row]), self.cursorLocation.col
            )
            self.notifyCursorObservers()

    def deleteBefore(self, location: Location | None = None) -> EditAction | None:
        if self.selectionRange:
            return self.deleteRange(self.selectionRange)

        else:
            if location is None:
                location = Location(self.cursorLocation.row, self.cursorLocation.col)
            else:
                self.cursorLocation = location
                self.moveCursorRight(None)

            row, col = location.getCoords()
            line = self.lines[row]

            if col > 0:
                deleted_text = line[col - 1]

                line = line[: col - 1] + line[col:]
                self.lines[row] = line

                self.moveCursorLeft(None)

                self.notifyTextObservers()

                location = Location(self.cursorLocation.row, self.cursorLocation.col)

                return DeleteBeforeCharAction(self, deleted_text, location)

            elif row > 0:
                self.moveCursorLeft(None)

                prev_line = self.lines[row - 1]
                new_line = prev_line + line
                self.lines[row - 1] = new_line
                self.lines.pop(row)

                self.notifyTextObservers()

                location = Location(self.cursorLocation.row, self.cursorLocation.col)

                return DeleteBeforeNewlineAction(self, location)

    def deleteAfter(self, location: Location | None = None) -> EditAction | None:
        if self.selectionRange:
            return self.deleteRange(self.selectionRange)

        else:
            if location is None:
                location = Location(self.cursorLocation.row, self.cursorLocation.col)
            else:
                self.cursorLocation = location
                self.notifyCursorObservers()

            row, col = location.getCoords()
            line = self.lines[row]

            if col < len(line):
                deleted_text = line[col]

                line = line[:col] + line[col + 1 :]
                self.lines[row] = line

                self.notifyTextObservers()

                return DeleteAfterCharAction(self, deleted_text, location)

            elif row < len(self.lines) - 1:
                next_line = self.lines[row + 1]
                line += next_line
                self.lines[row] = line
                self.lines.pop(row + 1)

                self.notifyTextObservers()

                return DeleteAfterNewlineAction(self, location)

    def deleteRange(self, locationRange: LocationRange) -> EditAction:
        s_row, s_col, e_row, e_col = locationRange.getCoords()
        cursor_location = Location(self.cursorLocation.row, self.cursorLocation.col)

        if s_row == e_row:
            line = self.lines[s_row]
            deleted_text = line[s_col:e_col]
            line = line[:s_col] + line[e_col:]
            self.lines[s_row] = line

        else:
            s_line = self.lines[s_row]
            e_line = self.lines[e_row]
            line = s_line[:s_col] + e_line[e_col:]
            self.lines[s_row] = line

            deleted_text = [s_line[s_col:]]

            for i in range(s_row + 1, e_row):
                deleted_text.append(self.lines[i])

            deleted_text.append(e_line[:e_col])

            deleted_text = "\n".join(deleted_text)

            for _ in range(s_row, e_row):
                self.lines.pop(s_row + 1)

        self.cursorLocation = Location(s_row, s_col)
        self.selectionRange = None
        self.notifySelectObservers()
        self.notifyCursorObservers()
        self.notifyTextObservers()

        return DeleteRangeAction(self, deleted_text, locationRange, cursor_location)

    def _undo_delete_range(
        self, text: str, locationRange: LocationRange, cursorLocation: Location
    ) -> None:
        s_row, s_col, e_row, e_col = locationRange.getCoords()
        if "\n" in text:
            self._insert_multiline(text, Location(s_row, s_col))
        else:
            self._insert_char(text, Location(s_row, s_col))

        self.cursorLocation = Location(cursorLocation.row, cursorLocation.col)
        self.selectionRange = locationRange

        self.notifySelectObservers()
        self.notifyTextObservers()
        self.notifyCursorObservers()

    def selectLeft(self, event: Event | None) -> None:
        sr = self.selectionRange
        if sr:
            self.moveCursorLeft(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if sr.start == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(sr.start, Location(e_row, e_col))
            self.notifySelectObservers()
            self.notifyTextObservers()

        else:
            s_row, s_col = self.cursorLocation.getCoords()

            self.moveCursorLeft(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if Location(s_row, s_col) == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(
                    Location(s_row, s_col), Location(e_row, e_col)
                )
            self.notifySelectObservers()
            self.notifyTextObservers()

    def selectRight(self, event: Event | None) -> None:
        sr = self.selectionRange
        if sr:
            self.moveCursorRight(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if sr.start == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(sr.start, Location(e_row, e_col))
            self.notifySelectObservers()
            self.notifyTextObservers()

        else:
            s_row, s_col = self.cursorLocation.getCoords()

            self.moveCursorRight(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if Location(s_row, s_col) == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(
                    Location(s_row, s_col), Location(e_row, e_col)
                )
            self.notifySelectObservers()
            self.notifyTextObservers()

    def selectUp(self, event: Event | None) -> None:
        sr = self.selectionRange
        if sr:
            self.moveCursorUp(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if sr.start == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(sr.start, Location(e_row, e_col))
            self.notifySelectObservers()
            self.notifyTextObservers()

        else:
            s_row, s_col = self.cursorLocation.getCoords()

            self.moveCursorUp(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if Location(s_row, s_col) == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(
                    Location(s_row, s_col), Location(e_row, e_col)
                )
            self.notifySelectObservers()
            self.notifyTextObservers()

    def selectDown(self, event: Event | None) -> None:
        sr = self.selectionRange
        if sr:
            self.moveCursorDown(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if sr.start == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(sr.start, Location(e_row, e_col))
            self.notifySelectObservers()
            self.notifyTextObservers()

        else:
            s_row, s_col = self.cursorLocation.getCoords()

            self.moveCursorDown(None)
            e_row, e_col = self.cursorLocation.getCoords()
            if Location(s_row, s_col) == Location(e_row, e_col):
                self.selectionRange = None
            else:
                self.selectionRange = LocationRange(
                    Location(s_row, s_col), Location(e_row, e_col)
                )
            self.notifySelectObservers()
            self.notifyTextObservers()

    def keyPress(self, event: Event) -> EditAction | None:
        return self.insert(event.char)

    def insert(self, text) -> EditAction | None:
        delete_action, insert_action = None, None
        chars = text[:].replace("\n", "")

        if text == "\r":
            if self.selectionRange:
                delete_action = self.deleteRange(self.selectionRange)

            location = self.cursorLocation

            self._insert_newline(self.cursorLocation)

            insert_action = InsertNewlineAction(self, location)

        elif text != "" and chars.isprintable():
            if self.selectionRange:
                delete_action = self.deleteRange(self.selectionRange)

            location = self.cursorLocation

            if "\n" not in text:
                self._insert_char(text, self.cursorLocation)

                insert_action = InsertCharAction(self, text, location)

            else:
                self._insert_multiline(text, self.cursorLocation)

                insert_action = InsertMultilineAction(self, text, location)

        if not insert_action:
            return

        if delete_action:
            return CompoundAction([delete_action, insert_action])
        else:
            return insert_action

    def _insert_char(self, text: str, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()
        line = self.lines[row]

        line = line[:col] + text + line[col:]
        self.lines[row] = line

        self.cursorLocation = Location(row, col + len(text))

        self.notifyTextObservers()
        self.notifyCursorObservers()

    def _undo_insert_char(self, text: str, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()
        line = self.lines[row]

        line = line[:col] + line[col + len(text) :]
        self.lines[row] = line

        self.cursorLocation = Location(row, col)

        self.notifyTextObservers()
        self.notifyCursorObservers()

    def _insert_newline(self, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()

        line = self.lines[row]
        line_1 = line[:col]
        line_2 = line[col:]

        self.lines[row] = line_1
        self.lines.insert(row + 1, line_2)

        self.cursorLocation = Location(row + 1, 0)

        self.notifyCursorObservers()
        self.notifyTextObservers()

    def _undo_insert_newline(self, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()

        line_1 = self.lines[row]
        line_2 = self.lines[row + 1]
        line = line_1 + line_2

        self.lines[row] = line
        self.lines.pop(row + 1)

        self.cursorLocation = location

        self.notifyCursorObservers()
        self.notifyTextObservers()

    def _insert_multiline(self, text: str, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()
        line = self.lines[row]

        pre_insert, post_insert = line[:col], line[col:]
        n = text.count("\n")
        lines = text.split("\n")
        col = len(lines[-1])
        lines[0], lines[-1] = pre_insert + lines[0], lines[-1] + post_insert

        lines.reverse()
        self.lines.pop(row)

        for line in lines:
            self.lines.insert(row, line)

        self.cursorLocation = Location(row + n, col)

        self.notifyTextObservers()
        self.notifyCursorObservers()

    def _undo_insert_multiline(self, text: str, location: Location) -> None:
        if self.selectionRange:
            self.selectionRange = None
            self.notifySelectObservers()

        row, col = location.getCoords()
        line = self.lines[row]
        pre_insert = line[:col]

        n = text.count("\n")
        lines = text.split("\n")
        col = len(lines[-1])
        line = self.lines[row + n]
        post_insert = line[col:]

        self.lines[row] = pre_insert + post_insert

        for _ in range(n):
            self.lines.pop(row + 1)

        self.cursorLocation = Location(row, col)

        self.notifyTextObservers()
        self.notifyCursorObservers()

    def copy(self, event: Event | None, clipboardStack) -> None:
        sr = self.selectionRange

        if sr:
            s_row, s_col, e_row, e_col = sr.getCoords()

            if s_row == e_row:
                line = self.lines[s_row]
                selected = line[s_col:e_col]
                clipboardStack.push(selected)

            else:
                s_line = self.lines[s_row][s_col:]
                lines = [line for line in self.linesRange(s_row + 1, e_row)]
                e_line = self.lines[e_row][:e_col]

                lines.insert(0, s_line)
                lines.append(e_line)

                clipboardStack.push("\n".join(lines))

    def cut(self, event: Event | None, clipboardStack) -> EditAction | None:
        sr = self.selectionRange

        if sr:
            s_row, s_col, e_row, e_col = sr.getCoords()

            if s_row == e_row:
                line = self.lines[s_row]
                selected = line[s_col:e_col]
                clipboardStack.push(selected)
                return self.deleteRange(sr)

            else:
                s_line = self.lines[s_row][s_col:]
                lines = [line for line in self.linesRange(s_row + 1, e_row)]
                e_line = self.lines[e_row][:e_col]

                lines.insert(0, s_line)
                lines.append(e_line)

                clipboardStack.push("\n".join(lines))
                return self.deleteRange(sr)

    def paste(self, clipboardStack: ClipboardStack) -> EditAction | None:
        try:
            text = clipboardStack.peek()
        except IndexError as e:
            print(e)
            return

        return self.insert(text)

    def pasteAndTake(self, clipboardStack: ClipboardStack) -> EditAction | None:
        try:
            text = clipboardStack.pop()
        except IndexError as e:
            print(e)
            return

        return self.insert(text)

    def getLines(self) -> list[str]:
        return self.lines

    def setLines(self, lines: list[str]) -> None:
        self.moveCursorStart()

        self.lines = [""] if not lines else lines
        self.notifyTextObservers()

    def getSelectionRange(self) -> LocationRange | None:
        return self.selectionRange

    def setSelectionRange(self, locationRange: LocationRange) -> None:
        self.selectionRange = locationRange
        self.notifySelectObservers()
        self.notifyTextObservers()

    def getCursorLocation(self) -> Location:
        return self.cursorLocation

    def setCursorLocation(self, location: Location) -> None:
        self.cursorLocation = location
        self.notifyCursorObservers()

    def clear(self) -> EditAction | None:
        if Location(0, 0) != Location(len(self.lines) - 1, len(self.lines[-1])):
            return self.deleteRange(
                LocationRange(
                    Location(0, 0), Location(len(self.lines) - 1, len(self.lines[-1]))
                )
            )

    def moveCursorStart(self) -> None:
        self.cursorLocation = Location(0, 0)

        self.notifyCursorObservers()

        self.selectionRange = None

        self.notifySelectObservers()
        self.notifyTextObservers()

    def moveCursorEnd(self) -> None:
        row, col = len(self.lines) - 1, len(self.lines[-1])

        self.cursorLocation = Location(row, col)

        self.notifyCursorObservers()

        self.selectionRange = None

        self.notifySelectObservers()
        self.notifyTextObservers()
