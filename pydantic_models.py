from pydantic import BaseModel
from typing import List, Tuple


class WorkflowRequestModel(BaseModel):
    conversation: List[Tuple[str, str]]
    query_prompt: str = ""
    ticket: bool
