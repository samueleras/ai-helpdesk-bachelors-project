from datetime import datetime
from typing import TypedDict, List, Tuple


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


class MySqlConfig(TypedDict):
    user: str
    host: str
    database: str


class AppConfig(TypedDict):
    ollama: OllamaConfig
    workflow: WorkflowConfig
    milvus: MilvusConfig
    mysql: MySqlConfig


class WorkflowRequest(TypedDict):
    conversation: List[Tuple[str, str]]
    ticket: bool


class WorkflowResponse(TypedDict):
    llm_output: str
    ticket_title: str
    ticket_content: str
    ticket_summary: str
    query_prompt: str
    ticket: bool


class GraphState(TypedDict):
    input: str
    chat_history: str
    query_prompt: str = ""
    documents: List[dict]
    web_search: bool
    solvable: str
    further_details: bool = False
    generation: str = ""
    ticket_content: str = ""
    ticket_summary: str = ""
    ticket_title: str = ""
    ticket: bool
    excecution_count: int


class SimilarTicket(TypedDict):
    ticket_id: int
    title: str


class TicketMessage(TypedDict):
    message: str
    author_name: str
    group: str
    created_at: datetime


class Ticket(TypedDict):
    ticket_id: int
    title: str
    content: str
    creation_date: datetime
    closed_date: datetime | None
    author_name: str
    assignee_name: str | None
    similar_tickets: List[SimilarTicket]
    ticket_messages: List[TicketMessage]


class Technician(TypedDict):
    user_id: str
    user_name: str
