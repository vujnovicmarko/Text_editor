from abc import ABC, abstractmethod
import os
from importlib import import_module
from collections.abc import Callable
from text.text_editor_model import TextEditorModel
from undo.undo_manager import UndoManager
from clipboard.clipboard_stack import ClipboardStack


class Plugin(ABC):
    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getDescription(self) -> str:
        pass

    @abstractmethod
    def execute(
        self,
        model: TextEditorModel,
        undoManager: UndoManager,
        clipboardStack: ClipboardStack,
    ) -> None:
        pass


def pluginFactory(pluginName: str) -> Callable[[], Plugin]:
    className = "".join([plugin.capitalize() for plugin in pluginName.split("_")])
    return getattr(import_module(f"plugins.{pluginName}"), className)


def loadPlugins() -> list[Plugin]:
    plugins = []

    for plugin in os.listdir("plugins"):
        pluginName, pluginExt = os.path.splitext(plugin)

        if pluginExt == ".py":
            plugin = pluginFactory(pluginName)()
            plugins.append(plugin)

    return plugins
