from unittest.mock import patch, call


def test_list_brands(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "b1", "name": "BrandA"}]

        result = client.opener.list_brands()

        mock_request.assert_has_calls([
            call("GET", "/opener/brand")
        ])
        assert isinstance(result, list)
        assert result[0]["id"] == "b1"


def test_get_brand(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "b1", "name": "BrandA"}

        result = client.opener.get_brand("b1")

        mock_request.assert_has_calls([
            call("GET", "/opener/brand/b1")
        ])
        assert result["id"] == "b1"


def test_list_intercoms(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"id": "i1", "model": "IntercomX"}]

        result = client.opener.list_intercoms()

        mock_request.assert_has_calls([
            call("GET", "/opener/intercom")
        ])
        assert isinstance(result, list)
        assert result[0]["id"] == "i1"


def test_get_intercom(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"id": "i1", "model": "IntercomX"}

        result = client.opener.get_intercom("i1")

        mock_request.assert_has_calls([
            call("GET", "/opener/intercom/i1")
        ])
        assert result["id"] == "i1"
