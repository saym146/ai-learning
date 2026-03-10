import os
import sys
from typing import Iterable, List, Dict, Optional
from langchain.chat_models import init_chat_model

# Ensure the project root is on sys.path so `tools` can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools import get_weather  # tool example import

SYSTEM_PROMPT = (
    "You are a helpful weather assistant that replies in a concise manner. Not more than 50 words"
)


def get_system_prompt() -> str:
    """Return the system prompt used to seed the chat conversation."""
    return SYSTEM_PROMPT


def init_model(model_name: str):
    """Initialize and return a chat model instance for the given provider/model name."""
    return init_chat_model(model_name)

def build_initial_conversation(system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
    """Create a new chat conversation list seeded with the system prompt."""
    prompt = system_prompt or get_system_prompt()
    return [{"role": "system", "content": prompt}]

def fetch_usage(response) -> dict:
    """
    Extracts token usage (input, output, total) from a LangChain response.
    Returns a dictionary with 0 as default for missing values.
    """
    # 1. Attempt to get standardized usage_metadata (LangChain standard)
    usage = getattr(response, "usage_metadata", {})
    
    # 2. Fallback to response_metadata (Provider specific)
    if not usage:
        usage = response.response_metadata.get("token_usage", {})

    return {
        "input": usage.get("input_tokens", usage.get("prompt_tokens", 0)),
        "output": usage.get("output_tokens", usage.get("completion_tokens", 0)),
        "total": usage.get("total_tokens", 0)
    }

def chat_once(model, conversation: List[Dict[str, str]], user_input: str, max_history: int = 3) -> Optional[str]:
    """
    Send a single user message to the model and append the assistant's reply.

    - Returns the assistant's reply text, or None if the input is empty/whitespace/None.
    - Mutates the provided `conversation` in-place by appending user and assistant messages.
    """
    # 1. Prune history before sending to save input tokens
    if len(conversation) > max_history:
        # Keep system prompt + last N messages
        conversation[:] = [conversation[0]] + conversation[-(max_history-1):]

    if user_input is None:
        return None
    user_input = user_input.strip()
    if user_input == "":
        return None

    text = ''
    conversation.append({"role": "user", "content": user_input})
    response = model.invoke(conversation)
    usage1 = fetch_usage(response)
    print(f"[Tokens] Input: {usage1["input"]} | Output: {usage1["output"]} | Total: {usage1["total"]}")

    conversation.append(response)
    # Some model responses expose `.text`; fall back to `str(response)` if absent
    for tool_call in response.tool_calls:
        # View tool calls made by the model
        print(f"Tool: {tool_call['name']}",end=" ")
        print(f"Args: {tool_call['args']}")
        if(tool_call['name'] == 'get_weather'):
            tool_result = get_weather.invoke(tool_call)
            conversation.append({"tool_call_id": tool_call['id'],"role": "tool", "content": tool_result.text})
            tool_response = model.invoke(conversation)
            usage2 = fetch_usage(tool_response)
            print(f"[Tokens] Input: {usage2["input"]} | Output: {usage2["output"]} | Total: {usage2["total"]}")
            text = getattr(tool_response, "text", str(tool_response))

    text = text if text != "" else getattr(response, "text", str(response))
    conversation.append({"role": "assistant", "content": text})
    return text




def run_chat_session(
    model,
    user_inputs: Iterable[str],
    system_prompt: Optional[str] = None,
) -> List[str]:
    """
    Run a multi-turn chat session over the provided iterable of user inputs.

    Returns a list of assistant replies (skips None/empty inputs).
    """
    conversation = build_initial_conversation(system_prompt)
    outputs: List[str] = []
    for ui in user_inputs:
        out = chat_once(model, conversation, ui)
        if out is not None:
            outputs.append(out)
    return outputs


def main() -> None:
    essential_model_name = "ollama:gpt-oss:20b"

    model = init_model(essential_model_name)
    model_with_tools = model.bind_tools([get_weather])
    conversation = build_initial_conversation()

    # Example tool reference (not used by the loop):
    # print(get_weather.run("San Francisco"))

    while True:
        user_question = input("Ask: ")
        out = chat_once(model_with_tools, conversation, user_question)
        if out is not None:
            print("AI: " + out)


if __name__ == "__main__":
    main()
