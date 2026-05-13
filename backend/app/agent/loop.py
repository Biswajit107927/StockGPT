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
from app.tools.market import get_sector_summary, list_sectors


# System prompt — sets the agent's persona and instructions.
# This is sent on every turn and shapes the agent's behavior.
SYSTEM_PROMPT = """You are a stock market research assistant for the S&P 500.

You have tools to query a database of S&P 500 companies. Use the tools to
answer questions accurately. Do not guess at facts the tools can provide.

When a user asks about a sector, use the get_sector_summary tool.
When you need to know which sectors exist, use list_sectors first.

Be concise and direct. State what you found, with relevant numbers.
"""

# Safety limit — never let the agent loop forever
MAX_ITERATIONS = 5

# The Gemini model to use. Flash is fast and cheap on the free tier.
MODEL_NAME = "gemini-2.5-flash"


def _tools_for_gemini() -> list[types.Tool]:
    """Build the Tool declarations Gemini needs to know about our functions.

    Gemini's SDK can introspect Python functions directly — it reads the
    function signature and docstring to build the schema. This is why
    well-typed parameters and thorough docstrings matter so much.
    """
    return [
        types.Tool(function_declarations=[
            # Pass the function objects; the SDK builds the schema
            {"name": "get_sector_summary",
             "description": get_sector_summary.__doc__,
             "parameters": {
                 "type": "object",
                 "properties": {
                     "sector_name": {
                         "type": "string",
                         "description": "The exact GICS sector name (case-sensitive)"
                     }
                 },
                 "required": ["sector_name"]
             }},
            {"name": "list_sectors",
             "description": list_sectors.__doc__,
             "parameters": {
                 "type": "object",
                 "properties": {},
             }},
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
