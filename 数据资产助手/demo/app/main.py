from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.assistant import router as assistant_router
from app.ui import INDEX_HTML

app = FastAPI(title="Data Asset Assistant Demo", version="0.1.0")
app.include_router(assistant_router)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
