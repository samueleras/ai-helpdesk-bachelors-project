import os
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils import load_json

app_path = os.path.dirname(os.path.abspath(__file__))
prompts = load_json(os.path.join(app_path, "prompts.json"))


def query_prompt_with_context():
    return ChatPromptTemplate(
        [
            (
                "system",
                prompts["query_prompt_with_context"]["default_prompt"],
            ),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["query_prompt_with_context"]["followup_prompt"],
            ),
        ]
    )


def grading_prompt():
    return ChatPromptTemplate(
        [
            (
                "system",
                prompts["grading_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("document"),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["grading_prompt"]["followup_prompt"],
            ),
        ]
    )


def solvability_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["solvability_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("documents"),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            ("system", prompts["solvability_prompt"]["followup_prompt"]),
        ]
    )


def details_provided_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["details_provided_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            ("system", prompts["details_provided_prompt"]["followup_prompt"]),
        ]
    )


def troubleshooting_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["troubleshooting_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("documents"),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["troubleshooting_prompt"]["followup_prompt"],
            ),
        ]
    )


def ask_for_ticket_details_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["further_questions_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("documents"),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["further_questions_prompt"]["followup_prompt"],
            ),
        ]
    )


def ticket_issue_description_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["ticket_issue_description_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["ticket_issue_description_prompt"]["followup_prompt"],
            ),
        ]
    )


def ticket_propose_solutions_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["ticket_propose_solutions_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("issue_description"),
            MessagesPlaceholder("documents"),
            (
                "system",
                prompts["ticket_propose_solutions_prompt"]["followup_prompt"],
            ),
        ]
    )


def ticket_summary_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["ticket_summary_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("ticket"),
        ]
    )


def ticket_title_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompts["ticket_title_prompt"]["default_prompt"],
            ),
            MessagesPlaceholder("ticket"),
        ]
    )
