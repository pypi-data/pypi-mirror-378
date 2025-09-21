from unittest.mock import patch, call, MagicMock
import pytest


def test_list_smartlocks(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": 123, "name": "Front Door"}]

        result = client.smartlock.list_smartlocks()

        mock_request.assert_has_calls([call("GET", "/smartlock")])
        assert isinstance(result, list)
        assert result[0]["id"] == 123


def test_get_smartlock(client):
    with patch.object(client, "_request") as mock_request, \
         patch("nukiwebapi.smartlock.SmartlockInstance") as mock_instance:

        mock_request.return_value = {"id": 123, "name": "Front Door"}
        mock_instance.return_value = "mocked_instance"

        result = client.smartlock.get_smartlock(123)

        mock_request.assert_called_once_with("GET", "/smartlock/123")
        mock_instance.assert_called_once_with(client, 123, {"id": 123, "name": "Front Door"})
        assert result == "mocked_instance"


def test_bulk_web_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"foo": "bar"}
        result = client.smartlock.bulk_web_config(data)

        mock_request.assert_called_once_with("POST", "/bulk-web-config", json=data)
        assert result["status"] == "success"


def test_update_smartlock(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"foo": "bar"}
        result = client.smartlock.update_smartlock(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123", json=data)
        assert result["status"] == "success"


def test_delete_smartlock(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        result = client.smartlock.delete_smartlock(123)

        mock_request.assert_called_once_with("DELETE", "/smartlock/123")
        assert result["status"] == "success"


def test_action(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        action_data = {"action": 2}
        result = client.smartlock.action(123, action_data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/action", json=action_data)
        assert result["status"] == "success"


def test_update_admin_pin(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"pin": "1234"}
        result = client.smartlock.update_admin_pin(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/admin/pin", json=data)
        assert result["status"] == "success"


def test_update_advanced_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"a": 1}
        result = client.smartlock.update_advanced_config(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/advanced/config", json=data)
        assert result["status"] == "success"


def test_update_opener_advanced_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"o": 2}
        result = client.smartlock.update_opener_advanced_config(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/advanced/openerconfig", json=data)
        assert result["status"] == "success"


def test_update_smartdoor_advanced_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"s": 3}
        result = client.smartlock.update_smartdoor_advanced_config(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/advanced/smartdoorconfig", json=data)
        assert result["status"] == "success"


def test_update_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"c": 4}
        result = client.smartlock.update_config(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/config", json=data)
        assert result["status"] == "success"


def test_sync_smartlock(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        result = client.smartlock.sync_smartlock(123)

        mock_request.assert_called_once_with("POST", "/smartlock/123/sync")
        assert result["status"] == "success"


def test_update_web_config(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}

        data = {"w": 5}
        result = client.smartlock.update_web_config(123, data)

        mock_request.assert_called_once_with("POST", "/smartlock/123/web/config", json=data)
        assert result["status"] == "success"
