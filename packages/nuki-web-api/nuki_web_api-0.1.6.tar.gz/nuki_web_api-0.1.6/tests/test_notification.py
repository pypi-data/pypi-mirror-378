from unittest.mock import patch, call


def test_list_notifications(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "n1", "type": "email"}]

        result = client.notification.list_notifications()

        mock_request.assert_has_calls([
            call("GET", "/notification")
        ])
        assert isinstance(result, list)
        assert result[0]["id"] == "n1"


def test_create_notification(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "created"}
        data = {"type": "email", "target": "user@example.com"}

        result = client.notification.create_notification(data)

        mock_request.assert_has_calls([
            call("PUT", "/notification", json=data)
        ])
        assert result["status"] == "created"


def test_get_notification(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "n1", "type": "email"}

        result = client.notification.get_notification("n1")

        mock_request.assert_has_calls([
            call("GET", "/notification/n1")
        ])
        assert result["id"] == "n1"


def test_update_notification(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "updated"}
        data = {"type": "push"}

        result = client.notification.update_notification("n1", data)

        mock_request.assert_has_calls([
            call("POST", "/notification/n1", json=data)
        ])
        assert result["status"] == "updated"


def test_delete_notification(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "deleted"}

        result = client.notification.delete_notification("n1")

        mock_request.assert_has_calls([
            call("DELETE", "/notification/n1")
        ])
        assert result["status"] == "deleted"
