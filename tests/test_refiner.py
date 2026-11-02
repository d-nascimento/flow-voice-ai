from unittest.mock import MagicMock
from src.refiner.llm import ContextRefiner
from src.context.window import WindowContext


def test_refiner_empty_text():
    refiner = ContextRefiner(api_key="fake_key")
    assert refiner.refine("") == ""
    assert refiner.refine("   ") == ""


def test_refiner_short_phrase_bypass():
    refiner = ContextRefiner(api_key="fake_key")
    # Frases curtas sem hesitações não precisam chamar a LLM
    assert refiner.refine("ok obrigado") == "ok obrigado"


def test_refiner_mock_call():
    refiner = ContextRefiner(api_key="fake_key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '"Texto refinado sem aspas"'
    mock_client.models.generate_content.return_value = mock_response
    refiner._client = mock_client

    ctx = WindowContext(
        title="WhatsApp",
        process_name="whatsapp.exe",
        app_category="messaging",
        hwnd=123,
    )

    result = refiner.refine("ééé eu acho que tipo assim vamos almoçar", context=ctx)
    assert result == "Texto refinado sem aspas"
    mock_client.models.generate_content.assert_called_once()
