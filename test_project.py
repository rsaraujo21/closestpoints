import os
import requests
from dotenv import load_dotenv
from project import get_places, get_lati_longi, places_api_call, process_json
from unittest.mock import patch, MagicMock


load_dotenv()
API_KEY = os.getenv("API_KEY")


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

    mock_gui.output_label.set.assert_called_once_with(mock_json())


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


if __name__ == "__main__":
    test_places_api_call()
