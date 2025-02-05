from datetime import datetime
from typing import Optional, TypedDict, List, Tuple


class OllamaConfig(TypedDict):
    llm: str
    embedding_model: str


class WorkflowConfig(TypedDict):
    max_count_of_troubleshootings: int


class MilvusConfig(TypedDict):
    host: str
    user: str
    metric_type_rag: str
    index_type_rag: str
    metric_type_tickets: str
    index_type_tickets: str
    number_of_retrieved_documents: int
    rag_documents_folder_absolute_path: str


class AppConfig(TypedDict):
    ollama: OllamaConfig
    workflow: WorkflowConfig
    milvus: MilvusConfig


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
    further_questions: bool = False
    documents: List[dict]
    ticket: bool
    ticket_content: str = ""
    ticket_summary: str = ""
    excecution_count: int


class Ticket(TypedDict):
    ticket_id: int
    title: str
    content: str
    summary: Optional[str]
    creation_date: datetime
    closed_date: Optional[datetime]
    user_id: str
    assignee_id: Optional[str]


class TicketConversation(TypedDict):
    message_id: int
    ticket_id: int
    author_id: str
    message: str
    created_at: datetime
