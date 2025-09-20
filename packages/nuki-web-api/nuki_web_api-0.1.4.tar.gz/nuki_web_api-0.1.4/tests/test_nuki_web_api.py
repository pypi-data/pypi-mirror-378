import pytest
from unittest.mock import patch, Mock
from nukiwebapi.nuki_web_api import NukiWebAPI, SmartlockInstance


# --- _fetch_smartlocks edge cases ---
def test_fetch_smartlocks_invalid_response_type():
    """_fetch_smartlocks raises ValueError if response is not a list."""
    with patch.object(NukiWebAPI, "_request", return_value={"not": "a list"}):
        client = NukiWebAPI("FAKE_API_KEY")
        with pytest.raises(ValueError, match="Expected list from /smartlock"):
            client._fetch_smartlocks()


def test_fetch_smartlocks_skips_items_without_id():
    """_fetch_smartlocks skips smartlock entries without 'smartlockId'."""
    fake_response = [
        {"smartlockId": 123, "name": "Lock 123"},
        {"name": "No ID"}  # should be skipped
    ]
    with patch.object(NukiWebAPI, "_request", return_value=fake_response):
        client = NukiWebAPI("FAKE_API_KEY")
        locks = client._fetch_smartlocks()
        assert 123 in locks
        assert len(locks) == 1
        assert isinstance(locks[123], SmartlockInstance)


# --- _request edge cases ---
def test_request_returns_raw_text_on_invalid_json():
    """_request returns raw text if JSON parsing fails."""
    fake_response = Mock()
    fake_response.text = "not a json"
    fake_response.raise_for_status = Mock()
    fake_response.json.side_effect = ValueError

    with patch("requests.request", return_value=fake_response):
        client = NukiWebAPI("FAKE_API_KEY")
        result = client._request("GET", "/some/endpoint")
        assert result == "not a json"


def test_request_returns_none_on_empty_response():
    """_request returns None if response body is empty."""
    fake_response = Mock()
    fake_response.text = ""
    fake_response.raise_for_status = Mock()

    with patch("requests.request", return_value=fake_response):
        client = NukiWebAPI("FAKE_API_KEY")
        result = client._request("GET", "/empty")
        assert result is None


def test_request_calls_requests_with_correct_headers():
    """_request sets Authorization and Accept headers correctly."""
    fake_response = Mock()
    fake_response.text = '{"ok": true}'
    fake_response.raise_for_status = Mock()
    fake_response.json.return_value = {"ok": True}

    with patch("requests.request", return_value=fake_response) as mock_req:
        client = NukiWebAPI("FAKE_API_KEY")
        result = client._request("GET", "/test", headers={"X-Custom": "Value"})

        mock_req.assert_called_once()
        args, kwargs = mock_req.call_args
        # Verify headers
        assert kwargs["headers"]["Authorization"] == "Bearer FAKE_API_KEY"
        assert kwargs["headers"]["Accept"] == "application/json"
        assert kwargs["headers"]["X-Custom"] == "Value"
        # Verify return value
        assert result == {"ok": True}
