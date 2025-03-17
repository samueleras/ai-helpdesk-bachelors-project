import asyncio
from dataclasses import dataclass
import os
from typing import Callable, List, Tuple
from ai_system.vectordb import retrieve_documents_milvus
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langchain_core.messages.system import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
import uuid
import re
from utils import load_json
from custom_types import AppConfig, GraphState, WorkflowRequest, WorkflowResponse
from ai_system.prompts import (
    query_prompt_with_context,
    grading_prompt,
    solvability_prompt,
    ask_for_ticket_details_prompt,
    troubleshooting_prompt,
    ticket_issue_description_prompt,
    ticket_propose_solutions_prompt,
    ticket_summary_prompt,
    ticket_title_prompt,
)
import logging

logger = logging.getLogger("AI_SYSTEM " + __name__)


@dataclass
class LangChainModel:
    initiate_workflow_async: Callable[[WorkflowRequest], WorkflowResponse]


# Initialize the LangChain model (this part can be copied from your notebook)
def initialize_langchain(config: AppConfig):

    llm = ChatOllama(model=config["ollama"]["llm"], temperature=0)

    history_aware_query_chain = query_prompt_with_context() | llm

    retrieval_grader_chain = grading_prompt() | llm

    web_search_tool = TavilySearchResults(k=3)

    solvability_chain = solvability_prompt() | llm

    troubleshooting_chain = troubleshooting_prompt() | llm

    ask_for_ticket_details_chain = ask_for_ticket_details_prompt() | llm

    ticket_issue_description_chain = ticket_issue_description_prompt() | llm

    ticket_propose_solutions_chain = ticket_propose_solutions_prompt() | llm

    ticket_summary_chain = ticket_summary_prompt() | llm

    ticket_title_chain = ticket_title_prompt() | llm

    app_path = os.path.dirname(os.path.abspath(__file__))
    messages = load_json(os.path.join(app_path, "messages.json"))

    def remove_think_tags(response: str) -> str:
        # Regular expression to match <think>...</think> and remove them
        cleaned_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        return cleaned_response.strip()

    def generate_query_prompt(state: GraphState):
        logger.info(
            "generate_query_prompt",
        )
        input = state["input"]
        chat_history = state["chat_history"]
        query_prompt = history_aware_query_chain.invoke(
            {"input": input, "chat_history": chat_history}
        ).content
        query_prompt = remove_think_tags(query_prompt)
        return {"query_prompt": query_prompt}

    def retrieve_documents(state: GraphState):
        query_prompt = state["query_prompt"]
        logger.debug(
            f"query Prompt: {query_prompt}",
        )
        logger.info(
            "retrieve_documents",
        )
        retrieved_data = retrieve_documents_milvus(query_prompt)
        documents = []
        if retrieved_data:
            documents = [
                {
                    "role": "system",
                    "content": f"Reference document (Source: {doc['entity']['metadata']}): {doc['entity']['text']}",
                }
                for doc in retrieved_data
            ]
        return {"documents": documents}

    def grade_documents(state: GraphState):
        logger.info(
            "grade_documents",
        )
        input = state["input"]
        documents = state["documents"]
        chat_history = state["chat_history"]
        filtered_docs = []
        web_search = False
        for doc in documents:
            score = retrieval_grader_chain.invoke(
                {
                    "input": input,
                    "document": [doc],
                    "chat_history": chat_history,
                }
            ).content[0]
            logger.info(
                f"Document Grade: {score}",
            )
            if score == "1":
                logger.info(
                    "Doc appended",
                )
                filtered_docs.append(doc)
        if len(filtered_docs) < 2:
            web_search = True
        return {
            "documents": filtered_docs,
            "web_search": web_search,
        }

    def decide_web_search(state: GraphState):
        logger.info(
            "decide_web_search",
        )
        web_search = state["web_search"]
        ticket = state["ticket"]
        if web_search:
            logger.info(
                "perform_web_search",
            )
            return "perform_web_search"
        elif ticket:
            logger.info(
                "check_ticket_details_provided",
            )
            return "check_ticket_details_provided"
        else:
            logger.info(
                "check_solvability",
            )
            return "check_solvability"

    def perform_web_search(state: GraphState):
        query_prompt = state.get("query_prompt")
        documents = state.get("documents", [])
        try:
            web_results = web_search_tool.invoke({"query": query_prompt})
            documents.extend(
                {
                    "role": "system",
                    "content": f"Reference document (Source: {d["url"]}): {d["content"]}",
                }
                for d in web_results
            )
            return {"documents": documents}
        except Exception as e:
            logger.error(
                f"Error in perform_web_search: {e}",
                exc_info=True,
            )
            raise

    def decide_ticket_or_troubelshooting_path(state: GraphState):
        logger.info(
            "decide_ticket_or_troubelshooting_path",
        )
        ticket = state["ticket"]
        if ticket:
            logger.info(
                "check_ticket_details_provided",
            )
            return "check_ticket_details_provided"
        else:
            logger.info(
                "check_solvability",
            )
            return "check_solvability"

    def check_solvability(state: GraphState):
        excecution_count = state["excecution_count"]
        if excecution_count >= config["workflow"]["max_count_of_troubleshootings"]:
            logger.debug(
                f"Execition >= {config["workflow"]["max_count_of_troubleshootings"]}, therefore ticket will be proposed.",
            )
            return {"solvable": "0"}
        input = state["input"]
        chat_history = state["chat_history"]
        documents = state["documents"]
        solvable = solvability_chain.invoke(
            {
                "documents": documents,
                "input": input,
                "chat_history": chat_history,
            },
        ).content
        solvable = remove_think_tags(solvable)
        return {"solvable": solvable}

    def decide_issue_troubleshootable(state: GraphState):
        logger.info(
            "decide_issue_troubleshootable",
        )
        solvable = state["solvable"]
        if solvable[0] == "1":
            logger.info(
                "generate_troubleshooting_guide",
            )
            return "generate_troubleshooting_guide"
        else:
            logger.info(
                "offer_ticket",
            )
            return "offer_ticket"

    def check_ticket_details_provided(state: GraphState):
        excecution_count = state["excecution_count"]
        if excecution_count == 0:
            further_details = True
        else:
            further_details = False
        return {"further_details": further_details}

    def decide_ticket_details_provided(state: GraphState):
        logger.info(
            "decide_ticket_details_provided",
        )
        further_details = state["further_details"]
        if further_details:
            logger.info(
                "ask_for_ticket_details",
            )
            return "ask_for_ticket_details"
        else:
            logger.info(
                "generate_ticket",
            )
            return "generate_ticket"

    def generate_troubleshooting_guide(state: GraphState):
        input = state["input"]
        documents = state["documents"]
        chat_history = state["chat_history"]
        generation = troubleshooting_chain.invoke(
            {
                "documents": documents,
                "input": input,
                "chat_history": chat_history,
            }
        ).content
        generation = remove_think_tags(generation)
        return {"generation": generation}

    def offer_ticket(state: GraphState):
        return {
            "generation": messages["ticket_generation_message"],
            "ticket": True,
        }

    def ask_for_ticket_details(state: GraphState):
        input = state["input"]
        chat_history = state["chat_history"]
        documents = state["documents"]
        generation = ask_for_ticket_details_chain.invoke(
            {
                "documents": documents,
                "input": input,
                "chat_history": chat_history,
            }
        ).content
        generation = remove_think_tags(generation)
        return {"generation": generation}

    def generate_ticket(state: GraphState):
        try:
            input = state["input"]
            chat_history = state["chat_history"]
            documents = state["documents"]
            logger.info(
                "generate_issue_description",
            )
            issue_description = ticket_issue_description_chain.invoke(
                {
                    "chat_history": chat_history,
                    "input": input,
                }
            ).content
            issue_description = remove_think_tags(issue_description)
            logger.info(
                "generate_proposed_solutions",
            )
            proposed_solutions = ticket_propose_solutions_chain.invoke(
                {
                    "issue_description": [SystemMessage(issue_description)],
                    "documents": documents,
                }
            ).content
            proposed_solutions = remove_think_tags(proposed_solutions)
            generated_ticket = issue_description + "\n" + proposed_solutions
            logger.info(
                "generate_ticket_summary",
            )
            ticket_summary = ticket_summary_chain.invoke(
                {"ticket": [SystemMessage(content=issue_description)]}
            ).content
            ticket_summary = remove_think_tags(ticket_summary)
            logger.info(
                "generate_ticket_title",
            )
            ticket_title = ticket_title_chain.invoke(
                {"ticket": [SystemMessage(content=ticket_summary)]}
            ).content
            ticket_title = remove_think_tags(ticket_title)
            return {
                "ticket_content": generated_ticket,
                "ticket_summary": ticket_summary,
                "ticket_title": ticket_title,
            }
        except Exception as e:
            logger.error(
                f"Ticket generation failed: {str(e)}",
                exc_info=True,
            )
            raise RuntimeError(f"Ticket generation failed: {str(e)}") from e

    # Graph
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node(
        "generate_query_prompt", generate_query_prompt
    )  # generate query prompt
    workflow.add_node("retrieve_documents", retrieve_documents)  # retrieve
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("perform_web_search", perform_web_search)  # web search
    workflow.add_node(
        "check_solvability", check_solvability
    )  # Check whether the issue can actually be solved by the user without administrative privileges
    workflow.add_node(
        "check_ticket_details_provided",
        check_ticket_details_provided,
    )  # check if questions were already asked
    workflow.add_node(
        "generate_troubleshooting_guide", generate_troubleshooting_guide
    )  # generate a proposed solution for the offer
    workflow.add_node(
        "offer_ticket", offer_ticket
    )  # Offer to create a ticket on behalf of the user
    workflow.add_node(
        "ask_for_ticket_details", ask_for_ticket_details
    )  # ask further questions to get all details from user
    workflow.add_node("generate_ticket", generate_ticket)  # create ticket

    # Build graph
    workflow.add_edge(START, "generate_query_prompt")
    workflow.add_edge("generate_query_prompt", "retrieve_documents")
    workflow.add_edge("retrieve_documents", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_web_search,
        {
            "perform_web_search": "perform_web_search",
            "check_solvability": "check_solvability",
            "check_ticket_details_provided": "check_ticket_details_provided",
        },
    )
    workflow.add_conditional_edges(
        "perform_web_search",
        decide_ticket_or_troubelshooting_path,
        {
            "check_solvability": "check_solvability",
            "check_ticket_details_provided": "check_ticket_details_provided",
        },
    )
    workflow.add_conditional_edges(
        "check_solvability",
        decide_issue_troubleshootable,
        {
            "generate_troubleshooting_guide": "generate_troubleshooting_guide",
            "offer_ticket": "offer_ticket",
        },
    )
    workflow.add_conditional_edges(
        "check_ticket_details_provided",
        decide_ticket_details_provided,
        {
            "ask_for_ticket_details": "ask_for_ticket_details",
            "generate_ticket": "generate_ticket",
        },
    )
    workflow.add_edge("offer_ticket", END)
    workflow.add_edge("generate_troubleshooting_guide", END)
    workflow.add_edge("ask_for_ticket_details", END)
    workflow.add_edge("generate_ticket", END)

    custom_graph = workflow.compile()

    async def initiate_workflow_async(
        conversation: List[Tuple[str, str]],
        ticket: bool,
        excecution_count: int,
    ) -> WorkflowResponse:
        response = await asyncio.to_thread(
            initiate_workflow, conversation, ticket, excecution_count
        )
        return response

    def initiate_workflow(
        conversation: List[Tuple[str, str]],
        ticket: bool,
        excecution_count: int,
    ) -> WorkflowResponse:
        try:
            input = [conversation.pop()]
            chat_history = conversation
            logger.info(
                f"Initating AI workflow ...",
            )
            logger.debug(
                f"AI Workflow Parameters: Question: {input}; Chat_history: {chat_history}; Execution Count: {excecution_count}",
            )
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            state_dict = custom_graph.invoke(
                {
                    "input": input,
                    "chat_history": chat_history,
                    "ticket": ticket,
                    "excecution_count": excecution_count,
                },
                config,
            )
            response: WorkflowResponse = {
                "llm_output": state_dict.get("generation", ""),
                "ticket_title": state_dict.get("ticket_title", ""),
                "ticket_content": state_dict.get("ticket_content", ""),
                "ticket_summary": state_dict.get("ticket_summary", ""),
                "ticket": state_dict["ticket"],
            }
            logger.info(
                "Sucessfully executed AI workflow.",
            )
            logger.debug(
                f"AI Workflow Response: {response}",
            )
            return response
        except Exception as e:
            logger.error(
                f"Initiate workflow failed: {str(e)}",
                exc_info=True,
            )
            raise RuntimeError(f"ERROR in initiate_workflow: {str(e)}") from e

    return LangChainModel(initiate_workflow_async)
