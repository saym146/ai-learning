import importlib.util
import sys
import os
from types import SimpleNamespace
import pytest

# Ensure the project root is on sys.path so `from tools import ...` works at import time
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Dynamically import the module
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'langchain', 'non-agentic', 'chat_loop_with_tools.py')
SPEC = importlib.util.spec_from_file_location('chat_loop_with_tools', MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class FakeResponse:
    """Mimics a LangChain AIMessage with text, usage_metadata, and tool_calls."""
    def __init__(self, text: str, tool_calls=None):
        self.text = text
        self.tool_calls = tool_calls or []
        self.usage_metadata = {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
        }

    def copy(self):
        return {"role": "assistant", "content": self.text}


class FakeModel:
    def __init__(self, responder=None):
        # responder: Callable[[list], str]
        self.calls = []
        self._responder = responder or (lambda conv: f"echo: {conv[-1]['content']}")

    def invoke(self, conversation):
        self.calls.append(list(conversation))
        return FakeResponse(self._responder(conversation))


@pytest.fixture()
def conversation():
    return module.build_initial_conversation()


def test_get_system_prompt_non_empty():
    assert isinstance(module.get_system_prompt(), str)
    assert len(module.get_system_prompt()) > 0


def test_build_initial_conversation_contains_system():
    conv = module.build_initial_conversation()
    assert isinstance(conv, list)
    assert conv[0]['role'] == 'system'
    assert module.get_system_prompt() in conv[0]['content']


def test_chat_once_ignores_none_and_empty(conversation):
    m = FakeModel()
    assert module.chat_once(m, conversation, None) is None
    assert module.chat_once(m, conversation, '   ') is None
    # No user/assistant messages appended for ignored inputs
    assert len(conversation) == 1  # only system message


def test_chat_once_appends_and_returns_text(conversation):
    m = FakeModel()
    out = module.chat_once(m, conversation, 'Hello')
    assert out is not None and out.startswith('echo: ')
    # Conversation: system, user, response (raw), assistant
    assert conversation[1] == {"role": "user", "content": "Hello"}
    assert conversation[-1]["role"] == "assistant"
    assert conversation[-1]["content"] == out


def test_chat_once_handles_response_without_text_attr(monkeypatch, conversation):
    class Resp:
        tool_calls = []
        usage_metadata = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        def __str__(self):
            return 'fallback to str'
    class ModelNoText(FakeModel):
        def invoke(self, c):
            return Resp()
    m = ModelNoText()
    out = module.chat_once(m, conversation, 'Hello')
    assert out == 'fallback to str'


def test_run_chat_session_multiple_turns_and_skips_empty():
    m = FakeModel()
    outs = module.run_chat_session(m, [None, '   ', 'Hi', 'There'])
    assert outs == ['echo: Hi', 'echo: There']
    # Ensure model was invoked exactly for non-empty inputs
    assert len(m.calls) == 2
    # First call should start with the system message
    assert m.calls[0][0]['role'] == 'system'


def test_init_model_not_called_in_tests(monkeypatch):
    # Ensure we do not accidentally hit external API during tests
    called = {'v': False}
    def fake_init(name):
        called['v'] = True
        return FakeModel()
    monkeypatch.setattr(module, 'init_chat_model', fake_init, raising=False)
    # Call our wrapper which should call the patched function
    m = module.init_model('x:y')
    assert called['v'] is True
    assert isinstance(m, FakeModel)
