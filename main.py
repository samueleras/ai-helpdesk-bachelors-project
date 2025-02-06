import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from vectordb import initialize_milvus
from ai_system import initialize_langchain
from custom_types import WorkflowResponse, AppConfig
from dotenv import load_dotenv
from pydantic_models import WorkflowRequestModel
from utils import load_json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Callable, Dict
import requests
import jwt

# Load environment variables
load_dotenv()

# Import necessary modules
app_path = os.path.dirname(os.path.abspath(__file__))

# Load configuration
config: AppConfig = load_json(os.path.join(app_path, "config.json"))
initialize_milvus(config)
langchain_model = initialize_langchain(config)

# Azure AD URLs and IDs
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me"
APP_USERS_GROUP_ID = os.getenv("APP_USERS_GROUP_ID")
TECHNICIANS_GROUP_ID = os.getenv("TECHNICIANS_GROUP_ID")

# OAuth2 Scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHORITY}/oauth2/v2.0/authorize", tokenUrl=TOKEN_URL
)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define static directory to serve frontend files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(app_path, "static"), html=True),
    name="frontend",
)


# Extract Current User and Groups
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(GRAPH_API_URL, headers=headers)
        user = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        groups_response = requests.get(f"{GRAPH_API_URL}/memberOf", headers=headers)
        groups_data = groups_response.json()

        if "value" in groups_data:
            user["groups"] = [group["id"] for group in groups_data["value"]]
        else:
            user["groups"] = []

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# Check user roles for authorisation
def check_user_role(required_group_id: str) -> Callable[[Dict], Dict]:
    def role_checker(user: Dict = Depends(get_current_user)) -> Dict:
        user_groups = user.get("groups", [])
        if required_group_id not in user_groups:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return user

    return role_checker


# Serve frontend files
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(app_path, "static", "index.html"))


# Return user properties for frontend, only possible if token is valid => User authenticated
@app.get("/users/me")
async def read_users_me(user: Dict = Depends(get_current_user)):
    return {
        "user_id": user.get("id"),
        "name": user.get("displayName"),
        "email": user.get("mail") or user.get("userPrincipalName"),
        "groups": user.get("groups", []),
    }


# Protected Route for Regular Users
@app.get("/user")
async def user_route(user: Dict = Depends(check_user_role(APP_USERS_GROUP_ID))):
    return {"message": "Welcome, regular user!", "user": user}


# Protected Route for Technicians
@app.get("/technician")
async def technician_route(user: Dict = Depends(check_user_role(TECHNICIANS_GROUP_ID))):
    return {"message": "Welcome, Technician!", "user": user}


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
