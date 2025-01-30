from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from vectordb import initialize_milvus
from ai_system import initialize_langchain
from dotenv import load_dotenv

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


# Define an endpoint that accepts POST requests and sends the request to the LangChain model
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    conversation = data.get("conversation")

    if not conversation:
        return jsonify({"error": "No conversation provided"}), 400

    # Use the LangChain model to generate a response
    try:
        response = langchain_model.predict_custom_agent_local_answer(conversation)
    except:
        response = {
            "llm_output": "An error occured, trying to process your request. Please reload the page and try again.",
            "error": True,
        }

    # Return the result as a JSON response
    print(response)
    return jsonify({"response": response})


@app.route("/create_ticket", methods=["POST"])
def create_ticket():
    data = request.json
    conversation = data.get("conversation")
    queryPrompt = data.get("queryPrompt")

    if not conversation:
        return jsonify({"error": "No conversation provided"}), 400

    # Use the LangChain model to generate a response
    try:
        response = langchain_model.initiate_ticket_creation(conversation, queryPrompt)
    except:
        response = {
            "llm_output": "An error occured, trying to process your request. Please reload the page and try again.",
            "error": True,
        }

    import json

    attempts = 0
    if response["ticket"]:
        while attempts < 3:
            try:
                if attempts != 0:
                    response = langchain_model.initiate_ticket_creation(
                        conversation, queryPrompt
                    )

                # Escape the strings
                title = json.dumps(response["queryPrompt"])
                content = json.dumps(response["llm_output"]["ticket_content"])
                summary = json.dumps(response["llm_output"]["ticket_summary"])

                json_string = (
                    f'{{"title": {title}, "content": {content}, "summary": {summary}}}'
                )

                # Try to parse the escaped JSON string
                data = json.loads(json_string)
                print("Title: ", data["title"])
                print("Content: ", data["content"])
                print("Summary: ", data["summary"])
                # Create Ticket in DB
                ticket_id = 5  # Fetch ticket id from db

                response = {
                    "ticket_id": ticket_id,
                    "llm_output": content,
                }
                break  # Exit the loop on success

            except json.JSONDecodeError as e:
                print(f"JSON parsing error on attempt {attempts + 1}: {e}")
                attempts += 1
                response = {
                    "llm_output": "Error on ticket creation. Try again.",
                    "queryPrompt": queryPrompt,
                    "ticket": False,
                }

    print(response)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=False)
