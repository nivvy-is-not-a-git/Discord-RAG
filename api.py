import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import buffer
import vector_search

load_dotenv()

app = FastAPI(title="Discord RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class AskResult(BaseModel):
    text: str
    link: Optional[str] = None


class AskResponse(BaseModel):
    results: list[AskResult]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    try:
        results = await run_in_threadpool(vector_search.vsearch, payload.question)
    except Exception:
        raise HTTPException(status_code=502, detail="search backend unavailable")

    ask_results = []
    for chunk_text, message_ids in results:
        link = await run_in_threadpool(buffer.get_discord_link, message_ids[0]) if message_ids else None
        ask_results.append(AskResult(text=chunk_text, link=link))
    return AskResponse(results=ask_results)
