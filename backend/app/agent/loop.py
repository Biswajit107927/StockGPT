"""Agent loop using Gemini's tool use API.

The agent takes a natural-language question, loops through calls to Gemini
with tool use enabled, executes any tools Gemini requests, and returns a
final synthesized answer.
"""
from typing import Any

from google import genai
from google.genai import types

from app.agent.tools_registry import TOOL_REGISTRY, execute_tool
from app.config import settings
from app.tools.market import (
    get_sector_summary,
    list_sectors,
    search_companies_by_name,
    get_ticker_details,
    compare_sectors,
)


# System prompt — sets the agent's persona and instructions.
# This is sent on every turn and shapes the agent's behavior.
SYSTEM_PROMPT = """You are a stock market research assistant for the S&P 500.

You have tools to query a database of S&P 500 companies. Use the tools to
answer questions accurately. Do not guess at facts the tools can provide.

Available tools:
- get_sector_summary: count and sample tickers for a specific sector
- list_sectors: list of all valid sector names
- search_companies_by_name: find companies by partial name match
- get_ticker_details: look up info on a specific ticker
- compare_sectors: side-by-side counts for multiple sectors

Strategy hints:
- If a user asks about a specific ticker, use get_ticker_details.
- If they ask to find companies by name, use search_companies_by_name.
- If they ask "which sector is bigger", use compare_sectors (not multiple
  separate calls to get_sector_summary).
- If you're unsure about a sector name, call list_sectors first.

Be concise and direct. State what you found, with relevant numbers.
"""

# Safety limit — never let the agent loop forever
MAX_ITERATIONS = 5

# The Gemini model to use. Flash is fast and cheap on the free tier.
MODEL_NAME = "gemini-2.5-flash"


def _tools_for_gemini() -> list[types.Tool]:
    """Build the Tool declarations Gemini needs to know about our functions.

    Each declaration tells Gemini: tool name, what it does (docstring),
    and what parameters it accepts (JSON Schema). Gemini reads these on
    every call to decide which tools to invoke.
    """
    return [
        types.Tool(function_declarations=[
            {
                "name": "get_sector_summary",
                "description": get_sector_summary.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sector_name": {
                            "type": "string",
                            "description": "The exact GICS sector name (case-sensitive)",
                        }
                    },
                    "required": ["sector_name"],
                },
            },
            {
                "name": "list_sectors",
                "description": list_sectors.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "search_companies_by_name",
                "description": search_companies_by_name.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name_fragment": {
                            "type": "string",
                            "description": "Substring to search for in company names (case-insensitive)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default 20, max 100)",
                        },
                    },
                    "required": ["name_fragment"],
                },
            },
            {
                "name": "get_ticker_details",
                "description": get_ticker_details.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Ticker symbol to look up (e.g., AAPL, NVDA)",
                        }
                    },
                    "required": ["ticker"],
                },
            },
            {
                "name": "compare_sectors",
                "description": compare_sectors.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sector_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of exact GICS sector names to compare (case-sensitive)",
                        }
                    },
                    "required": ["sector_names"],
                },
            },
        ])
    ]


def run_agent(question: str) -> dict[str, Any]:
    """Run the agent loop on a question. Returns answer + trace.

    Args:
        question: User's natural-language question

    Returns:
        Dict with:
          - answer: final text response from the agent
          - tool_calls: list of {name, args, result} for each tool invocation
          - iterations: how many loop turns it took
    """
    client = genai.Client(api_key=settings.gemini_api_key)

    # Conversation history — grows as we loop
    contents: list[Any] = [
        types.Content(role="user", parts=[types.Part(text=question)])
    ]

    trace = {
        "answer": "",
        "tool_calls": [],
        "iterations": 0,
    }

    for iteration in range(MAX_ITERATIONS):
        trace["iterations"] = iteration + 1

        # Call Gemini with the conversation so far and available tools
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=_tools_for_gemini(),
            ),
        )

        # Did Gemini return a tool call or a final text answer?
        candidate = response.candidates[0]
        parts = candidate.content.parts or []

        # Check for function calls in the response
        function_calls = [p.function_call for p in parts if p.function_call]

        if function_calls:
            # Append Gemini's tool-call request to the conversation
            contents.append(candidate.content)

            # Execute each function call and append the result
            for fc in function_calls:
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}

                try:
                    result = execute_tool(tool_name, tool_args)
                    trace["tool_calls"].append({
                        "name": tool_name,
                        "args": tool_args,
                        "result": result,
                    })
                except Exception as e:
                    result = {"error": str(e)}
                    trace["tool_calls"].append({
                        "name": tool_name,
                        "args": tool_args,
                        "error": str(e),
                    })

                # Append the tool result back into the conversation
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_function_response(
                            name=tool_name,
                            response={"result": result},
                        )],
                    )
                )

            # Loop back: Gemini will see the result and either call more tools
            # or give a final answer
            continue

        # No tool calls — Gemini has produced a final answer
        text_parts = [p.text for p in parts if p.text]
        trace["answer"] = "\n".join(text_parts)
        return trace

    # If we exit the loop without an answer, we hit the iteration limit
    trace["answer"] = "Agent exceeded maximum iterations without producing an answer."
    return trace
