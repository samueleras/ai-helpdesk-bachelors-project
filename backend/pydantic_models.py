from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Tuple


class WorkflowRequestModel(BaseModel):
    conversation: List[Tuple[str, str]]
    ticket: bool
    execution_count: int


class User(BaseModel):
    user_id: str
    user_name: str
    group: str


class TicketFilter(BaseModel):
    page: Optional[int] = None
    page_size: Optional[int] = None
    assignee_id: Optional[str] = None
    closed: Optional[bool] = None
    order: Optional[str] = None
    search: Optional[str] = None


class NewTicketMessage(BaseModel):
    ticket_id: int
    message: str
    created_at: datetime


class TicketId(BaseModel):
    ticket_id: int


class TicketAssignee(BaseModel):
    ticket_id: int
    assignee_id: str
