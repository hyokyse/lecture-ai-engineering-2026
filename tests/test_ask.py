import sys
from types import SimpleNamespace

import pytest

from app import ask as ask_module


def test_main_uses_default_temperature(monkeypatch, capsys):
    received = {"questions": [], "config": None, "client_closed": False}

    class FakeChat:
        def send_message(self, question):
            assert not received["client_closed"]
            received["questions"].append(question)
            return SimpleNamespace(usage_metadata=None, text=f"回答: {question}")

    class FakeChats:
        def create(self, *, model, config):
            received["model"] = model
            received["config"] = config
            return FakeChat()

    class FakeClient:
        def __init__(self, api_key):
            self.chats = FakeChats()

        def close(self):
            received["client_closed"] = True

    monkeypatch.setattr(sys, "argv", ["app.ask", "LoRAとは？"])
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    inputs = iter(["さらに質問", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    clock = iter([10.0, 10.25, 20.0, 21.0])
    monkeypatch.setattr(ask_module.time, "perf_counter", lambda: next(clock))

    ask_module.main()

    assert received["questions"] == ["LoRAとは？", "さらに質問"]
    assert received["config"].temperature == 1.0
    assert received["client_closed"]
    output = capsys.readouterr().out
    assert output.count("[RT]") == 2
    assert "[RT] 0.25秒" in output
    assert "[RT] 1.00秒" in output


def test_main_keeps_cli_temperature_for_followup_questions(monkeypatch):
    received = {"temperatures": [], "questions": []}

    class FakeChat:
        def send_message(self, question):
            received["questions"].append(question)
            return SimpleNamespace(usage_metadata=None, text="回答")

    chat = FakeChat()
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初", "0.7"])
    class FakeClient:
        def __init__(self, api_key):
            pass

        def close(self):
            pass

    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)

    def fake_create_chat(client, temperature):
        received["temperatures"].append(temperature)
        return chat

    monkeypatch.setattr(ask_module, "create_chat", fake_create_chat)
    inputs = iter(["続き", "/quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    ask_module.main()

    assert received["temperatures"] == [0.7]
    assert received["questions"] == ["最初", "続き"]


@pytest.mark.parametrize("exit_command", ["/exit", "/quit"])
def test_main_exits_on_exit_commands(monkeypatch, exit_command):
    monkeypatch.setattr(sys, "argv", ["app.ask", "質問"])
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    class FakeChat:
        def send_message(self, question):
            return SimpleNamespace(usage_metadata=None, text="回答")

    class FakeChats:
        def create(self, *, model, config):
            return FakeChat()

    class FakeClient:
        def __init__(self, api_key):
            self.chats = FakeChats()

        def close(self):
            pass

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr("builtins.input", lambda _: exit_command)

    ask_module.main()


@pytest.mark.parametrize("temperature", ["abc", "-0.1", "2.1"])
def test_main_rejects_invalid_temperature(monkeypatch, capsys, temperature):
    monkeypatch.setattr(sys, "argv", ["app.ask", "LoRAとは？", temperature])
    monkeypatch.setattr(ask_module.genai, "Client", lambda **_: pytest.fail("Gemini should not be called"))

    ask_module.main()

    assert capsys.readouterr().out.strip() == "Invalid temp"


def test_ask_sends_temperature_to_gemini(monkeypatch):
    received = {}

    class FakeChat:
        def send_message(self, question):
            received["question"] = question
            return SimpleNamespace(usage_metadata=None, text="回答")

    class FakeChats:
        def create(self, **kwargs):
            received.update(kwargs)
            return FakeChat()

    class FakeClient:
        def __init__(self, api_key):
            received["api_key"] = api_key
            self.chats = FakeChats()

        def close(self):
            received["client_closed"] = True

    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)

    assert ask_module.ask("LoRAとは？", 0.7) == "回答"
    assert received["config"].temperature == 0.7
    assert received["question"] == "LoRAとは？"
    assert received["client_closed"]