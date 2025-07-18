from __future__ import annotations
from typing import TYPE_CHECKING
from tkinter import Event

if TYPE_CHECKING:
    from action.edit_action import EditAction
    from undo.undo_observer import UndoObserver
    from undo.redo_observer import RedoObserver


class UndoManager:
    _instance: UndoManager | None = None

    def __init__(self) -> None:
        assert UndoManager._instance is None

        self.undoStack: list[EditAction] = []
        self.redoStack: list[EditAction] = []
        self.undoObservers: list[UndoObserver] = []
        self.redoObservers: list[RedoObserver] = []
        UndoManager._instance = self

    def undo(self, event: Event | None) -> None:
        if not self.undoStack:
            return

        action = self.undoStack.pop()
        self.redoStack.append(action)
        action.executeUndo()

        self.notifyUndoObservers()
        self.notifyRedoObservers()

    def redo(self, event: Event | None) -> None:
        if not self.redoStack:
            return

        action = self.redoStack.pop()
        self.undoStack.append(action)
        action.executeDo()

        self.notifyUndoObservers()
        self.notifyRedoObservers()

    def push(self, action: EditAction | None) -> None:
        if not action:
            return

        self.redoStack = []
        self.undoStack.append(action)

        self.notifyUndoObservers()
        self.notifyRedoObservers()

    @staticmethod
    def getInstance() -> UndoManager:
        if UndoManager._instance is None:
            UndoManager()

        assert UndoManager._instance is not None
        return UndoManager._instance

    def addUndoObserver(self, undoObserver: UndoObserver) -> None:
        self.undoObservers.append(undoObserver)

    def removeUndoObserver(self, undoObserver: UndoObserver) -> None:
        self.undoObservers.remove(undoObserver)

    def notifyUndoObservers(self) -> None:
        for undoObserver in self.undoObservers:
            undoObserver.updateUndoStack(len(self.undoStack) == 0)

    def addRedoObserver(self, redoObserver: RedoObserver) -> None:
        self.redoObservers.append(redoObserver)

    def removeRedoObserver(self, redoObserver: RedoObserver) -> None:
        self.redoObservers.remove(redoObserver)

    def notifyRedoObservers(self) -> None:
        for redoObserver in self.redoObservers:
            redoObserver.updateRedoStack(len(self.redoStack) == 0)
