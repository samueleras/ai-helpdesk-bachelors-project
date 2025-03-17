import logging
import json
from logging.handlers import RotatingFileHandler
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ai_system.vectordb import initialize_milvus, embed_summary
from ai_system.ai_system import initialize_langchain
from custom_types import WorkflowResponse, AppConfig
from dotenv import load_dotenv
from backend.pydantic_models import (
    NewTicketMessage,
    TicketAssignee,
    TicketFilter,
    TicketId,
    User,
    WorkflowRequestModel,
)
from utils import load_json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Annotated, Callable
import requests
import jwt
from backend.relationaldb import (
    assign_ticket,
    close_ticket,
    get_filtered_tickets,
    get_technicians,
    get_user_tickets,
    insert_ticket,
    insert_azure_user,
    insert_ticket_message,
    is_azure_user_in_db,
    get_ticket,
    reopen_ticket,
)

# Load environment variables
load_dotenv()

# Import necessary modules
app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load configuration
config: AppConfig = load_json(os.path.join(app_path, "config.json"))

# Init rotating file logger
file_handler = RotatingFileHandler("app.log", maxBytes=5000000, backupCount=5)
# Init console logger
console_handler = logging.StreamHandler()
# Logger config
log_level = getattr(
    logging,
    config.get("logging", {}).get("logging_level", "INFO").upper(),
    logging.INFO,
)
logging.basicConfig(
    level=log_level,
    handlers=[file_handler, console_handler],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add file handler to Uvicorn loggers
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.addHandler(file_handler)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("BACKEND " + __name__)

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


# Return user properties for frontend, only possible if token is valid => User authenticated
@app.get("/api/users/me")
async def read_users_me(user: Annotated[User, Depends(verify_token)]):
    try:
        if not is_azure_user_in_db(user.user_id, config):
            insert_azure_user(user.user_id, user.user_name, user.group, config)
    except Exception:
        raise HTTPException(status_code=500, detail="Storing user data failed")
    logger.info(f"User logged in and requested account details: {user}")
    return user


@app.post("/api/init_ai_workflow")
async def init_ai_workflow(
    user: Annotated[User, Depends(verify_token)], data: WorkflowRequestModel
):
    try:
        # Process input
        conversation = data.conversation
        ticket = data.ticket
        execution_count = data.execution_count

        # Use the LangChain model to generate a response or a ticket
        response: WorkflowResponse = await langchain_model.initiate_workflow_async(
            conversation, ticket, execution_count
        )
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Workflow execution failed")

    # If a ticket was generated, store it in the database and return the ID
    if response["ticket_content"]:
        attempts = 0
        while attempts < 3:
            try:
                if attempts > 0:
                    response: WorkflowResponse = (
                        await langchain_model.initiate_workflow_async(
                            conversation, ticket, execution_count
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
                    title, content, summary_vector, user.user_id, config
                )

                return {"llm_output": "", "ticket": True, "ticket_id": ticket_id}

            except Exception as e:
                logger.error(f"Error on attempt {attempts + 1}: {e}", exc_info=True)

            attempts += 1

        raise HTTPException(
            status_code=500, detail="Failed to process ticket after multiple attempts"
        )

    return {
        "llm_output": response["llm_output"],
        "ticket": response["ticket"],
        "ticket_id": None,
    }


@app.get("/api/ticket/{id}")
async def get_ticket_by_id(user: Annotated[User, Depends(verify_token)], id: int):
    try:
        ticket = get_ticket(id, user, config)
        # Only allow the request for the ticket author and technicians
        if user.user_name != ticket["author_name"]:
            if user.group != "technicians":
                logger.warning(
                    "Unauthorized ticket access. User is not the ticket author or part of the technicians group.",
                    exc_info=True,
                )
                raise PermissionError
        return ticket
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")


@app.post("/api/insert-ticket-message")
async def insert_ticket_message_db(
    user: Annotated[User, Depends(verify_token)],
    new_ticket_message: NewTicketMessage,
):
    try:
        insert_ticket_message(new_ticket_message, user, config)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to insert ticket message")


@app.post("/api/close-ticket")
async def close_ticket_db(
    user: Annotated[User, Depends(check_user_group("technicians"))],
    ticket: TicketId,
):
    try:
        close_ticket(ticket.ticket_id, config)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to close ticket")


@app.post("/api/reopen-ticket")
async def reopen_ticket_db(
    user: Annotated[User, Depends(check_user_group("technicians"))],
    ticket: TicketId,
):
    try:
        reopen_ticket(ticket.ticket_id, config)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reopen ticket")


@app.post("/api/tickets")
async def get_tickets(
    user: Annotated[User, Depends(check_user_group("technicians"))],
    filter_data: TicketFilter,
):
    try:
        tickets = get_filtered_tickets(filter_data, config)
        return tickets
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve tickets")


@app.post("/api/my-tickets")
async def get_my_tickets(
    user: Annotated[User, Depends(verify_token)],
    filter_data: TicketFilter,
):
    try:
        tickets = get_user_tickets(user, filter_data, config)
        return tickets
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve tickets")


@app.get("/api/technicians")
async def get_technicians_db(
    user: Annotated[User, Depends(check_user_group("technicians"))],
):
    try:
        technicians = get_technicians(config)
        return technicians
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve technicians")


@app.post("/api/assign-ticket")
async def assign_ticket_db(
    user: Annotated[User, Depends(check_user_group("technicians"))],
    ticket: TicketAssignee,
):
    try:
        assign_ticket(ticket, config)
        return
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to close ticket")


# Serve frontend files
app.mount(
    "/",
    StaticFiles(directory=os.path.join(app_path, "frontend", "dist"), html=True),
    name="static",
)
