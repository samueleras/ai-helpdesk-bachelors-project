import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from authentication import fetch_technician_access_token
from datetime import datetime

client = TestClient(app)

AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN = fetch_technician_access_token()

VALID_TICKET_ID = os.getenv("VALID_TICKET_ID")
assert VALID_TICKET_ID, "VALID_TICKET_ID is not set in environment variables!"


def test_get_ticket_by_id(ticket_id=VALID_TICKET_ID):

    response = client.get(
        f"/api/ticket/{ticket_id}",
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    ticket = response.json()

    assert isinstance(ticket, dict), "Response is not a dictionary"
    assert isinstance(ticket.get("ticket_id"), int)
    assert isinstance(ticket.get("title"), str)
    assert isinstance(ticket.get("content"), str)
    assert isinstance(ticket.get("creation_date"), str)  # Should be datetime string
    assert isinstance(ticket.get("author_name"), str)
    assert ticket.get("closed_date") is None or isinstance(
        ticket.get("closed_date"), str
    )
    assert ticket.get("assignee_name") is None or isinstance(
        ticket.get("assignee_name"), str
    )
    assert isinstance(ticket.get("similar_tickets"), list)
    assert isinstance(ticket.get("ticket_messages"), list)

    try:
        datetime.fromisoformat(ticket["creation_date"])
    except ValueError:
        pytest.fail("Invalid datetime format for creation_date")

    if ticket.get("closed_date"):
        try:
            datetime.fromisoformat(ticket["closed_date"])
        except ValueError:
            pytest.fail("Invalid datetime format for closed_date")
