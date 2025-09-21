from unittest.mock import patch, call


def test_list_decentral_webhooks(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "w1"}]
        result = client.advanced_api.list_decentral_webhooks()

        mock_request.assert_has_calls([
            call("GET", "/api/decentralWebhook")
        ])
        assert isinstance(result, list)
        assert result[0]["id"] == "w1"


def test_create_decentral_webhook(client):
    data = {"url": "https://example.com/webhook"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "created"}
        result = client.advanced_api.create_decentral_webhook(data)

        mock_request.assert_has_calls([
            call("PUT", "/api/decentralWebhook", json=data)
        ])
        assert result["status"] == "created"


def test_delete_decentral_webhook(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "deleted"}
        result = client.advanced_api.delete_decentral_webhook("w1")

        mock_request.assert_has_calls([
            call("DELETE", "/api/decentralWebhook/w1")
        ])
        assert result["status"] == "deleted"


def test_get_webhook_logs(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"event": "delivered"}]
        result = client.advanced_api.get_webhook_logs("k1")

        mock_request.assert_has_calls([
            call("GET", "/api/key/k1/webhook/logs")
        ])
        assert result[0]["event"] == "delivered"


def test_create_smartlock_auth_advanced(client):
    auth_data = {"user": "Alice"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "pending"}
        result = client.advanced_api.create_smartlock_auth_advanced(auth_data)

        mock_request.assert_has_calls([
            call("PUT", "/smartlock/auth/advanced", json=auth_data)
        ])
        assert result["status"] == "pending"


def test_action_smartlock_advanced(client):
    action_data = {"action": "unlock"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "executed"}
        result = client.advanced_api.action_smartlock_advanced(123, action_data)

        mock_request.assert_has_calls([
            call("POST", "/smartlock/123/action/advanced", json=action_data)
        ])
        assert result["status"] == "executed"


def test_lock_smartlock_advanced_with_data(client):
    lock_data = {"mode": "full"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "locked"}
        result = client.advanced_api.lock_smartlock_advanced(123, lock_data)

        mock_request.assert_has_calls([
            call("POST", "/smartlock/123/action/lock/advanced", json=lock_data)
        ])
        assert result["status"] == "locked"


def test_lock_smartlock_advanced_without_data(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "locked"}
        result = client.advanced_api.lock_smartlock_advanced(123)

        mock_request.assert_has_calls([
            call("POST", "/smartlock/123/action/lock/advanced", json={})
        ])
        assert result["status"] == "locked"


def test_unlock_smartlock_advanced_with_data(client):
    unlock_data = {"fast": True}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "unlocked"}
        result = client.advanced_api.unlock_smartlock_advanced(123, unlock_data)

        mock_request.assert_has_calls([
            call("POST", "/smartlock/123/action/unlock/advanced", json=unlock_data)
        ])
        assert result["status"] == "unlocked"


def test_unlock_smartlock_advanced_without_data(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "unlocked"}
        result = client.advanced_api.unlock_smartlock_advanced(123)

        mock_request.assert_has_calls([
            call("POST", "/smartlock/123/action/unlock/advanced", json={})
        ])
        assert result["status"] == "unlocked"
