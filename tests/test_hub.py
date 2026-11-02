from PyQt6.QtWidgets import QApplication
from src.ui.hub import HubWindow

app = QApplication.instance() or QApplication([])


def test_hub_window_init():
    hub = HubWindow()
    assert hub.windowTitle() == "Flow Voice AI — Hub"
    assert hub.combo_mic.count() > 0
    assert hub.chk_actions.isChecked()


def test_hub_add_history():
    hub = HubWindow()
    hub.add_history("Teste ditação", is_command=False)
    hub.add_history("Abrir Chrome", is_command=True)
    assert hub.history_list.count() == 2
    assert "COMANDO" in hub.history_list.item(0).text()
    assert "DITAÇÃO" in hub.history_list.item(1).text()
