from abc import ABC, abstractmethod


class SelectObserver(ABC):
    @abstractmethod
    def updateSelect(self, isSelected: bool) -> None:
        pass
