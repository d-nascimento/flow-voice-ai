from unittest.mock import patch
from src.actions.system_controller import SystemController


@patch("os.startfile")
def test_open_app(mock_startfile):
    assert SystemController.open_app("chrome") is True
    mock_startfile.assert_called_with("chrome")


@patch("webbrowser.open")
def test_search_web(mock_webbrowser):
    assert SystemController.search_web("python asyncio") is True
    mock_webbrowser.assert_called_once()
    assert "python%20asyncio" in mock_webbrowser.call_args[0][0]


@patch("ctypes.windll.user32.keybd_event")
def test_volume_controls(mock_keybd):
    assert SystemController.volume_up(steps=2) is True
    assert SystemController.volume_down(steps=2) is True
    assert SystemController.volume_mute() is True
    assert mock_keybd.call_count > 0


@patch("ctypes.windll.user32.LockWorkStation")
def test_lock_pc(mock_lock):
    assert SystemController.lock_pc() is True
    mock_lock.assert_called_once()
