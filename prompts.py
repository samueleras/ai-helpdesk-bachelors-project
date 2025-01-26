import json
import os
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def load_prompts(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)


app_path = os.path.dirname(os.path.abspath(__file__))
prompts = load_prompts(os.path.join(app_path, "prompts.json"))


def queryPromptwithContext():
    return ChatPromptTemplate(
        [
            (
                "system",
                prompts["queryPromptwithContext"]["default_prompt"],
            ),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("input"),
            (
                "system",
                prompts["queryPromptwithContext"]["followup_prompt"],
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
            MessagesPlaceholder("documents"),
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
