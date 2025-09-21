from unittest.mock import patch, call


# ---- API Keys ----
def test_list_api_keys(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "k1"}]
        result = client.api_key.list_api_keys()

        mock_request.assert_has_calls([
            call("GET", "/api/key")
        ])
        assert result[0]["id"] == "k1"


def test_create_api_key(client):
    key_data = {"name": "test-key"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "k1"}
        result = client.api_key.create_api_key(key_data)

        mock_request.assert_has_calls([
            call("PUT", "/api/key", json=key_data)
        ])
        assert result["id"] == "k1"


def test_update_api_key(client):
    key_data = {"name": "updated-key"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "ok"}
        result = client.api_key.update_api_key("k1", key_data)

        mock_request.assert_has_calls([
            call("POST", "/api/key/k1", json=key_data)
        ])
        assert result["status"] == "ok"


def test_delete_api_key(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"deleted": True}
        result = client.api_key.delete_api_key("k1")

        mock_request.assert_has_calls([
            call("DELETE", "/api/key/k1")
        ])
        assert result["deleted"] is True


# ---- Advanced API Keys ----
def test_get_advanced_api_key(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "k1", "type": "advanced"}
        result = client.api_key.get_advanced_api_key("k1")

        mock_request.assert_has_calls([
            call("GET", "/api/key/k1/advanced")
        ])
        assert result["type"] == "advanced"


def test_update_advanced_api_key(client):
    data = {"name": "adv-update"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "updated"}
        result = client.api_key.update_advanced_api_key("k1", data)

        mock_request.assert_has_calls([
            call("POST", "/api/key/k1/advanced", json=data)
        ])
        assert result["status"] == "updated"


def test_create_advanced_api_key(client):
    data = {"name": "adv-create"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "adv1"}
        result = client.api_key.create_advanced_api_key("k1", data)

        mock_request.assert_has_calls([
            call("PUT", "/api/key/k1/advanced", json=data)
        ])
        assert result["id"] == "adv1"


def test_delete_advanced_api_key(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"deleted": True}
        result = client.api_key.delete_advanced_api_key("k1")

        mock_request.assert_has_calls([
            call("DELETE", "/api/key/k1/advanced")
        ])
        assert result["deleted"] is True


def test_reactivate_advanced_api_key(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "reactivated"}
        result = client.api_key.reactivate_advanced_api_key("k1")

        mock_request.assert_has_calls([
            call("POST", "/api/key/k1/advanced/reactivate")
        ])
        assert result["status"] == "reactivated"


# ---- API Key Tokens ----
def test_list_api_key_tokens(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "t1"}]
        result = client.api_key.list_api_key_tokens("k1")

        mock_request.assert_has_calls([
            call("GET", "/api/key/k1/token")
        ])
        assert result[0]["id"] == "t1"


def test_create_api_key_token(client):
    token_data = {"scope": "read"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "t1"}
        result = client.api_key.create_api_key_token("k1", token_data)

        mock_request.assert_has_calls([
            call("PUT", "/api/key/k1/token", json=token_data)
        ])
        assert result["id"] == "t1"


def test_update_api_key_token(client):
    token_data = {"scope": "write"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "ok"}
        result = client.api_key.update_api_key_token("k1", "t1", token_data)

        mock_request.assert_has_calls([
            call("POST", "/api/key/k1/token/t1", json=token_data)
        ])
        assert result["status"] == "ok"


def test_delete_api_key_token(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"deleted": True}
        result = client.api_key.delete_api_key_token("k1", "t1")

        mock_request.assert_has_calls([
            call("DELETE", "/api/key/k1/token/t1")
        ])
        assert result["deleted"] is True
