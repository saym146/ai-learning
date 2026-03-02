# Chat Loop With Tools (Non Agentic)

A lightweight, stateful Python client for interacting with Large Language Models (LLMs) via LangChain.

Unlike standard Agent executors, this script implements **manual tool calling and execution**. It explicitly manages conversation history, intercepts tool call requests from the model, executes the corresponding Python functions locally, and feeds the results back into the context window.

## How LLMs Communicate — Message Types

- When we talk to an LLM, we don't just send plain text — we send **structured messages**.
- Each message has a **role** (who is speaking) and **content** (what is being said).
- LangChain wraps these into specific message classes:

| Message Type | Role | Purpose |
|---|---|---|
| `SystemMessage` | System | Sets the behavior/personality of the LLM (system prompt) |
| `HumanMessage` | User | The question or input from the user |
| `AIMessage` | Assistant | The LLM's response — may include text, tool calls, or metadata |
| `ToolMessage` | Tool | The result returned after executing a tool |

- In **non-agentic mode**, we must manually build and manage this list of messages to maintain conversation context.
- The `AIMessage` is especially important here — we preserve it in the conversation so the LLM knows what it already said and what tool it requested.

### How a User Prompt Becomes a Chat Completion Request

```
User types: "What's the weather in Paris?"
        │
        ▼
┌──────────────────────────────────────────────┐
│         Chat Completion Request              │
│  ┌────────────────────────────────────────┐  │
│  │ messages: [                            │  │
│  │   { role: "system",    content: "..." }│  │
│  │   { role: "user",      content: "..." }│  │
│  │   { role: "assistant", content: "..." }│  │  ← conversation history
│  │   { role: "tool",      content: "..." }│  │
│  │   { role: "user",      content: "..." }│  │  ← latest user prompt
│  │ ]                                      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                ┌─────────────┐
                │     LLM     │
                └──────┬──────┘
                       │
                       ▼
              AIMessage (response)
```

- The user's prompt is **not sent alone** — it is wrapped as a `HumanMessage` and appended to the full conversation history.
- The entire `messages` list is sent to the LLM on every call.

### How the Code Builds the Conversation (`chat_loop_with_tools.py`)

The conversation is built as a list of dictionaries. Here is how each message type appears in the code:

**1. System Prompt** — set via `build_initial_conversation()`
```python
{"role": "system", "content": "You are a helpful weather assistant that replies in a concise manner. Not more than 20 words"}
```

**2. User Message** — appended in `chat_once()`
```python
conversation.append({"role": "user", "content": user_input})
```

**3. AI Response** — the raw `response` object from `model.invoke()` is appended directly
```python
response = model.invoke(conversation)
conversation.append(response)
```
- This preserves the full `AIMessage` including any `tool_calls` metadata.

**4. Tool Result** — appended after executing the tool manually
```python
tool_result = get_weather.invoke(tool_call)
conversation.append({"tool_call_id": tool_call['id'], "role": "tool", "content": tool_result.text})
```

**5. Final Assistant Reply** — after the tool result is processed by the LLM
```python
conversation.append({"role": "assistant", "content": text})
```

Each of these maps to a raw JSON structure sent to the LLM API:

**1. System**
```json
{
  "role": "system",
  "content": "You are a helpful weather assistant that replies in a concise manner. Not more than 20 words"
}
```

**2. User**
```json
{
  "role": "user",
  "content": "What's the weather in San Francisco?"
}
```

**3. AI (with tool call)**
```json
{
  "role": "assistant",
  "content": "",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\": \"San Francisco\"}"
      }
    }
  ]
}
```

**4. Tool**
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "It's sunny in San Francisco."
}
```

**5. Assistant (final reply)**
```json
{
  "role": "assistant",
  "content": "It's sunny in San Francisco."
}
```

> 📖 Reference: [LangChain Messages documentation](https://docs.langchain.com/oss/python/langchain/messages)

## Explicit Tool Call Handling (Non-Agentic Mode)

- In **agentic** mode, an agent automatically decides which tool to call and processes the result.
- In **non-agentic** mode (this script), **we handle tool calls manually**:
  1. The LLM responds with a `tool_call` in its `AIMessage`.
  2. Our code detects this and executes the matching Python function.
  3. The tool result is appended as a `ToolMessage` to the conversation.
  4. The updated conversation is sent back to the LLM for a final response.
- This gives **full control** over tool execution and message flow.



## Key Features

* **Stateful Conversation Management:** Maintains a continuous list of message dictionaries (system, user, assistant, and tool roles).
* **Automatic History Pruning:** Prevents context window overflow by automatically trimming older messages (configurable via `max_history`), while preserving the initial system prompt.
* **Manual Tool Execution Loop:** Explicitly handles `tool_calls` generated by the model, executes the tool (e.g., `get_weather`), and appends the `tool_result` back to the model to generate a final response.
* **Granular Token Tracking:** Extracts and logs input, output, and total token usage per API call (including the intermediate tool-resolution calls) using LangChain's metadata.

## Prerequisites

Ensure you have the following installed:

* Python 3.8+
* `langchain`
* `langchain-google-genai` (or your preferred provider's LangChain integration)

You will also need to set your API key as an environment variable:

```bash
export GOOGLE_API_KEY="your_api_key_here"