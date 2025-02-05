import json
from typing import Any


def load_json(json_file: str) -> dict[str, Any]:
    with open(json_file, "r") as file:
        return json.load(file)
