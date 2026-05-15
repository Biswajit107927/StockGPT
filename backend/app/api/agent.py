"""Agent API: accept questions, return agent answers with trace."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import traceback
import logging

logger = logging.getLogger(__name__)

from app.agent.loop import run_agent


router = APIRouter(prefix="/agent", tags=["agent"])


class AskRequest(BaseModel):
    """Incoming question to the agent."""

    question: str = Field(
        min_length=1,
        max_length=500,
        description="Natural-language question for the agent",
    )


class ToolCall(BaseModel):
    """Record of a single tool invocation during agent execution."""

    name: str
    args: dict[str, Any]
    result: Any | None = None
    error: str | None = None


class AskResponse(BaseModel):
    """Agent's answer and execution trace."""

    answer: str
    tool_calls: list[ToolCall]
    iterations: int


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """Send a question to the agent. Returns the answer and the trace.

    The trace shows which tools the agent called, with what arguments,
    and what they returned. Useful for the UI to display reasoning steps.
    """
    try:
        result = run_agent(request.question)
        return AskResponse(**result)
    except Exception as e:
        # Print full traceback to uvicorn logs for debugging
        logger.error("Agent failed on question: %r", request.question)
        logger.error("Traceback:\n%s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {type(e).__name__}: {str(e)}",
        )