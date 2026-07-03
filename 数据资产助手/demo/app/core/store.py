from __future__ import annotations

from typing import Any


class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._confirms: dict[str, dict[str, Any]] = {}

    def save_task(self, task_id: str, state: dict[str, Any]) -> None:
        self._tasks[task_id] = state

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    def save_confirm(self, confirm_id: str, state: dict[str, Any]) -> None:
        self._confirms[confirm_id] = state

    def get_confirm(self, confirm_id: str) -> dict[str, Any] | None:
        return self._confirms.get(confirm_id)


store = InMemoryTaskStore()

