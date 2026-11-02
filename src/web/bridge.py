import logging
import sounddevice as sd
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.meetings.recorder import MeetingRecorder
from src.meetings.synthesizer import MeetingSynthesizer
from src.meetings.exporter import MeetingExporter

logger = logging.getLogger(__name__)


class WebBridge:
    """
    Ponte de comunicação bidirecional entre o Frontend Web e o Backend Python.
    Exposta diretamente no JavaScript da janela como `window.pywebview.api`.
    """

    def __init__(self) -> None:
        self.meeting_recorder = MeetingRecorder()
        self.synthesizer = MeetingSynthesizer()
        self.exporter = MeetingExporter()
        self.history: List[Dict[str, Any]] = []
        self._window = None

    def set_window(self, window: Any) -> None:
        self._window = window

    # --- Microfones e Dispositivos ---

    def get_microphones(self) -> List[str]:
        """Lista os microfones disponíveis no sistema."""
        try:
            devs = sd.query_devices()
            unique_mics: List[str] = []
            for d in devs:
                if d.get("max_input_channels", 0) > 0:
                    name = str(d.get("name", "Desconhecido"))
                    if name not in unique_mics:
                        unique_mics.append(name)
            return unique_mics or ["Microfone Padrão do Sistema"]
        except Exception as e:
            logger.warning("Falha ao listar microfones: %s", e)
            return ["Microfone Padrão do Sistema"]

    # --- Histórico de Transcrições ---

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def clear_history(self) -> bool:
        self.history.clear()
        return True

    def add_history_entry(self, text: str, is_command: bool = False) -> None:
        from datetime import datetime
        entry = {
            "time": datetime.now().strftime("%H:%M"),
            "type": "command" if is_command else "dictation",
            "text": text,
        }
        self.history.insert(0, entry)
        if self._window:
            try:
                self._window.evaluate_js(f"window.onHistoryUpdate && window.onHistoryUpdate({entry})")
            except Exception as e:
                logger.debug("Falha ao disparar evento de histórico no JS: %s", e)

    # --- Reuniões & Notetaker ---

    def get_meeting_status(self) -> Dict[str, Any]:
        return {
            "is_recording": self.meeting_recorder.is_recording,
            "duration_sec": self.meeting_recorder.get_duration_sec(),
        }

    def start_meeting_recording(self, include_loopback: bool = True) -> Dict[str, Any]:
        success = self.meeting_recorder.start_recording(include_system_audio=include_loopback)
        return {"success": success}

    def stop_meeting_recording(self, save_obsidian: bool = True) -> Dict[str, Any]:
        try:
            audio_data = self.meeting_recorder.stop_recording()
            if not audio_data:
                return {"success": False, "error": "Nenhum áudio detectado."}

            markdown = self.synthesizer.synthesize(audio_data)
            obsidian_path: Optional[Path] = None
            if save_obsidian:
                obsidian_path = self.exporter.export(markdown)

            return {
                "success": True,
                "markdown": markdown,
                "obsidian_path": str(obsidian_path) if obsidian_path else "",
            }
        except Exception as e:
            logger.error("Erro ao finalizar reunião via bridge: %s", e)
            return {"success": False, "error": str(e)}

    def synthesize_uploaded_file(self, file_path_str: str, save_obsidian: bool = True) -> Dict[str, Any]:
        try:
            path = Path(file_path_str)
            if not path.exists():
                return {"success": False, "error": "Arquivo não encontrado no disco."}

            markdown = self.synthesizer.synthesize_file(path)
            obsidian_path: Optional[Path] = None
            if save_obsidian:
                obsidian_path = self.exporter.export(markdown)

            return {
                "success": True,
                "markdown": markdown,
                "obsidian_path": str(obsidian_path) if obsidian_path else "",
            }
        except Exception as e:
            logger.error("Erro ao sintetizar arquivo via bridge: %s", e)
            return {"success": False, "error": str(e)}

    def open_path_in_os(self, file_path: str) -> bool:
        """Abre arquivo no Obsidian ou aplicativo padrão do Windows."""
        try:
            import os
            if os.path.exists(file_path):
                os.startfile(file_path)
                return True
        except Exception as e:
            logger.warning("Falha ao abrir caminho: %s", e)
        return False
