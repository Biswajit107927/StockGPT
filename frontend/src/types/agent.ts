// Mirrors the backend's Pydantic models in app/api/agent.py

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: unknown;
  error?: string | null;
}

export interface AskResponse {
  answer: string;
  tool_calls: ToolCall[];
  iterations: number;
}

export interface AskRequest {
  question: string;
}
