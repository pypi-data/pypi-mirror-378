import pytest
from unittest.mock import patch, call
from nukiwebapi import NukiWebAPI

def test_list_account_users(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.side_effect = [

            [{"id": 1, "name": "Alice"}]  # GET /account/user
        ]
        account_users = client.account_user.list_account_users()
        mock_request.assert_has_calls([
            call("GET", "/account/user")
        ])
        assert isinstance(account_users, list)
        assert account_users[0]["name"] == "Alice"

def test_create_account_user(client):
    user_data = {"name": "Bob"}
    with patch.object(client, "_request") as mock_request:
        mock_request.side_effect = [

            {"status": "success"}  # PUT /account/user
        ]
        result = client.account_user.create_account_user(user_data)
        mock_request.assert_has_calls([
            call("PUT", "/account/user", json=user_data)
        ])
        assert result["status"] == "success"

def test_get_account_user(client):
    user_id = "123"
    with patch.object(client, "_request") as mock_request:
        mock_request.side_effect = [
            {"id": user_id, "name": "Charlie"}  # GET /account/user/123
        ]
        result = client.account_user.get_account_user(user_id)
        mock_request.assert_has_calls([
            call("GET", f"/account/user/{user_id}")
        ])
        assert result["id"] == user_id

def test_update_account_user(client):
    user_id = "456"
    user_data = {"name": "Dana"}
    with patch.object(client, "_request") as mock_request:
        mock_request.side_effect = [
            {"status": "success"}  # POST /account/user/456
        ]
        result = client.account_user.update_account_user(user_id, user_data)
        mock_request.assert_has_calls([
            call("POST", f"/account/user/{user_id}", json=user_data)
        ])
        assert result["status"] == "success"

def test_delete_account_user(client):
    user_id = "789"
    with patch.object(client, "_request") as mock_request:
        mock_request.side_effect = [
            {"status": "success"}  # DELETE /account/user/789
        ]
        result = client.account_user.delete_account_user(user_id)
        mock_request.assert_has_calls([
            call("DELETE", f"/account/user/{user_id}")
        ])
        assert result["status"] == "success"
