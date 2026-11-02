import sys
import os
import logging
import threading
from pathlib import Path
from typing import Set

# Garante compatibilidade plena com pythonw.exe silencioso no Windows
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from pynput import keyboard

from src.config import HOTKEY_PUSH_TO_TALK, GROQ_API_KEY, GEMINI_API_KEY
from src.pipeline import VoicePipeline
from src.ui.overlay import VoiceOverlay
from src.ui.web_hub import WebHubManager
from src.ui.tray import TrayManager
from src.ui.sound import SoundPlayer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("FlowVoiceAI")
ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"


class DesktopApplication:
    """
    Controlador mestre da aplicação Desktop do Flow Voice AI.
    Conecta o ciclo de eventos do PyQt6, a bandeja, o overlay flutuante e a pipeline.
    """

    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Mantém vivo na bandeja do sistema
        if ICON_PATH.exists():
            self.app.setWindowIcon(QIcon(str(ICON_PATH)))

        # Inicializa UI e Pipeline
        self.pipeline = VoicePipeline()
        self.overlay = VoiceOverlay()
        self.hub = WebHubManager()
        self.tray = TrayManager(
            on_open_hub=self.show_hub,
            on_exit=self.quit,
        )

        # Estado do atalho Push-to-Talk
        self._current_keys: Set[keyboard.Key | keyboard.KeyCode] = set()
        self._is_recording = False
        self._lock = threading.Lock()
        self._hotkey_listener: keyboard.Listener | None = None

    def start(self) -> None:
        """Inicia a aplicação, a bandeja e o listener de teclado."""
        self.tray.show()
        self._start_keyboard_hook()
        logger.info("Flow Voice AI iniciado com sucesso na bandeja.")

    def show_hub(self) -> None:
        self.hub.show()

    def quit(self) -> None:
        logger.info("Encerrando Flow Voice AI...")
        if self._hotkey_listener:
            self._hotkey_listener.stop()
        self.app.quit()

    def _start_keyboard_hook(self) -> None:
        self._hotkey_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._hotkey_listener.daemon = True
        self._hotkey_listener.start()

    def _is_ctrl_pressed(self) -> bool:
        return any(
            k in self._current_keys
            for k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        )

    def _is_hotkey_active(self) -> bool:
        return self._is_ctrl_pressed() and keyboard.Key.space in self._current_keys

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            self._current_keys.add(key)
            if not self._is_recording and self._is_hotkey_active():
                self._is_recording = True
                # Feedback instantâneo de início
                SoundPlayer.play_start()
                self.overlay.show_listening()
                self.pipeline.start_recording()

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            was_recording = self._is_recording
            self._current_keys.discard(key)
            if was_recording and not self._is_hotkey_active():
                self._is_recording = False
                # Feedback de término e início de processamento
                SoundPlayer.play_stop()
                self.overlay.show_processing()

                # Processa em thread separada para não travar a UI nem o hook do Windows
                threading.Thread(target=self._process_voice, daemon=True).start()

    def _process_voice(self) -> None:
        try:
            result = self.pipeline.stop_and_process()
            if result:
                is_command = result.startswith("[COMANDO EXECUTADO:")
                SoundPlayer.play_paste()
                if is_command:
                    self.overlay.show_done("Comando OK!")
                    self.hub.add_history(result, is_command=True)
                else:
                    self.overlay.show_done("Injetado!")
                    self.hub.add_history(result, is_command=False)
            else:
                SoundPlayer.play_error()
                self.overlay.show_error("Inaudível")
        except Exception as e:
            logger.error("Erro no processamento de voz: %s", e)
            SoundPlayer.play_error()
            self.overlay.show_error("Falha")


def main() -> None:
    if not GROQ_API_KEY or not GEMINI_API_KEY:
        print("Aviso: Chaves de API não configuradas no .env!")

    app_instance = DesktopApplication()
    app_instance.start()
    sys.exit(app_instance.app.exec())


if __name__ == "__main__":
    main()
