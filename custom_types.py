from typing import TypedDict, List, Tuple


class WorkflowRequest(TypedDict):
    conversation: List[Tuple[str, str]]
    query_prompt: str
    ticket: bool


class WorkflowResponse(TypedDict):
    llm_output: str
    ticket_content: str
    ticket_summary: str
    query_prompt: str
    ticket: bool


class GraphState(TypedDict):
    input: str
    chat_history: str
    query_prompt: str = ""
    generation: str = ""
    web_search: bool
    solvable: str
    details_provided: str
    documents: List[dict]
    ticket: bool
    ticket_content: str = ""
    ticket_summary: str = ""
