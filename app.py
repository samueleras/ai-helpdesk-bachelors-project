from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from vectordb import initialize_milvus
from ai_system import WorkflowResponse, initialize_langchain
from dotenv import load_dotenv
import json
from pydantic import BaseModel, ValidationError
from typing import List, Tuple

load_dotenv()


def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)


app_path = os.path.dirname(os.path.abspath(__file__))
config = load_config(os.path.join(app_path, "config.json"))
initialize_milvus(config)
langchain_model = initialize_langchain(config)

app = Flask(__name__)

CORS(app)


class WorkflowRequest(BaseModel):
    conversation: List[Tuple[str, str]]
    query_prompt: str = ""
    ticket: bool


# Define an endpoint that accepts POST requests and sends the request to the LangChain model
@app.route("/init_ai_workflow", methods=["POST"])
def init_ai_workflow():
    try:
        data = request.get_json()
        validated_data = WorkflowRequest(
            conversation=data["conversation"],
            query_prompt=data.get("query_prompt", ""),
            ticket=data["ticket"],
        )
    except ValidationError as e:
        return jsonify({"error": "Invalid request data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    conversation = validated_data.conversation
    query_prompt = validated_data.query_prompt
    ticket = validated_data.ticket

    # Use the LangChain model to generate a response or a ticket, depending on the ticket variable
    try:
        response: WorkflowResponse = langchain_model.initiate_workflow(
            conversation, query_prompt, ticket
        )
    except RuntimeError as e:
        return jsonify({"error": f"Workflow execution failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    # If a ticket was generated, store it in database and return ID
    if response["ticket_content"] != "":
        attempts = 0
        while attempts < 3:
            try:
                if attempts > 0:
                    response: WorkflowResponse = langchain_model.initiate_workflow(
                        conversation, query_prompt, ticket
                    )

                # Convert to JSON-safe format
                title = json.dumps(response["query_prompt"])
                content = json.dumps(response["ticket_content"])
                summary = json.dumps(response["ticket_summary"])

                # Simulate storing ticket in DB
                ticket_id = 5  # Replace with real DB logic

                response = {
                    "ticket_id": ticket_id,
                    "llm_output": content,
                }
                return jsonify({"response": response}, 200)

            except json.JSONDecodeError as e:
                print(f"JSON parsing error on attempt {attempts + 1}: {e}")
                attempts += 1

        # If all attempts fail, return an error
        return (
            jsonify({"error": "Failed to process ticket after multiple attempts"}),
            500,
        )

    # Return the result as a JSON response
    return jsonify({"response": response}, 200)


if __name__ == "__main__":
    app.run(debug=False)
