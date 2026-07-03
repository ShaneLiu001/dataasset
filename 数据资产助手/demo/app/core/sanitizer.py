from __future__ import annotations

import re
from typing import Any

SENSITIVE_KEYS = {
    "access_token",
    "token",
    "password",
    "passwd",
    "secret",
    "connection_string",
    "jdbc_url",
    "dsn",
}

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
ID_CARD_RE = re.compile(r"(?<!\d)(\d{6})(\d{8})(\d{3}[\dXx])(?!\d)")


def mask_text(value: str) -> str:
    value = PHONE_RE.sub(lambda m: m.group(1)[:3] + "****" + m.group(1)[-4:], value)
    value = ID_CARD_RE.sub(lambda m: m.group(1) + "********" + m.group(3), value)
    return value


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "***"
            else:
                sanitized[key] = sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return mask_text(value)
    return value

