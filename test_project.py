from project import get_places, get_lati_longi, places_api_call, process_json
from unittest.mock import patch, MagicMock

@patch("project.get_lati_longi")
@patch("project.places_api_call")
@patch("project.process_json")
def test_get_places(mock_json, mock_api, mock_latlong):
    mock_latlong.return_value("-47.222,22.777")
    mock_json.return_value("tabulateobject")
    mock_api.return_value.json.return_value = {"results":[]}

    mock_gui = MagicMock()
    mock_gui.name_address.get.return_value = "harvard square"
    mock_gui.type_establishment.get.return_value = "restaurant"



    get_places(mock_gui)


    mock_latlong.assert_called_once()
    mock_api.assert_called_once_with(mock_latlong(), mock_gui.type_establishment.get(), mock_gui)
    mock_json.assert_called_once_with(mock_gui, mock_api.return_value.json()["results"])
