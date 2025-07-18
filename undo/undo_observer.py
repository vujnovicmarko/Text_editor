from abc import ABC, abstractmethod


class UndoObserver(ABC):
    @abstractmethod
    def updateUndoStack(self, isEmpty: bool) -> None:
        pass
