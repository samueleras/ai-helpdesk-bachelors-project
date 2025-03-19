import os
from fastapi.testclient import TestClient
from authentication import fetch_user_access_token, fetch_technician_access_token
from backend.main import app

client = TestClient(app)

AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN = fetch_technician_access_token()
AZURE_USER_TESTING_ACCESS_TOKEN = fetch_user_access_token()

VALID_TICKET_ID = os.getenv("VALID_TICKET_ID")
assert VALID_TICKET_ID, "VALID_TICKET_ID is not set in environment variables!"


def test_get_technicians():
    response = client.get(
        "/api/technicians",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    technicians = response.json()
    assert isinstance(technicians, list), "Response should be a list"

    for technician in technicians:
        assert isinstance(technician, dict), "Each technician should be a dictionary"
        assert "user_id" in technician and isinstance(
            technician["user_id"], str
        ), "Invalid user_id"
        assert "user_name" in technician and isinstance(
            technician["user_name"], str
        ), "Invalid user_name"


def test_get_technicians_unauthorized():
    response = client.get(
        "/api/technicians",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
    )

    assert (
        response.status_code == 403
    ), f"Expected 403 for unauthorized access, got {response.status_code}"
