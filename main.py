import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from vectordb import initialize_milvus
from ai_system import initialize_langchain
from custom_types import WorkflowResponse, AppConfig
from dotenv import load_dotenv
from pydantic_models import WorkflowRequestModel
from utils import load_json

# Load environment variables
load_dotenv()

# Import necessary modules
app_path = os.path.dirname(os.path.abspath(__file__))

# Load configuration
config: AppConfig = load_json(os.path.join(app_path, "config.json"))
initialize_milvus(config)
langchain_model = initialize_langchain(config)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/",
    StaticFiles(directory=os.path.join(app_path, "static"), html=True),
    name="frontend",
)


@app.post("/init_ai_workflow")
async def init_ai_workflow(data: WorkflowRequestModel):
    try:
        # Process input
        conversation = data.conversation
        query_prompt = data.query_prompt
        ticket = data.ticket
        excecution_count = data.excecution_count

        # Use the LangChain model to generate a response or a ticket
        response: WorkflowResponse = await langchain_model.initiate_workflow(
            conversation, query_prompt, ticket, excecution_count
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500, detail=f"Workflow execution failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # If a ticket was generated, store it in the database and return the ID
    if response.ticket_content:
        attempts = 0
        while attempts < 3:
            try:
                if attempts > 0:
                    response: WorkflowResponse = (
                        await langchain_model.initiate_workflow(
                            conversation, query_prompt, ticket, excecution_count
                        )
                    )

                # Convert response fields to JSON-safe format
                title = json.dumps(response.query_prompt)
                content = json.dumps(response.ticket_content)
                summary = json.dumps(response.ticket_summary)

                # Simulate storing ticket in DB
                ticket_id = 5  # Replace with actual database logic

                return {"ticket_id": ticket_id, "ticket_content": content}
            except json.JSONDecodeError as e:
                print(f"JSON parsing error on attempt {attempts + 1}: {e}")
                attempts += 1

        raise HTTPException(
            status_code=500, detail="Failed to process ticket after multiple attempts"
        )

    # Return the result
    return response
