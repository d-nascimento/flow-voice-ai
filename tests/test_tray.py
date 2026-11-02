from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from src.ui.tray import TrayManager

app = QApplication.instance() or QApplication([])


def test_tray_manager_init():
    mock_hub = MagicMock()
    mock_exit = MagicMock()
    tray = TrayManager(on_open_hub=mock_hub, on_exit=mock_exit)

    assert tray.tray_icon.toolTip() == "Flow Voice AI — Pressione Ctrl + Espaço"
    assert tray.tray_icon.contextMenu() is not None
