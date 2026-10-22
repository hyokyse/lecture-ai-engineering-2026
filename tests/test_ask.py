import sys
from types import SimpleNamespace

import pytest

from app import ask as ask_module


def test_main_uses_default_temperature(monkeypatch):
    received = []
    monkeypatch.setattr(sys, "argv", ["app.ask", "LoRAとは？"])
    monkeypatch.setattr(ask_module, "ask", lambda question, temperature: received.append((question, temperature)) or "回答")

    ask_module.main()

    assert received == [("LoRAとは？", 1.0)]


@pytest.mark.parametrize("temperature", ["abc", "-0.1", "2.1"])
def test_main_rejects_invalid_temperature(monkeypatch, capsys, temperature):
    monkeypatch.setattr(sys, "argv", ["app.ask", "LoRAとは？", temperature])
    monkeypatch.setattr(ask_module, "ask", lambda *_: pytest.fail("Gemini should not be called"))

    ask_module.main()

    assert capsys.readouterr().out.strip() == "Invalid temp"


def test_ask_sends_temperature_to_gemini(monkeypatch):
    received = {}

    class FakeClient:
        def __init__(self, api_key):
            received["api_key"] = api_key
            self.models = self

        def generate_content(self, **kwargs):
            received.update(kwargs)
            return SimpleNamespace(usage_metadata=None, text="回答")

    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)

    assert ask_module.ask("LoRAとは？", 0.7) == "回答"
    assert received["config"].temperature == 0.7