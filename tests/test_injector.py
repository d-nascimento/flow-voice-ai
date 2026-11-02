from unittest.mock import patch, MagicMock
from src.injector.keyboard import TextInjector


def test_injector_empty_text():
    injector = TextInjector()
    assert injector.inject("") is False


@patch("pyperclip.copy")
@patch("pyperclip.paste", return_value="conteudo_anterior")
def test_injector_success(mock_paste, mock_copy):
    injector = TextInjector(paste_delay_sec=0.01)
    with patch.object(injector._keyboard, "pressed") as mock_pressed, \
         patch.object(injector._keyboard, "tap") as mock_tap:
        mock_pressed.return_value.__enter__ = MagicMock()
        mock_pressed.return_value.__exit__ = MagicMock()

        success = injector.inject("Texto para injetar")
        assert success is True
        mock_copy.assert_called_with("Texto para injetar")
        mock_tap.assert_called_with("v")
