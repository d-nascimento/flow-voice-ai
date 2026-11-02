import sys
import time
import logging
import threading
import winsound
from typing import Set
from pynput import keyboard

from src.config import HOTKEY_PUSH_TO_TALK, GROQ_API_KEY, GEMINI_API_KEY
from src.pipeline import VoicePipeline

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("FlowVoiceAI")


def play_sound(freq: int, duration_ms: int) -> None:
    """Toca sinal sonoro sutil em thread separada para não travar a execução."""
    def _beep():
        try:
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()


class HotkeyListener:
    """
    Gerenciador global de atalho Push-to-Talk (ex: Ctrl+Space).
    """

    def __init__(self, pipeline: VoicePipeline, hotkey_str: str = HOTKEY_PUSH_TO_TALK) -> None:
        self.pipeline = pipeline
        self.hotkey_str = hotkey_str.lower().strip()
        self._current_keys: Set[keyboard.Key | keyboard.KeyCode] = set()
        self._is_active = False
        self._lock = threading.Lock()

    def _is_ctrl_pressed(self) -> bool:
        return any(
            k in self._current_keys
            for k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        )

    def _is_hotkey_triggered(self) -> bool:
        if self.hotkey_str == "ctrl+space":
            return self._is_ctrl_pressed() and keyboard.Key.space in self._current_keys
        if self.hotkey_str in ("f8", "f9", "f10"):
            target_key = getattr(keyboard.Key, self.hotkey_str, None)
            return target_key in self._current_keys if target_key else False
        return self._is_ctrl_pressed() and keyboard.Key.space in self._current_keys

    def on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            self._current_keys.add(key)
            if not self._is_active and self._is_hotkey_triggered():
                self._is_active = True
                play_sound(880, 40)  # Beep agudo curto: início
                print("\n🎙️ [GRAVANDO...] Fale naturalmente e solte a tecla para injetar.")
                self.pipeline.start_recording()

    def on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            was_active = self._is_active
            self._current_keys.discard(key)
            # Se estava gravando e a combinação foi desfeita
            if was_active and not self._is_hotkey_triggered():
                self._is_active = False
                play_sound(580, 40)  # Beep grave curto: fim
                print("⏳ [PROCESSANDO...] Transcrevendo com Groq e refinando com Gemini...")

                # Executa o processamento em thread separada para não bloquear a mensageria do Windows
                threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self) -> None:
        try:
            result = self.pipeline.stop_and_process()
            if result:
                if result.startswith("[COMANDO EXECUTADO:"):
                    print(f"🚀 {result}\n")
                else:
                    print(f"✨ [INJETADO COM SUCESSO]: \"{result}\"\n")
            else:
                print("⚠️ [NENHUM TEXTO]: Fala muito curta ou inaudível.\n")
        except Exception as e:
            logger.error("Erro inesperado no pipeline de voz: %s", e)


def print_banner() -> None:
    banner = r"""
  ______ _                 __      __   _             QUICK PTT
 |  ____| |                \ \    / /  (_)               AI
 | |__  | | _____      __   \ \  / /__  _  ___ ___ 
 |  __| | |/ _ \ \ /\ / /    \ \/ / _ \| |/ __/ _ \
 | |    | | (_) \ V  V /      \  / (_) | | (_|  __/
 |_|    |_|\___/ \_/\_/        \/ \___/|_|\___\___|  v1.0 (Windows)
    """
    print(banner)
    print("=" * 65)
    print(f"  Atalho Push-to-Talk : [{HOTKEY_PUSH_TO_TALK.upper()}] (Segure para falar)")
    print("  ASR Engine          : Groq Cloud (Whisper Large-v3-turbo)")
    print("  AI Router & Brain   : Google Gemini (3.5 Flash Lite)")
    print("  Modos Ativos        : Ditação Inteligente + Controle de Voz do PC")
    print("=" * 65)
    print("  Pressione Ctrl+C para encerrar.\n")


def main() -> None:
    print_banner()

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY não definida! Preencha no arquivo .env.")
        sys.exit(1)
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY não definida! Preencha no arquivo .env.")
        sys.exit(1)

    pipeline = VoicePipeline()
    handler = HotkeyListener(pipeline=pipeline)

    logger.info("Ouvindo atalho global: %s", HOTKEY_PUSH_TO_TALK)
    with keyboard.Listener(on_press=handler.on_press, on_release=handler.on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nEncerrando Flow Voice AI com segurança.")


if __name__ == "__main__":
    main()
