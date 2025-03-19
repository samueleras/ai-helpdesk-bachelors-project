import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from authentication import fetch_user_access_token, fetch_technician_access_token
from datetime import datetime

client = TestClient(app)

AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN = fetch_technician_access_token()
AZURE_USER_TESTING_ACCESS_TOKEN = fetch_user_access_token()

VALID_TICKET_ID = os.getenv("VALID_TICKET_ID")
assert VALID_TICKET_ID, "VALID_TICKET_ID is not set in environment variables!"


def test_get_mytickets():
    valid_filter_data = {
        "page": 1,
        "page_size": 10,
    }

    response = client.post(
        "/api/my-tickets",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
        json=valid_filter_data,
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    ticket_list = response.json()
    assert isinstance(ticket_list, dict), "Response should be a dictionary"
    assert "count" in ticket_list and isinstance(
        ticket_list["count"], int
    ), "Invalid count format"
    assert "tickets" in ticket_list and isinstance(
        ticket_list["tickets"], list
    ), "Invalid tickets format"

    for ticket in ticket_list["tickets"]:
        assert isinstance(ticket, dict), "Each ticket should be a dictionary"
        assert isinstance(ticket["ticket_id"], int), "Invalid ticket_id"
        assert isinstance(ticket["title"], str), "Invalid title"
        assert isinstance(ticket["content"], str), "Invalid content"
        assert isinstance(ticket["creation_date"], str), "Invalid creation_date"
        assert isinstance(ticket["author_name"], str), "Invalid author_name"
        assert ticket["closed_date"] is None or isinstance(
            ticket["closed_date"], str
        ), "Invalid closed_date"
        assert ticket["assignee_name"] is None or isinstance(
            ticket["assignee_name"], str
        ), "Invalid assignee_name"
        assert isinstance(ticket["similar_tickets"], list), "Invalid similar_tickets"
        assert isinstance(ticket["ticket_messages"], list), "Invalid ticket_messages"

        try:
            datetime.fromisoformat(ticket["creation_date"])
        except ValueError:
            pytest.fail("Invalid datetime format for creation_date")

        if ticket["closed_date"]:
            try:
                datetime.fromisoformat(ticket["closed_date"])
            except ValueError:
                pytest.fail("Invalid datetime format for closed_date")


def test_get_mytickets_invalid_input():

    invalid_filter_data = {
        "page": "one",  # Invalid type
        "page_size": 10,
    }

    response = client.post(
        "/api/my-tickets",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
        json=invalid_filter_data,
    )

    assert (
        response.status_code == 422
    ), f"Expected 422 for invalid page, got {response.status_code}"
