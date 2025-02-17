from pydantic import BaseModel
from typing import List, Optional, Tuple


class WorkflowRequestModel(BaseModel):
    conversation: List[Tuple[str, str]]
    query_prompt: str = ""
    ticket: bool
    excecution_count: int


class User(BaseModel):
    user_id: str
    user_name: str
    group: str


class TicketFilter(BaseModel):
    assignee_id: Optional[str] = None
