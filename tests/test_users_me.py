import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.pydantic_models import User

client = TestClient(app)

AZURE_USER_TESTING_ACCESS_TOKEN = os.getenv("AZURE_USER_TESTING_ACCESS_TOKEN")
assert (
    AZURE_USER_TESTING_ACCESS_TOKEN
), "AZURE_USER_TESTING_ACCESS_TOKEN is not set in environment variables!"


def test_read_users_me():
    # Test valid token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    user_data = response.json()
    user = User(**user_data)

    assert isinstance(user.user_id, str)
    assert isinstance(user.user_name, str)
    assert isinstance(user.group, str)

    # Test missing token
    response_no_token = client.get("/api/users/me")
    assert (
        response_no_token.status_code == 401
    ), f"Unexpected response: {response_no_token.json()}"

    # Test invalid token
    response_invalid_token = client.get(
        "/api/users/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert (
        response_invalid_token.status_code == 401
    ), f"Unexpected response: {response_invalid_token.json()}"
