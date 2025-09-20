# tests/test_account.py
import pytest
from unittest.mock import patch, call
from nukiwebapi import NukiWebAPI




# ---- OTP tests ----
def test_enable_otp(client):
    result = client.account.enable_otp()
    client._mock_request.assert_called_with("POST", "/account/otp")
    assert result["status"] == "success"


def test_create_otp(client):
    data = {"method": "totp"}
    result = client.account.create_otp(data)
    client._mock_request.assert_called_with("PUT", "/account/otp", json=data)
    assert result["status"] == "success"


def test_disable_otp(client):
    result = client.account.disable_otp()
    client._mock_request.assert_called_with("DELETE", "/account/otp")
    assert result["status"] == "success"


# ---- Password reset ----
def test_reset_password(client):
    email = "user@example.com"
    delete_tokens = True

    result = client.account.reset_password(email=email, deleteApiTokens=delete_tokens)
    client._mock_request.assert_called_with(
        "POST",
        "/account/password/reset",
        json={"email": email, "deleteApiTokens": delete_tokens}
    )
    assert result["status"] == "success"


# ---- Account settings ----
def test_get_setting(client):
    result = client.account.get_setting()
    client._mock_request.assert_called_with("GET", "/account/setting")
    assert result["status"] == "success"


def test_update_setting(client):
    data = {"theme": "dark"}
    result = client.account.update_setting(data)
    client._mock_request.assert_called_with("PUT", "/account/setting", json=data)
    assert result["status"] == "success"


def test_delete_setting(client):
    key = "theme"
    result = client.account.delete_setting(key)
    client._mock_request.assert_called_with("DELETE", "/account/setting", json={"key": key})
    assert result["status"] == "success"


# ---- Sub-account management ----
def test_list_sub_accounts(client):
    result = client.account.list_sub_accounts()
    client._mock_request.assert_called_with("GET", "/account/sub")
    assert result["status"] == "success"


def test_create_sub_account(client):
    data = {"name": "SubUser"}
    result = client.account.create_sub_account(data)
    client._mock_request.assert_called_with("PUT", "/account/sub", json=data)
    assert result["status"] == "success"


def test_get_sub_account(client):
    account_id = "abc123"
    result = client.account.get_sub_account(account_id)
    client._mock_request.assert_called_with("GET", f"/account/sub/{account_id}")
    assert result["status"] == "success"


def test_update_sub_account(client):
    account_id = "abc123"
    data = {"name": "Updated"}
    result = client.account.update_sub_account(account_id, data)
    client._mock_request.assert_called_with("POST", f"/account/sub/{account_id}", json=data)
    assert result["status"] == "success"


def test_delete_sub_account(client):
    account_id = "abc123"
    result = client.account.delete_sub_account(account_id)
    client._mock_request.assert_called_with("DELETE", f"/account/sub/{account_id}")
    assert result["status"] == "success"


# ---- Account operations ----
def test_delete_account(client):
    result = client.account.delete()
    client._mock_request.assert_called_with("DELETE", "/account")
    assert result["status"] == "success"


def test_update_account(client):
    data = {"accountId": "FAKE"}
    result = client.account.update(data)
    client._mock_request.assert_called_with("POST", "/account", json=data)
    assert result["status"] == "success"


def test_change_email(client):
    result = client.account.change_email("fake_email")
    client._mock_request.assert_called_with("POST", "/account/email/change", json={"email": "fake_email"})
    assert result["status"] == "success"


def test_send_verification_email(client):
    result = client.account.verify_email()
    client._mock_request.assert_called_with("POST", "/account/email/verify")
    assert result["status"] == "success"


# ---- Account integrations ----
def test_delete_integration(client):
    apiKeyId = "abc123"
    tokenId = "deadbeef"
    result = client.account.delete_integration(apiKeyId, tokenId)
    client._mock_request.assert_called_with(
        "DELETE",
        "/account/integration",
        json={"apiKeyId": apiKeyId, "tokenId": tokenId}
    )
    assert result["status"] == "success"
