from unittest.mock import Mock
from project import get_places


def test_get_places():
    test = Mock()
    test.name_address.set("harvard square")
    test.type_establishment.set("restaurant")

    get_places(test)

    assert test.name_address.set.call_count == 2
    test.name_address.set.assert_any_call("harvard square")
    test.name_address.set.assert_any_call("")

    assert test.type_establishment.set.call_count == 2
    test.type_establishment.set.assert_any_call("restaurant")
    test.type_establishment.set.assert_any_call("")
