from tkinter import Tk
from text.text_editor import TextEditor
from menu.menu_bar import MenuBar
from toolbar.toolbar import Toolbar
from statusbar.statusbar import Statusbar
from text.text_editor_model import TextEditorModel
from clipboard.clipboard_stack import ClipboardStack
from undo.undo_manager import UndoManager
from plugin import loadPlugins


def main() -> None:
    window = Tk()
    tem = TextEditorModel(
        "The sky was painted with soft gold,\nWaves whispered secrets to the shore,\nLeaves danced under the autumn wind,\nSilent streets bathed in silver light,\nOld clocks ticked in sleepy rhythm,\nLanterns swung in the cooling breeze,\nForgotten songs hummed by the river,\nThe city breathed under velvet skies,\nFootsteps faded into the misty dark,\nDreams gathered on the edge of dawn."
    )
    cs = ClipboardStack()
    um = UndoManager.getInstance()
    mb = MenuBar(window)
    tb = Toolbar(window)
    sb = Statusbar(window)

    te = TextEditor(window, tem, cs, um, mb, tb, sb)

    plugins = loadPlugins()
    te.setPlugins(plugins)

    window.mainloop()


if __name__ == "__main__":
    main()
