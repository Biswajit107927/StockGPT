"""Agent API: accept questions, return agent answers with trace."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
        # Catch any unexpected agent errors so the API stays responsive
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}",
        )
