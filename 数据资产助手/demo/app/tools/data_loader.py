from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app.core.config import MOCK_DATA_DIR


@lru_cache
def load_json(filename: str) -> dict[str, Any]:
    with (MOCK_DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)

