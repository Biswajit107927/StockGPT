import { useState } from "react";
import { useAskAgent } from "../hooks/useAskAgent";
import type { ToolCall } from "../types/agent";

/**
 * Chat interface for the agent.
 * - Input box for the user's question
 * - Submit button (also Enter key)
 * - Loading state while agent thinks
 * - Final answer display
 * - Expandable trace showing tool calls (the "agent observability" view)
 */
export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [showTrace, setShowTrace] = useState(false);
  const { mutate, data, isPending, error, reset } = useAskAgent();

  const handleSubmit = () => {
    const trimmed = question.trim();
    if (!trimmed || isPending) return;
    mutate({ question: trimmed });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex gap-2 mb-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the S&P 500... (Enter to submit, Shift+Enter for newline)"
          rows={2}
          disabled={isPending}
          className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
        />
        <button
          onClick={handleSubmit}
          disabled={isPending || !question.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-sm font-medium px-4 py-2 rounded-md transition-colors"
        >
          {isPending ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && (
        <div className="text-red-600 text-sm mb-3">
          Error: {error.message}
        </div>
      )}

      {data && (
        <div className="space-y-3">
          <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
            <div className="text-xs font-medium text-gray-500 uppercase mb-1">
              Answer
            </div>
            <div className="text-sm text-gray-900 whitespace-pre-wrap">
              {data.answer}
            </div>
          </div>

          <div>
            <button
              onClick={() => setShowTrace((v) => !v)}
              className="text-xs text-gray-500 hover:text-gray-900"
            >
              {showTrace ? "Hide" : "Show"} trace ({data.tool_calls.length} tool call{data.tool_calls.length === 1 ? "" : "s"}, {data.iterations} iteration{data.iterations === 1 ? "" : "s"})
            </button>
            {showTrace && (
              <div className="mt-2 space-y-2">
                {data.tool_calls.map((tc, i) => (
                  <TraceItem key={i} tc={tc} />
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => {
              reset();
              setQuestion("");
            }}
            className="text-xs text-gray-500 hover:text-gray-900"
          >
            Ask another question
          </button>
        </div>
      )}
    </div>
  );
}

function TraceItem({ tc }: { tc: ToolCall }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-md p-2 text-xs font-mono">
      <div className="text-gray-900 font-medium">
        {tc.name}({JSON.stringify(tc.args)})
      </div>
      {tc.error ? (
        <div className="text-red-600 mt-1">Error: {tc.error}</div>
      ) : (
        <div className="text-gray-600 mt-1 max-h-32 overflow-auto whitespace-pre-wrap">
          {JSON.stringify(tc.result, null, 2)}
        </div>
      )}
    </div>
  );
}
