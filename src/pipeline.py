import time
import logging
from dataclasses import dataclass
from typing import Optional

from src.audio.recorder import AudioRecorder
from src.transcriber.whisper import WhisperTranscriber
from src.context.window import WindowTracker, WindowContext
from src.injector.keyboard import TextInjector
from src.actions.intent_router import IntentRouter, VoiceIntent
from src.actions.system_controller import SystemController

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    transcription_ms: float = 0.0
    intent_ms: float = 0.0
    execution_ms: float = 0.0
    total_ms: float = 0.0


class VoicePipeline:
    """
    Orquestrador central do Flow Voice AI.
    Conecta Gravação -> Transcrição -> Detecção de Contexto -> Roteamento de Intenção -> Ação/Injeção.
    """

    def __init__(
        self,
        recorder: Optional[AudioRecorder] = None,
        transcriber: Optional[WhisperTranscriber] = None,
        router: Optional[IntentRouter] = None,
        injector: Optional[TextInjector] = None,
        controller: Optional[SystemController] = None,
    ) -> None:
        self.recorder = recorder or AudioRecorder()
        self.transcriber = transcriber or WhisperTranscriber()
        self.router = router or IntentRouter()
        self.injector = injector or TextInjector()
        self.controller = controller or SystemController()

    def start_recording(self) -> bool:
        """Disparado quando o usuário aperta a tecla de atalho (Push)."""
        return self.recorder.start_recording()

    def stop_and_process(self) -> Optional[str]:
        """
        Disparado quando o usuário solta a tecla de atalho (Release).
        Executa a pipeline ponta a ponta e despacha para Ação no Windows ou Injeção de Texto.
        """
        # Captura imediatamente a janela em foco no exato momento da soltura
        context: WindowContext = WindowTracker.get_active_window()
        logger.info(
            "Processando fala para janela ativa: '%s' (%s | %s)",
            context.title,
            context.process_name,
            context.app_category,
        )

        # 1. Finaliza a gravação e extrai os bytes do áudio WAV
        audio_bytes = self.recorder.stop_recording()
        if not audio_bytes:
            logger.info("Áudio vazio ou insuficiente para transcrição.")
            return None

        pipeline_start = time.perf_counter()
        metrics = PipelineMetrics()

        # 2. Transcrição ASR (Groq Whisper Large-v3)
        t_start = time.perf_counter()
        raw_text = self.transcriber.transcribe(audio_bytes)
        metrics.transcription_ms = (time.perf_counter() - t_start) * 1000

        if not raw_text:
            logger.info("Nenhuma fala compreensível detectada.")
            return None

        # 3. Roteamento de Intenção (Gemini Flash: Comando ou Ditação)
        r_start = time.perf_counter()
        intent: VoiceIntent = self.router.route_intent(raw_text, context=context)
        metrics.intent_ms = (time.perf_counter() - r_start) * 1000

        # 4. Execução de Acordo com a Intenção
        e_start = time.perf_counter()
        if intent.type == "command" and intent.action:
            result_str = self._execute_command(intent)
        else:
            self.injector.inject(intent.text)
            result_str = intent.text

        metrics.execution_ms = (time.perf_counter() - e_start) * 1000
        metrics.total_ms = (time.perf_counter() - pipeline_start) * 1000

        logger.info(
            "⚡ PIPELINE CONCLUÍDA EM %.0fms | Transcrição: %.0fms | Intenção/Refino: %.0fms | Execução: %.0fms",
            metrics.total_ms,
            metrics.transcription_ms,
            metrics.intent_ms,
            metrics.execution_ms,
        )
        return result_str

    def _execute_command(self, intent: VoiceIntent) -> str:
        """Executa ações no Windows disparadas por comando de voz."""
        action = intent.action
        param = intent.parameter or ""
        logger.info("Executando comando no Windows: '%s' (parâmetro: '%s')", action, param)

        if action == "open_app":
            self.controller.open_app(param)
        elif action == "open_folder":
            self.controller.open_folder(param)
        elif action == "search_web":
            self.controller.search_web(param)
        elif action == "volume_up":
            self.controller.volume_up()
        elif action == "volume_down":
            self.controller.volume_down()
        elif action == "volume_mute":
            self.controller.volume_mute()
        elif action == "screenshot":
            self.controller.screenshot()
        elif action == "show_desktop":
            self.controller.show_desktop()
        elif action == "close_window":
            self.controller.close_window()
        elif action == "lock_pc":
            self.controller.lock_pc()
        else:
            logger.warning("Ação desconhecida: %s. Tratando como ditação.", action)
            self.injector.inject(intent.text)

        action_tag = action.upper() if action else "UNKNOWN"
        return f"[COMANDO EXECUTADO: {action_tag}] {intent.text}"
