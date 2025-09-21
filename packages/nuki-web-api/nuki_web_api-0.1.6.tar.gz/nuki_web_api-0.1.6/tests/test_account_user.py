import os
import random
import pytest
from nukiwebapi.nuki_web_api import NukiWebAPI

API_TOKEN = os.getenv("NUKI_API_TOKEN")
EMAIL_PREFIX = os.getenv("TEST_EMAIL_PREFIX")  # e.g. "blachosf"

if not API_TOKEN or not EMAIL_PREFIX:
    pytest.skip("NUKI_API_TOKEN or TEST_EMAIL_PREFIX not set", allow_module_level=True)


@pytest.fixture(scope="module")
def client():
    """Real API client."""
    return NukiWebAPI(API_TOKEN)


def base_email():
    """Base email schema for account user tests."""
    return f"{EMAIL_PREFIX}+accountusertest@gmail.com"


def update_email():
    """Randomized email for update tests (001–999 suffix)."""
    suffix = f"{random.randint(1,999):03d}"
    return f"{EMAIL_PREFIX}+accountusertest{suffix}@gmail.com"


@pytest.fixture
def test_user(client):
    """Create a temporary user before test and delete after."""
    email = base_email()
    created = client.account_user.create_account_user(email, "Test User", type=0, language="en")
    user_id = created.get("accountUserId")

    yield created  # provide user to the test

    # Teardown: delete if still exists
    try:
        client.account_user.delete_account_user(user_id)
    except Exception as e:
        print(f"Teardown failed for user {user_id}: {e}")


def test_create_account_user(client, test_user):
    """Verify user was created and returned in list."""
    assert "accountUserId" in test_user
    listed = client.account_user.list_account_users()
    ids = [u["accountUserId"] for u in listed]
    assert test_user["accountUserId"] in ids


def test_get_and_update_account_user(client, test_user):
    """Get and update user details."""
    user_id = test_user["accountUserId"]

    # Get
    fetched = client.account_user.get_account_user(user_id)
    assert fetched["accountUserId"] == user_id
    assert fetched["email"] == test_user["email"]

    # Update with new email + name
    new_email = update_email()
    updated = client.account_user.update_account_user(
        user_id,
        email=new_email,
        name="Updated Name",
        language="de"
    )
    assert updated["name"] == "Updated Name"
    assert updated["language"] == "de"
    assert updated["email"] == new_email


def test_delete_account_user(client):
    """Create a user and then delete it explicitly."""
    email = base_email()
    user = client.account_user.create_account_user(email, "ToDelete", type=0, language="en")
    user_id = user["accountUserId"]

    deleted = client.account_user.delete_account_user(user_id)
    assert deleted.get("status") == "success"

    # Verify it’s gone
    users = client.account_user.list_account_users()
    assert all(u["accountUserId"] != user_id for u in users)


# -------------------
# Validation tests
# -------------------

def test_invalid_type_rejected(client):
    """Ensure invalid type raises ValueError (not sent to API)."""
    with pytest.raises(ValueError, match="type must be 0 or 1"):
        client.account_user.create_account_user(
            base_email(), "BadType", type=99, language="en"
        )


def test_invalid_language_rejected(client):
    """Ensure invalid language raises ValueError (not sent to API)."""
    with pytest.raises(ValueError, match="language must be one of"):
        client.account_user.create_account_user(
            base_email(), "BadLang", type=0, language="xx"
        )
