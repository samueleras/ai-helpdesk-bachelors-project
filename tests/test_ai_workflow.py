import os
from typing import Optional, TypedDict
from fastapi.testclient import TestClient
from authentication import fetch_user_access_token
from backend.main import app
from utils import load_json
from custom_types import AppConfig

client = TestClient(app)

app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config: AppConfig = load_json(os.path.join(app_path, "config.json"))

AZURE_USER_TESTING_ACCESS_TOKEN = fetch_user_access_token()


class APIWorkflowResponse(TypedDict):
    llm_output: Optional[str]
    ticket_id: Optional[int]
    ticket: Optional[bool]


def test_troubleshooting_ai_workflow():
    request_data = {
        "conversation": [("user", "My monitor does not work.")],
        "ticket": False,
        "execution_count": 1,
    }
    init_ai_workflow(request_data)


def test_offer_ticket_ai_workflow():
    request_data = {
        "conversation": [("user", "My monitor does not work.")],
        "ticket": False,
        "execution_count": config["workflow"]["max_count_of_troubleshootings"],
    }
    init_ai_workflow(request_data)


def test_further_questions_ai_workflow():
    request_data = {
        "conversation": [
            ("user", "My Monitor does not work."),
            ("ai", "Check the connections."),
            ("user", "Please create a ticket."),
        ],
        "ticket": True,
        "execution_count": 0,
    }
    init_ai_workflow(request_data)


def test_ticketcreation_ai_workflow():
    request_data = {
        "conversation": [
            ("user", "My Monitor does not work."),
            ("ai", "Check the connections."),
            ("user", "Please create a ticket."),
        ],
        "ticket": True,
        "execution_count": 1,
    }
    init_ai_workflow(request_data)


def init_ai_workflow(request_data):

    response = client.post(
        "/api/init_ai_workflow",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
        json=request_data,
    )

    assert response.status_code == 200, f"Unexpected response: {response.json()}"

    response_data = response.json()
    assert isinstance(response_data, dict)

    expected_keys = APIWorkflowResponse.__annotations__.keys()
    assert all(
        key in response_data for key in expected_keys
    ), f"Missing keys in response: {response_data.keys()}"

    assert isinstance(response_data["llm_output"], str | None)
    assert isinstance(response_data["ticket"], bool | None)
    assert isinstance(response_data["ticket_id"], int | None)


def test_ai_workflow_invalid_input():

    invalid_request_conversation = {
        "conversation": ["Invalid list"],  # Should be a list of tuples
        "ticket": False,
        "execution_count": 1,
    }

    response = client.post(
        "/api/init_ai_workflow",
        headers={"Authorization": f"Bearer {AZURE_USER_TESTING_ACCESS_TOKEN}"},
        json=invalid_request_conversation,
    )
    assert response.status_code == 422, f"Unexpected response: {response.json()}"
