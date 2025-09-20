from unittest.mock import patch, call
import pytest


def test_list_auths(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": 1}]
        result = client.smartlock_auth.list_auths()
        mock_request.assert_called_once_with("GET", "/smartlock/auth")
        assert result[0]["id"] == 1


def test_create_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"user": "alice"}
        result = client.smartlock_auth.create_auth(data)
        mock_request.assert_called_once_with("PUT", "/smartlock/auth", json=data)
        assert result["status"] == "success"


def test_update_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"user": "bob"}
        result = client.smartlock_auth.update_auth(data)
        mock_request.assert_called_once_with("POST", "/smartlock/auth", json=data)
        assert result["status"] == "success"


def test_delete_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"id": 1}
        result = client.smartlock_auth.delete_auth(data)
        mock_request.assert_called_once_with("DELETE", "/smartlock/auth", json=data)
        assert result["status"] == "success"


def test_list_auths_paged(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"page": 1, "items": []}
        params = {"limit": 10}
        result = client.smartlock_auth.list_auths_paged(params)
        mock_request.assert_called_once_with("GET", "/smartlock/auth/paged", params=params)
        assert result["page"] == 1


def test_list_auths_for_smartlock(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": 2}]
        result = client.smartlock_auth.list_auths_for_smartlock("123")
        mock_request.assert_called_once_with("GET", "/smartlock/123/auth")
        assert result[0]["id"] == 2


def test_create_auth_for_smartlock(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"user": "alice"}
        result = client.smartlock_auth.create_auth_for_smartlock("123", data)
        mock_request.assert_called_once_with("PUT", "/smartlock/123/auth", json=data)
        assert result["status"] == "success"


def test_generate_shared_key_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"key": "xyz"}
        result = client.smartlock_auth.generate_shared_key_auth("123", data)
        mock_request.assert_called_once_with(
            "POST", "/smartlock/123/auth/advanced/sharedkey", json=data
        )
        assert result["status"] == "success"


def test_get_smartlock_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "auth1"}
        result = client.smartlock_auth.get_smartlock_auth("123", "auth1")
        mock_request.assert_called_once_with("GET", "/smartlock/123/auth/auth1")
        assert result["id"] == "auth1"


def test_update_smartlock_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        data = {"user": "bob"}
        result = client.smartlock_auth.update_smartlock_auth("123", "auth1", data)
        mock_request.assert_called_once_with("POST", "/smartlock/123/auth/auth1", json=data)
        assert result["status"] == "success"


def test_delete_smartlock_auth(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "success"}
        result = client.smartlock_auth.delete_smartlock_auth("123", "auth1")
        mock_request.assert_called_once_with("DELETE", "/smartlock/123/auth/auth1")
        assert result["status"] == "success"
