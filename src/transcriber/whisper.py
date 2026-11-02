import logging
import time
from typing import Optional
from groq import Groq

from src.config import GROQ_API_KEY, WHISPER_MODEL, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """
    Cliente ASR de alta velocidade utilizando Whisper Large-v3 na Groq Cloud.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = WHISPER_MODEL,
        default_language: str = DEFAULT_LANGUAGE,
    ) -> None:
        self.api_key = api_key or GROQ_API_KEY
        self.model = model
        self.default_language = default_language
        self._client: Optional[Groq] = None

    @property
    def client(self) -> Groq:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY não configurada no ambiente ou .env.")
            self._client = Groq(api_key=self.api_key)
        return self._client

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcreve bytes WAV em texto bruto.
        Retorna string vazia caso o áudio seja vazio ou ocorra falha de conexão.
        """
        if not audio_bytes:
            return ""

        start_time = time.perf_counter()
        try:
            # Envia diretamente o buffer de memória com o cabeçalho WAV
            kwargs: dict = {
                "file": ("speech.wav", audio_bytes, "audio/wav"),
                "model": self.model,
                "response_format": "json",
                "temperature": 0.0,
            }
            if self.default_language:
                kwargs["language"] = self.default_language

            response = self.client.audio.transcriptions.create(**kwargs)

            raw_text = response.text.strip() if response.text else ""
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info("Transcrição concluída em %.1fms: '%s'", elapsed_ms, raw_text)

            # Filtra artefatos comuns do Whisper em silêncio
            unwanted_hallucinations = {"[música]", "[silêncio]", "[aplausos]", "[risos]"}
            if raw_text.lower() in unwanted_hallucinations:
                return ""

            return raw_text

        except Exception as e:
            logger.error("Erro na transcrição Groq Whisper: %s", e)
            return ""
