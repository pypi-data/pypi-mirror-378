from unittest.mock import patch, call


def test_list_addresses(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": 1, "street": "Main St"}]
        addresses = client.address.list_addresses()

        mock_request.assert_has_calls([
            call("GET", "/address")
        ])
        assert isinstance(addresses, list)
        assert addresses[0]["street"] == "Main St"


def test_create_address(client):
    new_address = {"street": "Broadway", "city": "NY"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": 42, **new_address}
        result = client.address.create_address(new_address)

        mock_request.assert_has_calls([
            call("PUT", "/address", json=new_address)
        ])
        assert result["id"] == 42


def test_update_address(client):
    updated = {"street": "Elm St"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        result = client.address.update_address(123, updated)

        mock_request.assert_has_calls([
            call("POST", "/address/123", json=updated)
        ])
        assert result["status"] == "success"


def test_delete_address(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "deleted"}
        result = client.address.delete_address(123)

        mock_request.assert_has_calls([
            call("DELETE", "/address/123")
        ])
        assert result["status"] == "deleted"


def test_list_address_units(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"unitId": "A1"}]
        result = client.address.list_address_units(123)

        mock_request.assert_has_calls([
            call("GET", "/address/123/unit")
        ])
        assert result[0]["unitId"] == "A1"


def test_create_address_unit(client):
    unit_data = {"name": "Unit 1"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "U1", **unit_data}
        result = client.address.create_address_unit(123, unit_data)

        mock_request.assert_has_calls([
            call("PUT", "/address/123/unit", json=unit_data)
        ])
        assert result["id"] == "U1"


def test_delete_address_units(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "all_deleted"}
        result = client.address.delete_address_units(123)

        mock_request.assert_has_calls([
            call("DELETE", "/address/123/unit")
        ])
        assert result["status"] == "all_deleted"


def test_delete_address_unit(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "deleted"}
        result = client.address.delete_address_unit(123, "U1")

        mock_request.assert_has_calls([
            call("DELETE", "/address/123/unit/U1")
        ])
        assert result["status"] == "deleted"
