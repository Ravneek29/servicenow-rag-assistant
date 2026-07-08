from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.qa import answer_question

router = APIRouter(prefix="/api", tags=["chat"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


@router.post("/ask")
def ask(request: AskRequest):
    try:
        return answer_question(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(502, f"Answer generation failed: {exc}")
