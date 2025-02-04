from dataclasses import dataclass
from typing import Callable, List, Tuple
from vectordb import retrieve_documents
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langchain_core.messages.system import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
import uuid
import re
from custom_types import AppConfig, GraphState, WorkflowRequest, WorkflowResponse
from prompts import (
    query_prompt_with_context,
    grading_prompt,
    solvability_prompt,
    details_provided_prompt,
    further_questions_prompt,
    troubleshooting_prompt,
    ticket_issue_description_prompt,
    ticket_propose_solutions_prompt,
    ticket_summary_prompt,
)


@dataclass
class LangChainModel:
    initiate_workflow: Callable[[WorkflowRequest], WorkflowResponse]


# Initialize the LangChain model (this part can be copied from your notebook)
def initialize_langchain(config: AppConfig):

    llm = ChatOllama(model=config["ollama"]["llm"], temperature=0)

    history_aware_query_chain = query_prompt_with_context() | llm

    retrieval_grader_chain = grading_prompt() | llm

    web_search_tool = TavilySearchResults(k=3)

    solvability_chain = solvability_prompt() | llm

    details_provided_chain = details_provided_prompt() | llm

    troubleshooting_chain = troubleshooting_prompt() | llm

    ask_further_questions_chain = further_questions_prompt() | llm

    ticket_issue_description_chain = ticket_issue_description_prompt() | llm

    ticket_propose_solutions_chain = ticket_propose_solutions_prompt() | llm

    ticket_summary_chain = ticket_summary_prompt() | llm

    def remove_think_tags(response: str) -> str:
        # Regular expression to match <think>...</think> and remove them
        cleaned_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        return cleaned_response.strip()

    def retrieve(state: GraphState):
        input = state["input"]
        chat_history = state["chat_history"]
        query_prompt = state["query_prompt"]
        if query_prompt == "":
            query_prompt = history_aware_query_chain.invoke(
                {"input": input, "chat_history": chat_history}
            ).content
        query_prompt = remove_think_tags(query_prompt)
        print(query_prompt)
        retrieved_data = retrieve_documents(query_prompt)
        documents = []
        if retrieved_data:
            documents = [
                {
                    "role": "system",
                    "content": f"Reference document (Source: {doc['entity']['metadata']['source']}): {doc['entity']['text']}",
                }
                for doc in retrieved_data["documents"]
            ]
        return {"documents": documents, "query_prompt": query_prompt}

    def grade_documents(state: GraphState):
        input = state["input"]
        documents = state["documents"]
        chat_history = state["chat_history"]
        filtered_docs = []
        web_search = False
        for doc in documents:
            score = retrieval_grader_chain.invoke(
                {
                    "input": input,
                    "document": doc,
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

    def decide_web_search(state: GraphState):
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
            print(documents)
            return {"documents": documents}
        except Exception as e:
            print(f"Error in perform_web_search: {e}")
            raise

    def check_web_search_cause(state: GraphState):
        ticket = state["ticket"]
        if ticket:
            print("check_details_provided")
            return "check_details_provided"
        else:
            print("check_solvability")
            return "check_solvability"

    def check_solvability(state: GraphState):
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

    def check_details_provided(state: GraphState):
        input = state["input"]
        chat_history = state["chat_history"]
        details_provided = details_provided_chain.invoke(
            {
                "input": input,
                "chat_history": chat_history,
            },
        ).content
        details_provided = remove_think_tags(details_provided)
        return {"details_provided": details_provided}

    def decide_ask_further_questions_or_generate_ticket(state: GraphState):
        details_provided = state["details_provided"]
        if details_provided[0] == "1":
            print("generate_ticket")
            return "generate_ticket"
        else:
            print("further_questions")
            return "further_questions"

    def decide_generate_solution_or_offer_ticket(state: GraphState):
        solvable = state["solvable"]
        print(solvable[0])
        if solvable[0] == "1":
            print("generate_solution")
            return "generate_solution"
        else:
            print("offer_ticket")
            return "offer_ticket"

    def generate_solution(state: GraphState):
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
        text = """
            It seems the issue is more complex than what can be resolved through standard troubleshooting.
            To address this, I recommend escalating it to our specialized technical support team, who have the tools and expertise to handle more advanced problems.
            \nWe can generate a support ticket to document all details, including the troubleshooting steps we've already taken, and forward it to the appropriate team for further investigation.
            \nIf you'd like me to create a ticket on your behalf, please click the "Create Ticket" button below.
                    Before submitting the ticket, I may need to ask you a few additional questions to gather all necessary information for our support team."""
        return {"generation": text, "ticket": True}

    def further_questions(state: GraphState):
        input = state["input"]
        chat_history = state["chat_history"]
        documents = state["documents"]
        generation = ask_further_questions_chain.invoke(
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
            chat_history = state["chat_history"]
            documents = state["documents"]
            print("generate_issue_description")
            issue_description = ticket_issue_description_chain.invoke(
                {"chat_history": chat_history}
            ).content
            issue_description = remove_think_tags(issue_description)
            print("generate_proposed_solutions")
            proposed_solutions = ticket_propose_solutions_chain.invoke(
                {
                    "issue_description": [SystemMessage(issue_description)],
                    "documents": documents,
                }
            ).content
            proposed_solutions = remove_think_tags(proposed_solutions)
            generated_ticket = issue_description + "\n" + proposed_solutions
            print("generate_ticket_summary")
            ticket_summary = ticket_summary_chain.invoke(
                {"ticket": [SystemMessage(content=issue_description)]}
            ).content
            ticket_summary = remove_think_tags(ticket_summary)
            return {
                "ticket_content": generated_ticket,
                "ticket_summary": ticket_summary,
            }
        except Exception as e:
            print(f"ERROR in generate_ticket: {str(e)}")
            raise RuntimeError(f"Ticket generation failed: {str(e)}")

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

    def initiate_workflow(
        conversation: List[Tuple[str, str]], query_prompt: str, ticket: bool
    ) -> WorkflowResponse:
        try:
            input = [conversation.pop()]
            chat_history = conversation
            print("chat_history: ", chat_history)
            print("question: ", input)
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            state_dict = custom_graph.invoke(
                {
                    "input": input,
                    "chat_history": chat_history,
                    "query_prompt": query_prompt,
                    "ticket": ticket,
                },
                config,
            )
            response: WorkflowResponse = {
                "llm_output": state_dict.get("generation", ""),
                "ticket_content": state_dict.get("ticket_content", ""),
                "ticket_summary": state_dict.get("ticket_summary", ""),
                "query_prompt": state_dict.get("query_prompt", ""),
                "ticket": state_dict["ticket"],
            }
            print(response)
            return response
        except Exception as e:
            print(f"ERROR in initiate_workflow: {str(e)}")
            raise RuntimeError(f"Workflow failed: {str(e)}")

    return LangChainModel(initiate_workflow)
