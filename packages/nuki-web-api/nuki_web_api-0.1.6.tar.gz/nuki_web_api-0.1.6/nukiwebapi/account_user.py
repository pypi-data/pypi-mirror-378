class AccountUser:
    """Sub-client for managing account users."""

    def __init__(self, client):
        self.client = client

    def list_account_users(self):
        """List all account users.

        GET /account/user
        """
        return self.client._request("GET", "/account/user")

    def create_account_user(self, email: str, name: str, type: int | None = None, language: str | None = None):
        """Create a new account user.

        PUT /account/user

        Args:
            email (str): Email of the user (mandatory).
            name (str): Name of the user (mandatory).
            type (int, optional): User type, 0 = user, 1 = company (only for caretakers).
            language (str, optional): Language code.
                                      Allowed values: ["en", "de", "es", "fr", "it", "nl", "cs", "sk"]

        Returns:
            dict: API response
        """
        payload = {
            "email": email,
            "name": name,
        }

        if type is not None:
            if type not in (0, 1):
                raise ValueError("type must be 0 (user) or 1 (company)")
            payload["type"] = type

        if language is not None:
            allowed_languages = {"en", "de", "es", "fr", "it", "nl", "cs", "sk"}
            if language not in allowed_languages:
                raise ValueError(f"language must be one of {allowed_languages}")
            payload["language"] = language

        return self.client._request("PUT", "/account/user", json=payload)

    def get_account_user(self, account_user_id):
        """Get details of a specific account user.

        GET /account/user/{accountUserId}
        """
        return self.client._request("GET", f"/account/user/{account_user_id}")

    def update_account_user(self, account_user_id: str, email: str, name: str, language: str):
        """Update details of a specific account user.

        POST /account/user/{accountUserId}

        Args:
            account_user_id (str): ID of the account user to update.
            email (str): New email (mandatory).
            name (str): New name (mandatory).
            language (str): Language code (mandatory).
                            Allowed values: ["en", "de", "es", "fr", "it", "nl", "cs", "sk"]

        Returns:
            dict: API response
        """
        allowed_languages = {"en", "de", "es", "fr", "it", "nl", "cs", "sk"}
        if language not in allowed_languages:
            raise ValueError(f"language must be one of {allowed_languages}")

        payload = {
            "email": email,
            "name": name,
            "language": language,
        }

        return self.client._request("POST", f"/account/user/{account_user_id}", json=payload)

    def delete_account_user(self, account_user_id):
        """Delete a specific account user.

        DELETE /account/user/{accountUserId}
        """
        return self.client._request("DELETE", f"/account/user/{account_user_id}")