import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from ai_system.vectordb import initialize_milvus, store_ticket_milvus, embed_summary
from ai_system import initialize_langchain
from custom_types import WorkflowResponse, AppConfig
from dotenv import load_dotenv
from pydantic_models import User, WorkflowRequestModel
from utils import load_json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Annotated, Callable
import requests
import jwt
from relationaldb import (
    insert_ticket,
    insert_azure_user,
    is_azure_user_in_db,
    get_ticket,
)

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
TOKEN_URL = (
    f"{AUTHORITY}/oauth2/v2.0/token"  # Where the frontend will fetch the token from
)
GRAPH_API_URL = (
    "https://graph.microsoft.com/v1.0/me"  # Backend verifys token and fetches user info
)
USERS_GROUP_ID = os.getenv("USERS_GROUP_ID")
TECHNICIANS_GROUP_ID = os.getenv("TECHNICIANS_GROUP_ID")

# OAuth2 Scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHORITY}/oauth2/v2.0/authorize", tokenUrl=TOKEN_URL
)  # Authorisation url is where users authenticate (login with azure account)

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


# Verify Token and Extract Current User and Groups
async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(GRAPH_API_URL, headers=headers)
        user_resp = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        groups_response = requests.get(f"{GRAPH_API_URL}/memberOf", headers=headers)
        groups_data = groups_response.json()

        group_ids = []
        # Convert groups in frontend understandable groupnames
        if "value" in groups_data:
            group_ids = [group["id"] for group in groups_data["value"]]

        # Translate groups into group names for frontend use
        group = ""
        if USERS_GROUP_ID in group_ids:
            group = "users"
        if TECHNICIANS_GROUP_ID in group_ids:
            group = "technicians"

        return User(
            user_id=user_resp.get("id"),
            user_name=user_resp.get("displayName"),
            email=user_resp.get("mail") or user_resp.get("userPrincipalName"),
            group=group,
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail="Error connecting to Microsoft Graph API"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# Check user roles for authorisation
def check_user_group(required_group_id: str) -> Callable[[User], User]:
    def role_checker(user: Annotated[User, Depends(verify_token)]) -> User:
        user_group = user.group
        if required_group_id != user_group:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return user

    return role_checker


# Serve frontend files
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(app_path, "static", "index.html"))


# Return user properties for frontend, only possible if token is valid => User authenticated
@app.get("/users/me")
async def read_users_me(user: Annotated[User, Depends(verify_token)]):
    try:
        if not is_azure_user_in_db(user.user_id, config):
            insert_azure_user(user.user_id, user.user_name, user.group, config)
    except Exception:
        raise HTTPException(status_code=500, detail="Storing user data failed")
    return user


# Protected Route for Regular Users
@app.get("/user")
async def user_route(user: Annotated[User, Depends(check_user_group("users"))]):
    return {"message": "Welcome, regular user!", "user": user}


# Protected Route for Technicians
@app.get("/technician")
async def technician_route(
    user: Annotated[User, Depends(check_user_group("technicians"))]
):
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
        response: WorkflowResponse = await langchain_model.initiate_workflow_async(
            conversation, query_prompt, ticket, excecution_count
        )
    except Exception as e:
        print(f"Workflow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Workflow execution failed")

    # If a ticket was generated, store it in the database and return the ID
    if response["ticket_content"]:
        attempts = 0
        while attempts < 3:
            try:
                if attempts > 0:
                    response: WorkflowResponse = (
                        await langchain_model.initiate_workflow_async(
                            conversation, query_prompt, ticket, excecution_count
                        )
                    )

                # Convert response fields to JSON-safe format
                title = json.dumps(response["ticket_title"])
                content = json.dumps(response["ticket_content"])
                summary = json.dumps(response["ticket_summary"])

                # Create embedding of the summary
                summary_vector = embed_summary(summary)

                # Store ticket in DB
                ticket_id = insert_ticket(
                    title, content, summary_vector, "test", config
                )

                store_ticket_milvus(ticket_id, summary_vector, title)

                return {"ticket_id": ticket_id, "ticket_content": content}

            except Exception as e:
                print(f"Error on attempt {attempts + 1}: {e}")

            attempts += 1

        raise HTTPException(
            status_code=500, detail="Failed to process ticket after multiple attempts"
        )

    return response


@app.get("/ticket/{id}")
async def get_ticket_by_id(user: Annotated[User, Depends(verify_token)], id: int):
    try:
        ticket = get_ticket(id, user, config)
        print(ticket)
        # Only allow the request for the ticket author and technicians
        if user.user_id != ticket["author_id"]:
            if user.group != "technician":
                print(
                    "Unauthorized ticket access. User is not the ticket author or part of the technicians group."
                )
                raise PermissionError
        return ticket
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")
