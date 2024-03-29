import os
import requests
from tkinter import *
from tkinter import ttk
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock, ANY
from project import (
    DisplayWindow,
    get_places,
    get_lati_longi,
    places_api_call,
    process_json,
    calc_distance,
    output_to_file,
)

load_dotenv()
API_KEY = os.getenv("API_KEY")


# tkinter gui initialization
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


# places_api_call tests
@patch("requests.get")
def test_places_api_call(mock_get):
    mock_gui = MagicMock()

    places_api_call("location", "keyword", mock_gui)

    arg1 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    arg2 = {
        "location": "location",
        "rankby": "distance",
        "keyword": "keyword",
        "key": API_KEY,
    }

    mock_get.assert_called_once_with(arg1, params=arg2)


@patch("requests.get")
def test_places_api_call_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException
    mock_gui = MagicMock()

    response = places_api_call("location", "keyword", mock_gui)

    mock_gui.error_label.set.assert_called_once_with("Error: Failed API request.")
    assert response == {"results": []}


# get_places tests
@patch("project.get_lati_longi")
@patch("project.places_api_call")
@patch("project.process_json")
def test_get_places(mock_json, mock_api, mock_latlong):
    mock_api.return_value.json.return_value = {"results": []}

    mock_gui = MagicMock()
    get_places(mock_gui)

    mock_latlong.assert_called_once_with(mock_gui)
    mock_api.assert_called_once_with(
        mock_latlong(), mock_gui.type_establishment.get(), mock_gui
    )
    mock_json.assert_called_once_with(mock_gui, mock_api.return_value.json()["results"])

    assert mock_gui.error_label.set.call_count == 2
    assert mock_gui.error_label.set.call_args_list[0][0] == ("",)
    assert str(mock_gui.error_label.set.call_args_list[1][0][0]) == "No results found."

    assert (
        mock_gui.type_establishment.get.call_count == 2
    )  # One in get_places, one in mock_api assertion
    
    # Clear textvariables
    mock_gui.type_establishment.set.assert_called_once_with("")
    mock_gui.name_address.set.assert_called_once_with("")

    mock_gui.output_label.set.assert_called_once_with(
        mock_json()[0]
    )  # process_json returns 2 value tuple, [0] tabulate [1] raw data


# process_jason tests
@patch("project.calc_distance")
def test_process_json(mock_calc_distance):
    mock_calc_distance.return_value = 1000
    mock_gui = MagicMock()

    placesjson = [
        {
            "name": "Place1",
            "opening_hours": {"open_now": True},
            "geometry": {"location": {"lat": 1, "lng": 1}},
        },
        {
            "name": "Place2",
            "opening_hours": {"open_now": False},
            "geometry": {"location": {"lat": 2, "lng": 2}},
        },
    ]

    return_value = process_json(
        mock_gui, placesjson
    )  # [0] = tabulated data [1] raw data

    expected_return_value = [
        {
            "Name": "Place1",
            "Status": "Open",
            "Rating": "Not Available",
            "User Ratings": "Not Available",
            "Distance": 1000,
            "Address": "Not Available",
        },
        {
            "Name": "Place2",
            "Status": "Closed",
            "Rating": "Not Available",
            "User Ratings": "Not Available",
            "Distance": 1000,
            "Address": "Not Available",
        },
    ]
    assert return_value[1] == expected_return_value
    assert type(return_value[0]) == str

    assert mock_calc_distance.call_count == 2
    mock_calc_distance.assert_any_call(mock_gui.lati_longi, "1,1")
    mock_calc_distance.assert_any_call(mock_gui.lati_longi, "2,2")


# calc_distance tests
def test_calc_distance():
    # meters
    user_location = "42.37365,-71.11896"
    place_location = "42.37854,-71.11518"
    expected_return_value = "626m"
    return_value = calc_distance(user_location, place_location)
    assert return_value == expected_return_value
    # kilometers
    user_location2 = "42.37365,-71.11896"
    place_location2 = "40.7505085,-73.9960136"
    expected_return_value2 = "299.8km"
    return_value2 = calc_distance(user_location2, place_location2)
    assert return_value2 == expected_return_value2


# get_lati_longi tests
def test_get_lati_longi():
    mock_gui = MagicMock()
    mock_gui.name_address.get.return_value = "harvard square"
    return_value = get_lati_longi(mock_gui)
    expected_return_value = "42.3734734,-71.1189431"

    assert return_value == expected_return_value
    mock_gui.name_address.get.assert_called_once()


def test_get_lati_longi_error():
    mock_gui = MagicMock()
    mock_gui.name_address.get.return_value = "FKAJDFLÇAKFJLADJFLAKDFJALFJLADKFJALDF"
    get_lati_longi(mock_gui)

    mock_gui.name_address.get.assert_called_once()
    mock_gui.error_label.set.assert_called_once_with("Invalid location.")


# output_to_file tests
@patch("builtins.open")
def test_output_to_file(mock_open):
    mock_gui = MagicMock()
    mock_gui.output_label.get.return_value = "Test"
    output_to_file(mock_gui)

    mock_gui.output_label.get.assert_called_once()
    mock_open.assert_called_once_with(ANY, "w", encoding="utf-8")
    file = mock_open.return_value.__enter__.return_value
    file.write.assert_called_once_with("Test")


@patch("builtins.open")
def test_output_to_file_error(mock_open):
    mock_gui = MagicMock()
    mock_open.side_effect = IOError
    output_to_file(mock_gui)
    mock_gui.error_label.set.assert_called_once_with("Error: Unable to save file.")
