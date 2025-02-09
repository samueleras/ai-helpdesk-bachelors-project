from pydantic import BaseModel
from typing import List, Tuple


class WorkflowRequestModel(BaseModel):
    conversation: List[Tuple[str, str]]
    query_prompt: str = ""
    ticket: bool
    excecution_count: int


class User(BaseModel):
    user_id: str
    user_name: str
    email: str
    group: str
