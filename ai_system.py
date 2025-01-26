from dataclasses import dataclass
from langchain_ollama import ChatOllama
from typing import List
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph


# Initialize the LangChain model (this part can be copied from your notebook)
def initialize_langchain(config):

    llm = ChatOllama(model=config["ollama"]["llm"])

    class GraphState(TypedDict):

        input: str
        chat_history: str
        queryPrompt: str
        generation: str
        web_search: bool
        solvable: str
        details_provided: str
        documents: List[dict]
        ticket: bool

    def retrieve(state):
        return

    def grade_documents(state):
        return

    def decide_web_search(state):
        return

    def perform_web_search(state):
        return

    def check_web_search_cause(state):
        return

    def check_solvability(state):
        return

    def check_details_provided(state):
        return

    def decide_ask_further_questions_or_generate_ticket(state):
        return

    def decide_generate_solution_or_offer_ticket(state):
        return

    def generate_solution(state):
        return

    def offer_ticket(state):
        return

    def further_questions(state):
        return

    def generate_ticket(state):
        return

    # Graph
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("perform_web_search", perform_web_search)  # web search
    workflow.add_node(
        "check_solvability", check_solvability
    )  # Check whether the issue can actually be solved by the user without administrative privileges
    workflow.add_node(
        "check_details_provided", check_details_provided
    )  # check if all necessary information is provided by user in order to generate a ticket
    workflow.add_node(
        "generate_solution", generate_solution
    )  # generate a proposed solution for the offer
    workflow.add_node(
        "offer_ticket", offer_ticket
    )  # Offer to create a ticket on behalf of the user
    workflow.add_node(
        "further_questions", further_questions
    )  # ask further questions to get all details from user
    workflow.add_node("generate_ticket", generate_ticket)  # create ticket

    # Build graph
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_web_search,
        {
            "perform_web_search": "perform_web_search",
            "check_solvability": "check_solvability",
            "check_details_provided": "check_details_provided",
        },
    )
    workflow.add_conditional_edges(
        "perform_web_search",
        check_web_search_cause,
        {
            "check_solvability": "check_solvability",
            "check_details_provided": "check_details_provided",
        },
    )
    workflow.add_conditional_edges(
        "check_solvability",
        decide_generate_solution_or_offer_ticket,
        {
            "generate_solution": "generate_solution",
            "offer_ticket": "offer_ticket",
        },
    )
    workflow.add_conditional_edges(
        "check_details_provided",
        decide_ask_further_questions_or_generate_ticket,
        {
            "further_questions": "further_questions",
            "generate_ticket": "generate_ticket",
        },
    )
    workflow.add_edge("offer_ticket", END)
    workflow.add_edge("generate_solution", END)
    workflow.add_edge("further_questions", END)
    workflow.add_edge("generate_ticket", END)

    custom_graph = workflow.compile()
