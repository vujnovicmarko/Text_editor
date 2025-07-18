from abc import ABC, abstractmethod


class EditAction(ABC):
    @abstractmethod
    def executeDo(self) -> None:
        pass

    @abstractmethod
    def executeUndo(self) -> None:
        pass
