from __future__ import annotations

from app.tools.data_loader import load_json


def get_user_common_context(user_id: str) -> dict:
    users = load_json("user_preferences.json")["users"]
    return users.get(
        user_id,
        {
            "space_id": "space_default",
            "space_name": "默认数据空间",
            "project_id": "project_default",
            "project_name": "默认项目",
            "dev_account": f"dev_{user_id}",
        },
    )

