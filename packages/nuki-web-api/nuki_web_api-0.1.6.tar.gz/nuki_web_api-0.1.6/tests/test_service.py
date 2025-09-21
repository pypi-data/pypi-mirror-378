from unittest.mock import patch, call


def test_list_services(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "s1", "name": "ServiceA"}]

        result = client.service.list_services()

        mock_request.assert_has_calls([
            call("GET", "/service")
        ])
        assert isinstance(result, list)
        assert result[0]["id"] == "s1"


def test_get_service(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "s1", "name": "ServiceA"}

        result = client.service.get_service("s1")

        mock_request.assert_has_calls([
            call("GET", "/service/s1")
        ])
        assert result["id"] == "s1"


def test_link_service(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "linked"}
        payload = {"foo": "bar"}

        result = client.service.link_service("s1", payload)

        mock_request.assert_has_calls([
            call("POST", "/service/s1/link", json=payload)
        ])
        assert result["status"] == "linked"


def test_sync_service(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "synced"}
        payload = {"sync": True}

        result = client.service.sync_service("s1", payload)

        mock_request.assert_has_calls([
            call("POST", "/service/s1/sync", json=payload)
        ])
        assert result["status"] == "synced"


def test_unlink_service(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "unlinked"}
        payload = {"confirm": True}

        result = client.service.unlink_service("s1", payload)

        mock_request.assert_has_calls([
            call("POST", "/service/s1/unlink", json=payload)
        ])
        assert result["status"] == "unlinked"
