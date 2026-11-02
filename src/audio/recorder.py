import io
import wave
import threading
import logging
from typing import Optional
import numpy as np
import sounddevice as sd

from src.config import SAMPLE_RATE, CHANNELS

logger = logging.getLogger(__name__)


class AudioRecorder:
    """
    Gerenciador de captura de áudio push-to-talk em memória.
    Grava em 16kHz mono (int16 PCM) diretamente para stream WAV sem I/O em disco.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self._stream: Optional[sd.InputStream] = None
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._is_recording

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags
    ) -> None:
        if status:
            logger.warning("Status do sounddevice: %s", status)
        with self._lock:
            if self._is_recording:
                # Faz cópia do buffer recebido
                self._frames.append(indata.copy())

    def start_recording(self) -> bool:
        """Inicia a gravação em memória."""
        with self._lock:
            if self._is_recording:
                logger.warning("Gravação já está em andamento.")
                return False

            self._frames.clear()
            self._is_recording = True

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
            logger.info("Gravação de áudio iniciada.")
            return True
        except Exception as e:
            logger.error("Falha ao abrir stream de áudio do microfone: %s", e)
            with self._lock:
                self._is_recording = False
            return False

    def stop_recording(self, min_duration_sec: float = 0.3) -> bytes:
        """
        Interrompe a gravação e retorna os bytes do arquivo WAV gerado em memória.
        Retorna bytes vazios se a gravação for menor que min_duration_sec ou silenciosa.
        """
        with self._lock:
            if not self._is_recording:
                return b""
            self._is_recording = False

        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.error("Erro ao encerrar stream de áudio: %s", e)
            finally:
                self._stream = None

        with self._lock:
            if not self._frames:
                logger.info("Nenhum quadro de áudio capturado.")
                return b""
            audio_data = np.concatenate(self._frames, axis=0)

        total_samples = len(audio_data)
        duration_sec = total_samples / self.sample_rate

        if duration_sec < min_duration_sec:
            logger.info("Áudio descartado: duração muito curta (%.2fs < %.2fs).", duration_sec, min_duration_sec)
            return b""

        # Checa RMS de energia para ignorar silêncio absoluto / cliques acidentais
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        if rms < 50.0:
            logger.info("Áudio descartado por falta de energia/volume (RMS: %.1f).", rms)
            return b""

        # Empacota em WAV na memória
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        wav_bytes = wav_buffer.getvalue()
        logger.info("Áudio capturado com sucesso: %.2fs (%d bytes, RMS: %.1f).", duration_sec, len(wav_bytes), rms)
        return wav_bytes
