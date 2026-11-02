from unittest.mock import MagicMock
from src.actions.intent_router import IntentRouter, VoiceIntent


def test_intent_router_empty():
    router = IntentRouter(api_key="fake_key")
    res = router.route_intent("")
    assert res.type == "dictation"
    assert res.text == ""


def test_intent_router_fast_heuristics():
    router = IntentRouter(api_key="fake_key")
    vol_intent = router.route_intent("aumentar volume")
    assert vol_intent.type == "command"
    assert vol_intent.action == "volume_up"

    mute_intent = router.route_intent("mutar som")
    assert mute_intent.type == "command"
    assert mute_intent.action == "volume_mute"

    print_intent = router.route_intent("tirar print")
    assert print_intent.type == "command"
    assert print_intent.action == "screenshot"


def test_intent_router_mock_gemini():
    router = IntentRouter(api_key="fake_key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"type": "command", "action": "open_app", "parameter": "chrome", "text": "Abrindo o Chrome..."}'
    mock_client.models.generate_content.return_value = mock_response
    router._client = mock_client

    intent = router.route_intent("abra o google chrome")
    assert intent.type == "command"
    assert intent.action == "open_app"
    assert intent.parameter == "chrome"
