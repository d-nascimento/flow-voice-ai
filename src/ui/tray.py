import logging
from pathlib import Path
from typing import Callable, Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction

logger = logging.getLogger(__name__)

ICON_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png"


class TrayManager:
    """
    Gerenciador do ícone de notificação na bandeja do sistema (perto do relógio do Windows).
    """

    def __init__(
        self,
        on_open_hub: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        self.on_open_hub = on_open_hub
        self.on_exit = on_exit or QApplication.quit
        self.tray_icon = QSystemTrayIcon()

        self._setup_icon()
        self._setup_menu()
        self._connect_signals()

    def _setup_icon(self) -> None:
        if ICON_PATH.exists():
            icon = QIcon(str(ICON_PATH))
            self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Flow Voice AI — Pressione Ctrl + Espaço")

    def _setup_menu(self) -> None:
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #171724;
                color: #f3f4f6;
                border: 1px solid #2d2d44;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #7e22ce;
            }
            QMenu::separator {
                height: 1px;
                background: #272738;
                margin: 4px 8px;
            }
        """)

        # Cabeçalho decorativo
        header = QAction("⚡ Flow Voice AI (v1.0)", menu)
        header.setEnabled(False)
        menu.addAction(header)

        shortcut = QAction("🎙️ Atalho: Ctrl + Espaço", menu)
        shortcut.setEnabled(False)
        menu.addAction(shortcut)

        menu.addSeparator()

        act_hub = QAction("⚙️ Abrir Configurações (Hub)", menu)
        if self.on_open_hub:
            act_hub.triggered.connect(self.on_open_hub)
        menu.addAction(act_hub)

        act_meeting = QAction("📋 Gravar Reunião (Atas & Tarefas)", menu)
        if self.on_open_hub:
            act_meeting.triggered.connect(self.on_open_hub)
        menu.addAction(act_meeting)

        menu.addSeparator()

        act_exit = QAction("🚪 Sair", menu)
        act_exit.triggered.connect(self.on_exit)
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)

    def _connect_signals(self) -> None:
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        # Clique com botão esquerdo ou duplo clique abre o Hub
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            if self.on_open_hub:
                self.on_open_hub()

    def show(self) -> None:
        self.tray_icon.show()

    def notify(self, title: str, message: str) -> None:
        """Exibe notificação nativa do Windows através da bandeja."""
        self.tray_icon.showMessage(
            title, message, QSystemTrayIcon.MessageIcon.Information, 2500
        )
