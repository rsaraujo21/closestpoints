from tkinter import *
from project import DisplayWindow, get_places
from unittest.mock import patch


def test_get_places_correct():
    root = Tk()
    root.withdraw()
    test = DisplayWindow(root)
    test.name_address.set("harvard square")
    test.type_establishment.set("restaurant")
    get_places(test)
    root.update()
    assert test.name_address.get() == ""
    assert test.type_establishment.get() == ""
    assert test.output_label.get() != ""
    assert test.error_label.get() == ""
    root.destroy()


