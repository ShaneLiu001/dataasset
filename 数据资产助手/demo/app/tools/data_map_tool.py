from __future__ import annotations

from app.tools.data_loader import load_json


def search_data_map(table_name: str) -> list[dict]:
    assets = load_json("assets.json")["assets"]
    return [asset for asset in assets if asset["table_name"] == table_name]


def get_asset_detail(asset_id: str) -> dict | None:
    assets = load_json("assets.json")["assets"]
    return next((asset for asset in assets if asset["asset_id"] == asset_id), None)

