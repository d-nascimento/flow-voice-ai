import io
import wave
import time
import threading
import logging
from typing import Optional, List
import numpy as np
import soundcard as sc

from src.config import SAMPLE_RATE

logger = logging.getLogger(__name__)


class MeetingRecorder:
    """
    Gravador contínuo de reuniões com suporte a mixagem de Microfone + Loopback (Fone/Chamada).
    Gera áudio WAV 16kHz mono pronto para o pipeline Gemini Long-Context.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self.sample_rate = sample_rate
        self._is_recording = False
        self._include_system_audio = True
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._audio_chunks: List[np.ndarray] = []
        self._lock = threading.Lock()
        self._start_time: float = 0.0

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._is_recording

    def get_duration_sec(self) -> float:
        """Retorna a duração atual da gravação em segundos."""
        with self._lock:
            if not self._is_recording or self._start_time == 0.0:
                return 0.0
            return time.time() - self._start_time

    def start_recording(self, include_system_audio: bool = True) -> bool:
        """Inicia a gravação contínua da reunião em thread de segundo plano."""
        with self._lock:
            if self._is_recording:
                logger.warning("Gravação de reunião já está em andamento.")
                return False

            self._is_recording = True
            self._include_system_audio = include_system_audio
            self._audio_chunks.clear()
            self._stop_event.clear()
            self._start_time = time.time()

        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        logger.info(
            "Gravação de reunião iniciada (Incluir áudio do sistema/chamada: %s).",
            include_system_audio,
        )
        return True

    def stop_recording(self) -> bytes:
        """Interrompe a gravação e retorna os bytes do arquivo WAV gerado."""
        with self._lock:
            if not self._is_recording:
                return b""
            self._is_recording = False

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        with self._lock:
            if not self._audio_chunks:
                logger.info("Nenhum áudio de reunião foi capturado.")
                return b""
            full_audio = np.concatenate(self._audio_chunks, axis=0)
            self._audio_chunks.clear()

        # Converte float32 (-1.0 a 1.0) para int16 PCM
        clamped = np.clip(full_audio, -1.0, 1.0)
        pcm_16 = (clamped * 32767.0).astype(np.int16)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm_16.tobytes())

        wav_bytes = wav_buffer.getvalue()
        duration = len(pcm_16) / self.sample_rate
        logger.info(
            "Gravação de reunião finalizada: %.1fs (%d bytes).",
            duration,
            len(wav_bytes),
        )
        return wav_bytes

    def _record_loop(self) -> None:
        """Loop contínuo de captura e mixagem de blocos de áudio."""
        block_frames = int(self.sample_rate * 0.5)  # Blocos de 500ms

        try:
            mic = sc.default_microphone()
        except Exception as e:
            logger.error("Microfone padrão não encontrado: %s", e)
            mic = None

        loopback = None
        if self._include_system_audio:
            try:
                speaker = sc.default_speaker()
                loopback = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            except Exception as e:
                logger.warning("Loopback de áudio do sistema indisponível: %s", e)

        # Se ambos disponíveis, grava e mixa ambos os canais
        if mic and loopback and self._include_system_audio:
            self._record_mixed_loop(mic, loopback, block_frames)
        elif mic:
            self._record_single_loop(mic, block_frames)
        elif loopback:
            self._record_single_loop(loopback, block_frames)
        else:
            logger.error("Nenhum dispositivo de captura de áudio disponível.")

    def _record_single_loop(self, device, block_frames: int) -> None:
        try:
            with device.recorder(samplerate=self.sample_rate) as rec:
                while not self._stop_event.is_set():
                    data = rec.record(numframes=block_frames)
                    mono = np.mean(data, axis=1) if data.ndim > 1 else data
                    with self._lock:
                        self._audio_chunks.append(mono)
        except Exception as e:
            logger.error("Erro no loop de gravação simples: %s", e)

    def _record_mixed_loop(self, mic_dev, loop_dev, block_frames: int) -> None:
        """Captura simultânea do microfone e loopback do sistema com fusão em mono."""
        try:
            with mic_dev.recorder(samplerate=self.sample_rate) as mic_rec, \
                 loop_dev.recorder(samplerate=self.sample_rate) as loop_rec:
                while not self._stop_event.is_set():
                    mic_data = mic_rec.record(numframes=block_frames)
                    loop_data = loop_rec.record(numframes=block_frames)

                    # Reduz ambos para mono
                    mic_mono = np.mean(mic_data, axis=1) if mic_data.ndim > 1 else mic_data
                    loop_mono = np.mean(loop_data, axis=1) if loop_data.ndim > 1 else loop_data

                    # Mixagem equilibrada com headroom
                    min_len = min(len(mic_mono), len(loop_mono))
                    mixed = 0.5 * mic_mono[:min_len] + 0.5 * loop_mono[:min_len]

                    with self._lock:
                        self._audio_chunks.append(mixed)
        except Exception as e:
            logger.error("Erro no loop de mixagem de reunião: %s", e)
