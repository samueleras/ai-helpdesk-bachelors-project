import os
import pytest
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


def get_valid_assignee_id():
    response = client.get(
        "/api/technicians",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
    )
    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    technicians = response.json()
    assert isinstance(technicians, list), "Response should be a list"

    if not technicians:
        pytest.fail("No available technicians to assign.")

    return technicians[0]["user_id"]


def test_assign_ticket():
    assignee_id = get_valid_assignee_id()

    request_data = {
        "ticket_id": int(VALID_TICKET_ID),
        "assignee_id": assignee_id,
    }

    response = client.post(
        "/api/assign-ticket",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
        json=request_data,
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"


def test_assign_ticket_unauthorized():
    assignee_id = get_valid_assignee_id()

    request_data = {
        "ticket_id": int(VALID_TICKET_ID),
        "assignee_id": assignee_id,
    }

    response = client.post(
        "/api/assign-ticket",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
        json=request_data,
    )

    assert (
        response.status_code == 403
    ), f"Expected 403 for unauthorized access, got {response.status_code}"


def test_assign_ticket_invalid_input():
    assignee_id = get_valid_assignee_id()

    # Test with incorrect ticket_id type (should be int)
    invalid_data = {
        "ticket_id": "not_a_number",  # Invalid type
        "assignee_id": assignee_id,
    }

    response = client.post(
        "/api/assign-ticket",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
        json=invalid_data,
    )

    assert (
        response.status_code == 422
    ), f"Expected 422 for invalid ticket_id, got {response.status_code}"
