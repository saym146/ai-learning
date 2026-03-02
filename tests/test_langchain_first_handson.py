import importlib.util
import sys
from types import SimpleNamespace
import pytest

# Dynamically import the module with a hyphen in the filename
MODULE_PATH = 'c:/Kajer/Projects/ai-learning/langchain-first-handson.py'
SPEC = importlib.util.spec_from_file_location('langchain_first_handson', MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class FakeResponse:
    def __init__(self, text: str):
        self.text = text


class FakeModel:
    def __init__(self, responder=None):
        # responder: Callable[[list[dict]], str]
        self.calls = []
        self._responder = responder or (lambda conv: f"echo: {conv[-1]['content']}")

    def invoke(self, conversation):
        self.calls.append([m.copy() for m in conversation])
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
    # Conversation should have user then assistant appended
    assert conversation[-2] == {"role": "user", "content": "Hello"}
    assert conversation[-1]["role"] == "assistant"
    assert conversation[-1]["content"] == out


def test_chat_once_handles_response_without_text_attr(monkeypatch, conversation):
    class Resp:
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
    # Each call includes growing conversation with system + turns
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
