import os
from fastapi import FastAPI
from vectordb import initialize_milvus
from ai_system import initialize_langchain
from custom_types import WorkflowResponse, AppConfig
from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_models import WorkflowRequestModel
from utils import load_json

# Load environment variables
load_dotenv()

# Import necessary modules
app_path = os.path.dirname(os.path.abspath(__file__))

# Load configuration
config = load_json(os.path.join(app_path, "config.json"))
initialize_milvus(config)
langchain_model = initialize_langchain(config)

# Initialize FastAPI app
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
