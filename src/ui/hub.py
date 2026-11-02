import logging
from datetime import datetime
from pathlib import Path
import sounddevice as sd
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QComboBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from src.ui.meeting_tab import MeetingTab
from src.ui.hub_styles import FLOW_THEME_QSS
from src.ui.hub_views import (
    create_dictation_page,
    create_insights_page,
    create_settings_page,
)
from src.ui.theme import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT_LILAC,
    COLOR_ACCENT_LILAC_BG,
)

logger = logging.getLogger(__name__)
ICON_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.png"


class HubWindow(QMainWindow):
    """
    Hub de Configurações, Histórico e Reuniões do Flow Voice AI.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Flow Voice AI — Hub")
        self.resize(880, 620)
        self.setStyleSheet(FLOW_THEME_QSS)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self._nav_buttons: list[QPushButton] = []
        self._init_controls()
        self._init_ui()

    def _init_controls(self) -> None:
        self.history_list = QListWidget(self)
        self._btn_copy_hist = QPushButton("Copiar")
        self._btn_copy_hist.setProperty("class", "btn-subtle")
        self._btn_copy_hist.clicked.connect(self._copy_selected_history)

        self._btn_clear_hist = QPushButton("Limpar")
        self._btn_clear_hist.setProperty("class", "btn-subtle")
        self._btn_clear_hist.clicked.connect(lambda: self.history_list.clear())

        self.combo_mic = QComboBox()
        self._load_microphones()

        self.chk_actions = QCheckBox("Habilitar Comandos de Voz no SO (abrir pastas, web, volume)")
        self.chk_actions.setChecked(True)

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Esquerda
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # 2. Área de Conteúdo Central (QStackedWidget)
        self.stack = QStackedWidget(self)
        self.stack.addWidget(create_dictation_page(self))
        meeting_page = QWidget()
        m_lay = QVBoxLayout(meeting_page)
        m_lay.setContentsMargins(16, 12, 16, 12)
        m_lay.addWidget(MeetingTab(self))
        self.stack.addWidget(meeting_page)
        self.stack.addWidget(create_insights_page())
        self.stack.addWidget(create_settings_page(self.combo_mic, self.chk_actions))
        main_layout.addWidget(self.stack, 1)

        self._select_nav(0)

    def _create_sidebar(self) -> QWidget:
        w = QFrame(self)
        w.setObjectName("sidebar")
        w.setFixedWidth(200)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 18, 14, 18)
        lay.setSpacing(6)

        logo_box = QHBoxLayout()
        logo_lbl = QLabel("||| Flow")
        logo_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        logo_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        badge_pro = QLabel("Pro")
        badge_pro.setStyleSheet(f"""
            background: {COLOR_ACCENT_LILAC_BG};
            color: {COLOR_ACCENT_LILAC};
            font-size: 11px;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 6px;
        """)

        logo_box.addWidget(logo_lbl)
        logo_box.addWidget(badge_pro)
        logo_box.addStretch()
        lay.addLayout(logo_box)
        lay.addSpacing(12)

        nav_items = [
            ("🎤  Dictation", 0),
            ("⏺  Notetaker / Reuniões", 1),
            ("📊  Insights & Uso", 2),
            ("⚙️  Configurações & APIs", 3),
        ]

        self._nav_buttons = []
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "nav-item")
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, idx=index: self._select_nav(idx))
            self._nav_buttons.append(btn)
            lay.addWidget(btn)

        lay.addStretch()

        card_pro = QFrame()
        card_pro.setStyleSheet(f"""
            background-color: {COLOR_ACCENT_LILAC_BG};
            border-radius: 10px;
            padding: 10px;
        """)
        c_lay = QVBoxLayout(card_pro)
        c_lay.setSpacing(4)
        lbl_p1 = QLabel("Flow Voice AI Ativo")
        lbl_p1.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_ACCENT_LILAC};")
        lbl_p2 = QLabel("Push-to-Talk com fidelidade natural à voz.")
        lbl_p2.setWordWrap(True)
        lbl_p2.setStyleSheet(f"font-size: 10px; color: {COLOR_TEXT_SECONDARY};")
        c_lay.addWidget(lbl_p1)
        c_lay.addWidget(lbl_p2)
        lay.addWidget(card_pro)

        return w

    def _select_nav(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            is_active = (i == index)
            btn.setProperty("active", "true" if is_active else "false")
            style = btn.style()
            if style:
                style.unpolish(btn)
                style.polish(btn)

    def _load_microphones(self) -> None:
        try:
            devs = sd.query_devices()
            unique_mics = []
            for d in devs:
                if d.get("max_input_channels", 0) > 0:
                    name = d.get("name", "Desconhecido")
                    if name not in unique_mics:
                        unique_mics.append(name)
            for m in unique_mics:
                self.combo_mic.addItem(m)
        except Exception as e:
            logger.warning("Falha ao listar microfones: %s", e)
            self.combo_mic.addItem("Microfone Padrão do Sistema")

    def add_history(self, text: str, is_command: bool = False) -> None:
        time_str = datetime.now().strftime("%H:%M")
        badge = "⚡ COMANDO" if is_command else "✍️ DITAÇÃO"
        item = QListWidgetItem(f"{time_str}   {badge}   —   {text}")
        self.history_list.insertItem(0, item)

    def _copy_selected_history(self) -> None:
        curr = self.history_list.currentItem()
        if curr:
            text = curr.text()
            if "—" in text:
                text = text.split("—", 1)[-1].strip()
            cb = QApplication.clipboard()
            if cb:
                cb.setText(text)

    def closeEvent(self, event) -> None:  # type: ignore
        event.ignore()
        self.hide()
