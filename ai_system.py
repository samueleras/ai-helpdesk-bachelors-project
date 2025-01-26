from dataclasses import dataclass
from vectordb import retrieve_documents
from langchain_ollama import ChatOllama
from typing import List
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from langchain_core.messages.system import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from prompts import queryPromptwithContext, grading_prompt


# Initialize the LangChain model (this part can be copied from your notebook)
def initialize_langchain(config):

    llm = ChatOllama(model=config["ollama"]["llm"])

    history_aware_query_chain = queryPromptwithContext() | llm

    retrieval_grader_chain = grading_prompt() | llm

    web_search_tool = TavilySearchResults(k=3)

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
        input = state["input"]
        chat_history = state["chat_history"]
        queryPrompt = state["queryPrompt"]
        if not queryPrompt:
            queryPrompt = history_aware_query_chain.invoke(
                {"input": input, "chat_history": chat_history}
            ).content
        documents = retrieve_documents(queryPrompt)
        return {"documents": documents, "queryPrompt": queryPrompt}

    def grade_documents(state):
        input = state["input"]
        documents = state["documents"]
        chat_history = state["chat_history"]
        filtered_docs = []
        web_search = False
        for doc in documents:
            score = retrieval_grader_chain.invoke(
                {
                    "input": input,
                    "documents": [SystemMessage(content=doc["entity"]["text"])],
                    "chat_history": chat_history,
                }
            ).content[0]
            print(score)
            if score == "1":
                print("Doc appended")
                filtered_docs.append(doc)
        if len(filtered_docs) < 2:
            web_search = True
        return {
            "documents": filtered_docs,
            "web_search": web_search,
        }

    def decide_web_search(state):
        web_search = state["web_search"]
        ticket = state["ticket"]
        if web_search:
            print("perform_web_search")
            return "perform_web_search"
        elif ticket:
            print("check_details_provided")
            return "check_details_provided"
        else:
            print("check_solvability")
            return "check_solvability"

    def perform_web_search(state):
        queryPrompt = state.get("queryPrompt")
        documents = state.get("documents")
        web_results = web_search_tool.invoke({"query": queryPrompt})
        documents.extend(
            {"entity": {"text": d["content"], "metadata": {"url": d["url"]}}}
            for d in web_results
        )
        return {"documents": documents}

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
