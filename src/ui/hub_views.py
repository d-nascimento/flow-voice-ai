from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QCheckBox,
)
from PyQt6.QtGui import QFont

from src.ui.theme import (
    COLOR_ACCENT_AMBER_BG,
    COLOR_ACCENT_AMBER,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_GREEN,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
)


def create_dictation_page(parent_hub: QWidget) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(24, 20, 24, 20)
    lay.setSpacing(14)

    header = QHBoxLayout()
    h_label = QLabel("Hey, entre no fluxo com")
    h_label.setStyleSheet("font-size: 16px; font-weight: 500;")

    badge_hotkey = QLabel("Ctrl + Espaço")
    badge_hotkey.setStyleSheet(f"""
        background: {COLOR_ACCENT_AMBER_BG};
        color: #b45309;
        border: 1px solid {COLOR_ACCENT_AMBER};
        font-size: 13px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
    """)
    header.addWidget(h_label)
    header.addWidget(badge_hotkey)
    header.addStretch()
    lay.addLayout(header)

    banner = QFrame()
    banner.setProperty("class", "banner")
    b_lay = QVBoxLayout(banner)
    b_lay.setSpacing(6)
    b_title = QLabel("Make Flow sound like you")
    b_title.setStyleSheet("font-family: Georgia, serif; font-size: 20px; color: #ffffff;")
    b_sub = QLabel("Fale naturalmente em Português ou Inglês. O modelo preserva o idioma e refina pontuação.")
    b_sub.setStyleSheet("font-size: 12px; color: #a1a1aa;")
    b_lay.addWidget(b_title)
    b_lay.addWidget(b_sub)
    lay.addWidget(banner)

    lay.addSpacing(6)
    hist_header = QHBoxLayout()
    lbl_recent = QLabel("TRANSCRIÇÕES RECENTES")
    lbl_recent.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLOR_TEXT_MUTED};")
    hist_header.addWidget(lbl_recent)
    hist_header.addStretch()

    btn_copy = getattr(parent_hub, "_btn_copy_hist")
    btn_clear = getattr(parent_hub, "_btn_clear_hist")
    hist_header.addWidget(btn_copy)
    hist_header.addWidget(btn_clear)
    lay.addLayout(hist_header)

    lay.addWidget(getattr(parent_hub, "history_list"), 1)
    return w


def create_insights_page() -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(24, 20, 24, 20)
    lay.setSpacing(16)

    title = QLabel("Insights & Produtividade")
    title.setProperty("class", "title-serif")
    lay.addWidget(title)

    grid = QHBoxLayout()
    grid.setSpacing(12)
    grid.addWidget(_build_stat_card("144", "PALAVRAS POR MINUTO", "Top 0.2% velocidade"))
    grid.addWidget(_build_stat_card("~240ms", "LATÊNCIA MÉDIA", "Groq Whisper Turbo"))
    grid.addWidget(_build_stat_card("100%", "DISPONIBILIDADE", "Desktop Windows Ativo"))
    lay.addLayout(grid)

    info_card = QFrame()
    info_card.setProperty("class", "card")
    i_lay = QVBoxLayout(info_card)
    i_lay.setSpacing(8)
    i_title = QLabel("Arquitetura de Dupla Inteligência")
    i_title.setStyleSheet("font-weight: 600; font-size: 14px;")
    i_desc = QLabel(
        "• Transcrição acústica imediata via Groq Whisper Large-v3-turbo.\n"
        "• Refinamento de pontuação, detecção de comandos de voz e preservação de idioma via Gemini 3.5 Flash Lite.\n"
        "• Atas executivas com contexto estendido de até 9,5h via Gemini Flash Long-Context."
    )
    i_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; line-height: 1.4;")
    i_lay.addWidget(i_title)
    i_lay.addWidget(i_desc)
    lay.addWidget(info_card)
    lay.addStretch()
    return w


def _build_stat_card(value: str, label: str, footer: str) -> QFrame:
    card = QFrame()
    card.setProperty("class", "card")
    lay = QVBoxLayout(card)
    lay.setSpacing(4)
    val_lbl = QLabel(value)
    val_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
    val_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
    tag_lbl = QLabel(label)
    tag_lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {COLOR_TEXT_MUTED};")
    ft_lbl = QLabel(footer)
    ft_lbl.setStyleSheet(f"font-size: 11px; color: {COLOR_ACCENT_TEAL}; font-weight: 500;")
    lay.addWidget(val_lbl)
    lay.addWidget(tag_lbl)
    lay.addSpacing(4)
    lay.addWidget(ft_lbl)
    return card


def create_settings_page(combo_mic: QComboBox, chk_actions: QCheckBox) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(24, 20, 24, 20)
    lay.setSpacing(14)

    title = QLabel("Configurações Gerais")
    title.setProperty("class", "title-serif")
    lay.addWidget(title)

    card_mic = QFrame()
    card_mic.setProperty("class", "card")
    m_lay = QVBoxLayout(card_mic)
    m_lay.setSpacing(6)
    m_lay.addWidget(QLabel("Dispositivo de Microfone:"))
    m_lay.addWidget(combo_mic)
    lay.addWidget(card_mic)

    card_actions = QFrame()
    card_actions.setProperty("class", "card")
    a_lay = QVBoxLayout(card_actions)
    a_lay.addWidget(chk_actions)
    lay.addWidget(card_actions)

    card_api = QFrame()
    card_api.setProperty("class", "card")
    api_lay = QVBoxLayout(card_api)
    api_lay.setSpacing(6)
    api_title = QLabel("Conexões de Inteligência Artificial")
    api_title.setStyleSheet("font-weight: 600;")
    s1 = QLabel("● Groq Cloud API (Whisper Large-v3-turbo): Conectado")
    s1.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 12px;")
    s2 = QLabel("● Google Gemini API (Flash Lite & Long-Context): Conectado")
    s2.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 12px;")
    api_lay.addWidget(api_title)
    api_lay.addWidget(s1)
    api_lay.addWidget(s2)
    lay.addWidget(card_api)

    lay.addStretch()
    return w
