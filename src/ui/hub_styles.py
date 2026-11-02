"""
Estilos e QSS para o Hub de Configurações no padrão Wispr Flow (Warm Clean Sand).
"""
from src.ui.theme import (
    COLOR_BG_APP,
    COLOR_BG_CARD,
    COLOR_BG_CONTAINER,
    COLOR_BG_SURFACE_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT_TEAL,
)

FLOW_THEME_QSS = f"""
QMainWindow {{
    background-color: {COLOR_BG_APP};
    color: {COLOR_TEXT_PRIMARY};
}}

QFrame#sidebar {{
    background-color: {COLOR_BG_APP};
    border-right: 1px solid {COLOR_BORDER};
}}

QPushButton.nav-item {{
    background: transparent;
    color: {COLOR_TEXT_SECONDARY};
    text-align: left;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    border: none;
}}

QPushButton.nav-item:hover {{
    background-color: {COLOR_BG_SURFACE_HOVER};
    color: {COLOR_TEXT_PRIMARY};
}}

QPushButton.nav-item[active="true"] {{
    background-color: {COLOR_BG_CARD};
    color: {COLOR_TEXT_PRIMARY};
    font-weight: 600;
    border: 1px solid {COLOR_BORDER};
}}

QFrame.card {{
    background-color: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 16px;
}}

QFrame.banner {{
    background-color: #1a1715;
    border-radius: 12px;
    padding: 20px;
}}

QLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-size: 13px;
}}

QLabel.title-serif {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 26px;
    font-weight: normal;
    color: {COLOR_TEXT_PRIMARY};
}}

QComboBox {{
    background: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 12px;
}}

QComboBox:focus {{
    border: 1px solid {COLOR_BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
}}

QCheckBox {{
    color: {COLOR_TEXT_PRIMARY};
    spacing: 8px;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {COLOR_BORDER};
    background: {COLOR_BG_CONTAINER};
}}

QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT_TEAL};
    border: 1px solid {COLOR_ACCENT_TEAL};
}}

QListWidget {{
    background-color: {COLOR_BG_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    color: {COLOR_TEXT_PRIMARY};
    padding: 6px;
}}

QListWidget::item {{
    padding: 10px;
    border-bottom: 1px solid {COLOR_BORDER};
    border-radius: 6px;
}}

QListWidget::item:hover {{
    background-color: {COLOR_BG_CONTAINER};
}}

QListWidget::item:selected {{
    background-color: {COLOR_BG_CONTAINER};
    color: {COLOR_TEXT_PRIMARY};
}}

QTextEdit {{
    background-color: {COLOR_BG_CONTAINER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    color: {COLOR_TEXT_PRIMARY};
    padding: 8px;
    font-family: 'Segoe UI', sans-serif;
}}

QPushButton.btn-subtle {{
    background-color: {COLOR_BG_CONTAINER};
    color: {COLOR_TEXT_PRIMARY};
    font-weight: 500;
    font-size: 12px;
    border-radius: 8px;
    padding: 7px 14px;
    border: 1px solid {COLOR_BORDER};
}}

QPushButton.btn-subtle:hover {{
    background-color: {COLOR_BG_SURFACE_HOVER};
}}
"""
