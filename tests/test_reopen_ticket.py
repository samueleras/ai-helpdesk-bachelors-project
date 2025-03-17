import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN = os.getenv(
    "AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN"
)
assert (
    AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN
), "AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN is not set in environment variables!"
AZURE_USER_TESTING_ACCESS_TOKEN = os.getenv("AZURE_USER_TESTING_ACCESS_TOKEN")
assert (
    AZURE_USER_TESTING_ACCESS_TOKEN
), "AZURE_USER_TESTING_ACCESS_TOKEN is not set in environment variables!"
VALID_TICKET_ID = os.getenv("VALID_TICKET_ID")
assert VALID_TICKET_ID, "VALID_TICKET_ID is not set in environment variables!"


def test_reopen_ticket_authorized():

    request_data = {"ticket_id": int(VALID_TICKET_ID)}

    response = client.post(
        "/api/reopen-ticket",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
        json=request_data,
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"


def test_reopen_ticket_unauthorized():

    request_data = {"ticket_id": int(VALID_TICKET_ID)}

    response = client.post(
        "/api/reopen-ticket",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
        json=request_data,
    )

    assert response.status_code == 403, f"Unexpected response: {response.json()}"
