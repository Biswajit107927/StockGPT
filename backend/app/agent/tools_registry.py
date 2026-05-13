"""Registry of tools available to the agent.

Maps tool names (strings) to the actual Python functions.
This is the single source of truth — when we add new tools in later weeks,
they get registered here.

Gemini's tool use API works by name: when Gemini decides to call
"get_sector_summary", we look up that name here to find the actual function.
"""
from typing import Any, Callable

from app.tools.market import get_sector_summary, list_sectors


# Map of tool name -> Python function.
# The function name MUST match what Gemini sees in the tool declaration.
TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "get_sector_summary": get_sector_summary,
    "list_sectors": list_sectors,
}


def execute_tool(tool_name: str, tool_args: dict[str, Any]) -> Any:
    """Execute a tool by name with the given arguments.

    Args:
        tool_name: Name of the tool to execute (must be in TOOL_REGISTRY)
        tool_args: Dict of keyword arguments to pass to the tool function

    Returns:
        Whatever the tool function returns. Pydantic models will be converted
        to dicts via .model_dump() before being sent back to Gemini.

    Raises:
        ValueError: if tool_name is not in the registry
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(
            f"Unknown tool: {tool_name}. Available: {list(TOOL_REGISTRY.keys())}"
        )

    func = TOOL_REGISTRY[tool_name]
    result = func(**tool_args)

    # Pydantic models need to be serialized for the LLM to receive them as JSON
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result
