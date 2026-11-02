import os
import logging
import winsound
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOUNDS_DIR = BASE_DIR / "assets" / "sounds"


class SoundPlayer:
    """
    Reprodutor de efeitos sonoros nativo do Windows com baixa latência e execução assíncrona.
    Utiliza os arquivos de som originais extraídos do Wispr Flow.
    """

    START_SOUND = SOUNDS_DIR / "start.wav"
    STOP_SOUND = SOUNDS_DIR / "stop.wav"
    PASTE_SOUND = SOUNDS_DIR / "paste.wav"
    ERROR_SOUND = SOUNDS_DIR / "error.wav"

    @classmethod
    def _play(cls, file_path: Path, fallback_freq: Optional[int] = None) -> None:
        try:
            if file_path.exists():
                winsound.PlaySound(
                    str(file_path),
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                )
            elif fallback_freq:
                winsound.Beep(fallback_freq, 40)
        except Exception as e:
            logger.debug("Falha ao reproduzir áudio %s: %s", file_path, e)

    @classmethod
    def play_start(cls) -> None:
        """Toca o som de início de gravação (suave e imediato)."""
        cls._play(cls.START_SOUND, fallback_freq=880)

    @classmethod
    def play_stop(cls) -> None:
        """Toca o som de término de gravação."""
        cls._play(cls.STOP_SOUND, fallback_freq=580)

    @classmethod
    def play_paste(cls) -> None:
        """Toca o som de sucesso na injeção de texto."""
        cls._play(cls.PASTE_SOUND, fallback_freq=1100)

    @classmethod
    def play_error(cls) -> None:
        """Toca o som de aviso/erro."""
        cls._play(cls.ERROR_SOUND, fallback_freq=350)
