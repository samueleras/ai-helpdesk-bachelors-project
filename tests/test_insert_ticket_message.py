from fastapi.testclient import TestClient
from datetime import datetime
import os
from authentication import fetch_technician_access_token
from backend.main import app

client = TestClient(app)

AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN = fetch_technician_access_token()

VALID_TICKET_ID = os.getenv("VALID_TICKET_ID")
assert VALID_TICKET_ID, "VALID_TICKET_ID is not set in environment variables!"


def test_insert_ticket_message():
    new_message = {
        "ticket_id": int(VALID_TICKET_ID),
        "message": "This is a test message",
        "created_at": datetime.now().isoformat(),
    }

    response = client.post(
        "/api/insert-ticket-message",
        json=new_message,
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"


def test_insert_ticket_message_invalid_data():
    invalid_message = {
        "ticket_id": "not_a_number",
        "message": 12345,
        "created_at": "invalid_date_format",
    }

    response = client.post(
        "/api/insert-ticket-message",
        json=invalid_message,
        headers={"Authorization": f"Bearer {AZURE_TECHNICIAN_TESTING_ACCESS_TOKEN}"},
    )

    assert response.status_code == 422, f"Unexpected response: {response.json()}"
