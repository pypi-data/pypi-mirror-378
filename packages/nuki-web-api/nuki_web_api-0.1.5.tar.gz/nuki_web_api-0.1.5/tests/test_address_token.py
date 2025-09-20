from unittest.mock import patch, call


def test_get_token_info(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"tokenId": "T1", "status": "active"}
        result = client.address_token.get_token_info("T1")

        mock_request.assert_has_calls([
            call("GET", "/address/token/T1")
        ])
        assert result["status"] == "active"


def test_get_redeemed_token(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"tokenId": "T1", "redeemed": True}
        result = client.address_token.get_redeemed_token("T1")

        mock_request.assert_has_calls([
            call("GET", "/address/token/T1/redeem")
        ])
        assert result["redeemed"] is True


def test_redeem_token_with_payload(client):
    payload = {"user": "Alice"}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "redeemed"}
        result = client.address_token.redeem_token("T1", payload)

        mock_request.assert_has_calls([
            call("POST", "/address/token/T1/redeem", json=payload)
        ])
        assert result["status"] == "redeemed"


def test_redeem_token_without_payload(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "redeemed"}
        result = client.address_token.redeem_token("T1")

        mock_request.assert_has_calls([
            call("POST", "/address/token/T1/redeem", json={})
        ])
        assert result["status"] == "redeemed"


def test_list_tokens(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"tokenId": "T1"}, {"tokenId": "T2"}]
        result = client.address_token.list_tokens(123)

        mock_request.assert_has_calls([
            call("GET", "/address/123/token")
        ])
        assert isinstance(result, list)
        assert len(result) == 2
