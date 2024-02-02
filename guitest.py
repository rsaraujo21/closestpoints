from project import DisplayWindow
from tkinter import *
from tkinter import ttk

def test_display_window():
    test_root = Tk()
    test_gui = DisplayWindow(test_root)
    # Test variables being created
    assert isinstance(test_gui.name_address, StringVar)
    assert isinstance(test_gui.type_establishment, StringVar)
    assert isinstance(test_gui.output_label, StringVar)
    assert isinstance(test_gui.error_label, StringVar)
    assert test_gui.lati_longi == None

    # Test mainframe and widgets being created
    assert "!frame" in test_root.children
    assert isinstance(test_root.children["!frame"], ttk.Frame)
    mainframe_widgets = test_root.children["!frame"].children
    labels = sum(isinstance(child, ttk.Label) for child in mainframe_widgets.values())
    assert labels == 5
    entries = sum(isinstance(child, ttk.Entry) for child in mainframe_widgets.values())
    assert entries == 2
    buttons = sum(isinstance(child, ttk.Button) for child in mainframe_widgets.values())
    assert buttons == 2
    # keybinds are being created
    assert "<Key-Return>" in test_root.bind()
    