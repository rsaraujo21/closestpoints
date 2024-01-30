from project import get_places, get_lati_longi, places_api_call, process_json
from unittest.mock import patch, MagicMock


@patch("project.get_lati_longi")
@patch("project.places_api_call")
@patch("project.process_json")
def test_get_places(mock_json, mock_api, mock_latlong):
    mock_latlong.return_value("-47.222,22.777")
    mock_json.return_value("tabulate object")
    mock_api.return_value.json.return_value = {"results": []}

    mock_gui = MagicMock()
    mock_gui.name_address.get.return_value = "harvard square"
    mock_gui.type_establishment.get.return_value = "restaurant"
    mock_gui.error_label

    get_places(mock_gui)

    mock_latlong.assert_called_once()
    mock_api.assert_called_once_with(
        mock_latlong(), mock_gui.type_establishment.get(), mock_gui
    )
    mock_json.assert_called_once_with(mock_gui, mock_api.return_value.json()["results"])

    assert mock_gui.error_label.set.call_count == 2
    assert mock_gui.error_label.set.call_args_list[0][0] == ("",)
    assert str(mock_gui.error_label.set.call_args_list[1][0][0]) == "No results found."

    

