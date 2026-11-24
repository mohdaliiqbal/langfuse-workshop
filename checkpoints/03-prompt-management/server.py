"""FastAPI server for the Dad IT Support Agent.

One process serves the chat UI and the API on http://127.0.0.1:3333.
The TypeScript workshop splits Vite (3333) and Express (8787). This port
keeps the same URL and routes, without a Node toolchain.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.env import env
from app.models import ChatRequest
from app.support_agent import run_support_conversation
from app.support_data import DEFAULT_SUPPORT_CONTEXT

def _static_dir() -> Path:
    here = Path(__file__).resolve().parent
    candidate = here / "static"
    if candidate.is_dir():
        return candidate
    # Checkpoint snapshots live outside app/ until use_checkpoint.py copies them.
    return here.parents[1] / "app" / "static"


STATIC = _static_dir()
_langfuse = None


def _boot_langfuse():
    global _langfuse
    if not env.langfuse_configured:
        return None
    from langfuse import get_client

    _langfuse = get_client()
    return _langfuse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _boot_langfuse()
    yield
    if _langfuse is not None:
        _langfuse.flush()
        _langfuse.shutdown()


app = FastAPI(title="Dad IT Support Agent", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "provider": "openai",
        "tracingConfigured": env.langfuse_configured,
        "model": env.openai_model,
    }


@app.get("/api/support-context")
def support_context() -> dict:
    return DEFAULT_SUPPORT_CONTEXT


@app.post("/api/chat")
async def chat(request: Request) -> Response:
    try:
        payload = ChatRequest.model_validate(await request.json())
        result = run_support_conversation(payload)
    except Exception as exc:
        message = str(exc) if str(exc) else "Unknown server error"
        return Response(content=message, status_code=400, media_type="text/plain")
    return JSONResponse(result.model_dump(by_alias=True))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.server:app",
        host="127.0.0.1",
        port=env.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
