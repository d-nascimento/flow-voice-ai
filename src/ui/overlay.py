import random
import ctypes
import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QBrush

logger = logging.getLogger(__name__)


class WaveformWidget(QWidget):
    """
    Mini visualizador de onda sonora em estilo Flow Voice AI Clean.
    Desenha barras dinâmicas brancas/azuis arredondadas com maior espessura.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self._bars = [0.38, 0.68, 1.0, 0.68, 0.38]
        self._is_active = False

    def set_active(self, active: bool) -> None:
        self._is_active = active
        self.update()

    def update_wave(self) -> None:
        if self._is_active:
            self._bars = [random.uniform(0.25, 1.0) for _ in self._bars]
            self.update()

    def paintEvent(self, event) -> None:  # type: ignore
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._is_active:
            color = QColor(148, 163, 184, 180)  # Slate muted
        else:
            color = QColor(255, 255, 255, 255)  # Branco nítido

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)

        w, h = self.width(), self.height()
        bar_width = 3.5  # Mais grossa e nítida
        gap = 4.0
        total_width = len(self._bars) * bar_width + (len(self._bars) - 1) * gap
        start_x = (w - total_width) / 2.0

        for i, amp in enumerate(self._bars):
            bar_height = max(5.0, h * (amp if self._is_active else 0.3))
            x = start_x + i * (bar_width + gap)
            y = (h - bar_height) / 2.0
            rect = QRectF(x, y, bar_width, bar_height)
            painter.drawRoundedRect(rect, 1.75, 1.75)


class VoiceOverlay(QWidget):
    """
    Floating Pill minimalista no estilo Flow Voice AI Clean Navy.
    Aparece suavemente sobre a tela sem roubar foco do cursor ativo (WS_EX_NOACTIVATE).
    """

    signal_start_listening = pyqtSignal()
    signal_start_processing = pyqtSignal()
    signal_done = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._init_window_flags()
        self._init_ui()
        self._init_timers()
        self._connect_signals()

    def _init_window_flags(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

    def _apply_win32_no_activate(self) -> None:
        try:
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
        except Exception as e:
            logger.debug("Win32 WS_EX_NOACTIVATE: %s", e)

    def _init_ui(self) -> None:
        self.setFixedSize(220, 44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        self.icon_label = QLabel("●", self)
        self.icon_label.setStyleSheet("color: #38bdf8; font-size: 13px;")

        self.status_label = QLabel("Ouvindo...", self)
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #ffffff;")

        self.wave_widget = WaveformWidget(self)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.wave_widget)

        self._position_on_screen()

    def _position_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            x = (geom.width() - self.width()) // 2
            y = geom.height() - 95
            self.move(x, y)

    def _init_timers(self) -> None:
        self.wave_timer = QTimer(self)
        self.wave_timer.setInterval(70)
        self.wave_timer.timeout.connect(self.wave_widget.update_wave)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def _connect_signals(self) -> None:
        self.signal_start_listening.connect(self._on_listening)
        self.signal_start_processing.connect(self._on_processing)
        self.signal_done.connect(self._on_done)
        self.signal_error.connect(self._on_error)

    def paintEvent(self, event) -> None:  # type: ignore
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
        # Navy Profundo (#0f172a) com borda discreta
        bg_color = QColor(15, 23, 42, 245)
        border_color = QColor(255, 255, 255, 35)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(border_color)
        painter.drawRoundedRect(rect, 22.0, 22.0)

    def show_listening(self) -> None:
        self.signal_start_listening.emit()

    def show_processing(self) -> None:
        self.signal_start_processing.emit()

    def show_done(self, message: str = "Injetado!") -> None:
        self.signal_done.emit(message)

    def show_error(self, message: str = "Inaudível") -> None:
        self.signal_error.emit(message)

    def _on_listening(self) -> None:
        self.hide_timer.stop()
        self.icon_label.setText("●")
        self.icon_label.setStyleSheet("color: #38bdf8; font-size: 13px;")  # Azul celeste
        self.status_label.setText("Ouvindo...")
        self.wave_widget.set_active(True)
        self.wave_timer.start()
        self._position_on_screen()
        self.show()
        self._apply_win32_no_activate()

    def _on_processing(self) -> None:
        self.wave_timer.stop()
        self.wave_widget.set_active(False)
        self.icon_label.setText("◐")
        self.icon_label.setStyleSheet("color: #fbbf24; font-size: 13px;")  # Âmbar
        self.status_label.setText("Processando...")
        self.show()

    def _on_done(self, message: str) -> None:
        self.wave_timer.stop()
        self.wave_widget.set_active(False)
        self.icon_label.setText("✓")
        self.icon_label.setStyleSheet("color: #22c55e; font-size: 13px; font-weight: bold;")  # Verde
        self.status_label.setText(message[:20])
        self.hide_timer.start(750)

    def _on_error(self, message: str) -> None:
        self.wave_timer.stop()
        self.wave_widget.set_active(False)
        self.icon_label.setText("!")
        self.icon_label.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: bold;")  # Vermelho
        self.status_label.setText(message[:20])
        self.hide_timer.start(900)
