from __future__ import annotations

from app.tools.data_loader import load_json


def get_data_standards(field_names: list[str]) -> list[dict]:
    standards = load_json("standards.json")["standards"]
    wanted = set(field_names)
    return [standard for standard in standards if standard["field"] in wanted]

