from abc import ABC, abstractmethod


class RedoObserver(ABC):
    @abstractmethod
    def updateRedoStack(self, isEmpty: bool) -> None:
        pass
