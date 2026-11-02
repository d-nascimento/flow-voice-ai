import os
import threading
import logging
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QFrame,
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from src.meetings.recorder import MeetingRecorder
from src.meetings.synthesizer import MeetingSynthesizer
from src.meetings.exporter import MeetingExporter
from src.ui.theme import (
    COLOR_BG_CONTAINER,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
)

logger = logging.getLogger(__name__)


class MeetingTab(QWidget):
    """
    Aba do Hub dedicada à gravação de reuniões longas, importação de arquivos de áudio
    e geração de atas executivas estruturadas no estilo visual Wispr Flow.
    """

    signal_status = pyqtSignal(str)
    signal_finished = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.recorder = MeetingRecorder()
        self.synthesizer = MeetingSynthesizer()
        self.exporter = MeetingExporter()

        self._elapsed_seconds = 0
        self._last_obsidian_path: Optional[str] = None
        self._selected_file_path: Optional[Path] = None

        self._init_ui()
        self._init_timer()
        self._connect_signals()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        card = QFrame()
        card.setProperty("class", "card")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(10)

        # Botão de gravação ao vivo e Timer
        top_box = QHBoxLayout()
        self.btn_toggle = QPushButton("🔴 Gravar Reunião ao Vivo")
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_RED};
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 18px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #b91c1c; }}
        """)
        self.btn_toggle.clicked.connect(self._toggle_recording)

        self.lbl_timer = QLabel("⏱️ 00:00:00")
        self.lbl_timer.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.lbl_timer.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; margin-left: 8px;")

        top_box.addWidget(self.btn_toggle)
        top_box.addWidget(self.lbl_timer)
        top_box.addStretch()
        c_lay.addLayout(top_box)

        # Seção de Importação de Arquivo de Áudio
        file_box = QHBoxLayout()
        self.btn_select_file = QPushButton("📁 Importar Arquivo de Áudio")
        self.btn_select_file.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_CONTAINER};
                color: {COLOR_TEXT_PRIMARY};
                font-size: 12px;
                font-weight: 600;
                padding: 7px 14px;
                border-radius: 8px;
                border: 1px solid {COLOR_BORDER};
            }}
            QPushButton:hover {{ background-color: #eae7df; }}
        """)
        self.btn_select_file.clicked.connect(self._select_audio_file)

        self.lbl_selected_file = QLabel("Nenhum arquivo selecionado (.mp3, .m4a, .wav)")
        self.lbl_selected_file.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")

        self.btn_process_file = QPushButton("Gerar Ata Executiva")
        self.btn_process_file.setEnabled(False)
        self.btn_process_file.clicked.connect(self._process_uploaded_file)

        file_box.addWidget(self.btn_select_file)
        file_box.addWidget(self.lbl_selected_file, 1)
        file_box.addWidget(self.btn_process_file)
        c_lay.addLayout(file_box)

        # Opções de captura
        opt_box = QHBoxLayout()
        self.chk_loopback = QCheckBox("Capturar Áudio da Chamada (Loopback de Fone de Ouvido)")
        self.chk_loopback.setChecked(True)
        self.chk_obsidian = QCheckBox("Exportar Automático para o Obsidian (00_Inbox)")
        self.chk_obsidian.setChecked(True)
        opt_box.addWidget(self.chk_loopback)
        opt_box.addWidget(self.chk_obsidian)
        opt_box.addStretch()
        c_lay.addLayout(opt_box)

        layout.addWidget(card)

        # Status
        self.lbl_status = QLabel("Pronto para gravar ou importar áudio.")
        self.lbl_status.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        # Visualizador da Ata Executiva
        layout.addWidget(QLabel("Ata Executiva Estruturada & Transcrição:"))
        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setPlaceholderText(
            "Após finalizar a gravação ou importar um arquivo, a ata executiva com BLUF, "
            "Decisões e Action Items será gerada pelo Gemini Long-Context e exibida aqui..."
        )
        layout.addWidget(self.txt_preview, 1)

        # Rodapé de Ações
        footer = QHBoxLayout()
        self.btn_open_obsidian = QPushButton("Abrir no Obsidian")
        self.btn_open_obsidian.setEnabled(False)
        self.btn_open_obsidian.clicked.connect(self._open_in_obsidian)

        self.btn_copy_markdown = QPushButton("Copiar Markdown")
        self.btn_copy_markdown.clicked.connect(self._copy_markdown)

        footer.addWidget(self.btn_open_obsidian)
        footer.addStretch()
        footer.addWidget(self.btn_copy_markdown)
        layout.addLayout(footer)

    def _init_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_clock)

    def _connect_signals(self) -> None:
        self.signal_status.connect(self.lbl_status.setText)
        self.signal_finished.connect(self._on_finished)

    def _update_clock(self) -> None:
        self._elapsed_seconds += 1
        h = self._elapsed_seconds // 3600
        m = (self._elapsed_seconds % 3600) // 60
        s = self._elapsed_seconds % 60
        self.lbl_timer.setText(f"⏱️ {h:02d}:{m:02d}:{s:02d}")

    def _toggle_recording(self) -> None:
        if not self.recorder.is_recording:
            include_lb = self.chk_loopback.isChecked()
            success = self.recorder.start_recording(include_system_audio=include_lb)
            if success:
                self.btn_toggle.setText("⏹️ Finalizar & Sintetizar Reunião")
                self.btn_toggle.setStyleSheet("""
                    QPushButton {
                        background-color: #262626;
                        color: #ffffff;
                        font-weight: 600;
                        padding: 8px 18px;
                        border-radius: 8px;
                    }
                    QPushButton:hover { background-color: #404040; }
                """)
                self.btn_select_file.setEnabled(False)
                self.btn_process_file.setEnabled(False)
                self._elapsed_seconds = 0
                self.lbl_timer.setText("⏱️ 00:00:00")
                self.timer.start()
                self.lbl_status.setText("Gravando áudio da reunião em alta fidelidade...")
            else:
                self.lbl_status.setText("Erro ao iniciar captura de áudio.")
        else:
            self.timer.stop()
            self.btn_toggle.setEnabled(False)
            self.btn_toggle.setText("Processando...")
            self.lbl_status.setText("Gerando ata com Gemini Long-Context...")
            threading.Thread(target=self._process_meeting, daemon=True).start()

    def _select_audio_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Gravação de Reunião",
            "",
            "Áudios (*.mp3 *.m4a *.wav *.aac *.ogg *.flac);;Todos os Arquivos (*.*)"
        )
        if file_path:
            self._selected_file_path = Path(file_path)
            size_mb = self._selected_file_path.stat().st_size / (1024 * 1024)
            self.lbl_selected_file.setText(f"{self._selected_file_path.name} ({size_mb:.1f} MB)")
            self.btn_process_file.setEnabled(True)

    def _process_uploaded_file(self) -> None:
        if not self._selected_file_path or not self._selected_file_path.exists():
            return
        self.btn_select_file.setEnabled(False)
        self.btn_process_file.setEnabled(False)
        self.btn_toggle.setEnabled(False)
        self.lbl_status.setText("Enviando arquivo para o Gemini Long-Context...")
        threading.Thread(target=self._run_file_synthesis, daemon=True).start()

    def _run_file_synthesis(self) -> None:
        try:
            if not self._selected_file_path:
                return
            markdown = self.synthesizer.synthesize_file(self._selected_file_path)
            saved_path: Optional[Path] = None
            if self.chk_obsidian.isChecked():
                saved_path = self.exporter.export(markdown)
            vault_str = str(saved_path) if saved_path else ""
            self.signal_finished.emit(markdown, vault_str)
        except Exception as e:
            logger.error("Erro na síntese do arquivo de áudio: %s", e)
            self.signal_status.emit(f"Erro no processamento: {e}")

    def _process_meeting(self) -> None:
        try:
            audio_data = self.recorder.stop_recording()
            if audio_data is None or len(audio_data) == 0:
                self.signal_status.emit("Nenhum áudio detectado.")
                self.signal_finished.emit("", "")
                return

            self.signal_status.emit("Enviando áudio ao Gemini Long-Context...")
            markdown = self.synthesizer.synthesize(audio_data)

            saved_path: Optional[Path] = None
            if self.chk_obsidian.isChecked():
                saved_path = self.exporter.export(markdown)

            vault_str = str(saved_path) if saved_path else ""
            self.signal_finished.emit(markdown, vault_str)
        except Exception as e:
            logger.error("Erro no processamento da reunião: %s", e)
            self.signal_status.emit(f"Erro: {e}")

    def _on_finished(self, markdown: str, obsidian_path: str) -> None:
        self.btn_toggle.setEnabled(True)
        self.btn_toggle.setText("🔴 Gravar Reunião ao Vivo")
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT_RED};
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 18px;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #b91c1c; }}
        """)
        self.btn_select_file.setEnabled(True)
        self.btn_process_file.setEnabled(bool(self._selected_file_path))

        if markdown:
            self.txt_preview.setPlainText(markdown)
            if obsidian_path:
                self._last_obsidian_path = obsidian_path
                self.btn_open_obsidian.setEnabled(True)
                self.lbl_status.setText(f"✓ Ata executiva gerada e salva no Obsidian!")
            else:
                self.lbl_status.setText("✓ Ata executiva gerada com sucesso!")
        else:
            self.lbl_status.setText("Processamento concluído sem conteúdo.")

    def _open_in_obsidian(self) -> None:
        if self._last_obsidian_path and os.path.exists(self._last_obsidian_path):
            os.startfile(self._last_obsidian_path)

    def _copy_markdown(self) -> None:
        cb = QApplication.clipboard()
        if cb:
            cb.setText(self.txt_preview.toPlainText())
            self.lbl_status.setText("✓ Markdown copiado para a Área de Transferência!")
