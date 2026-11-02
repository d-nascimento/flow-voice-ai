import json
import logging
import time
from dataclasses import dataclass
from typing import Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.context.window import WindowContext
from src.dictation.modes import DictationModesManager, MODE_EXACT

logger = logging.getLogger(__name__)

BASE_COMMANDS_SYSTEM_PROMPT = """Você é o roteador de inteligência do Flow Voice AI no Windows.
Sua missão é classificar a fala do usuário em:
1. "command": Uma ordem imperativa para controlar o computador.
2. "dictation": Texto destinado a ser escrito/digitado onde o cursor está localizado.

AÇÕES DE COMANDO SUPORTADAS:
- open_app: Iniciar aplicativo (parameter: "chrome", "code", "notion", "obsidian", "spotify", "whatsapp", "terminal", "notepad", "calc")
- open_folder: Abrir pasta (parameter: "downloads", "documentos", "desktop", "imagens")
- search_web: Pesquisar na web (parameter: o termo da busca)
- volume_up: Aumentar volume
- volume_down: Diminuir volume
- volume_mute: Mutar ou desmutar áudio
- screenshot: Tirar print da tela
- show_desktop: Mostrar área de trabalho (minimizar janelas)
- close_window: Fechar aba ou janela atual
- lock_pc: Bloquear o computador

FORMATO DE RESPOSTA (JSON OBRIGATÓRIO):
{
  "type": "command" | "dictation",
  "action": "open_app" | "open_folder" | "search_web" | "volume_up" | "volume_down" | "volume_mute" | "screenshot" | "show_desktop" | "close_window" | "lock_pc" | null,
  "parameter": "string com o parâmetro se aplicável" | null,
  "text": "Texto processado de acordo com a diretriz do modo ativo. Se for comando: mensagem curta de confirmação."
}

Se houver qualquer dúvida se é comando ou conversa/texto, prefira sempre "dictation".
"""


@dataclass
class VoiceIntent:
    type: str  # "command" ou "dictation"
    action: Optional[str] = None
    parameter: Optional[str] = None
    text: str = ""


class IntentRouter:
    """
    Roteador de inteligência que detecta comandos no SO ou processa o texto ditado
    segundo a Skill ativa:
    - MODE_EXACT: Ditado Fiel (Core)
    - MODE_POLISH: Otimização de Texto
    - MODE_PROMPT: Prompt Engineering
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = GEMINI_MODEL,
        modes_mgr: Optional[DictationModesManager] = None,
    ) -> None:
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.modes_mgr = modes_mgr or DictationModesManager()
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY não configurada no ambiente ou .env.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def route_intent(self, raw_text: str, context: Optional[WindowContext] = None) -> VoiceIntent:
        cleaned = raw_text.strip()
        if not cleaned:
            return VoiceIntent(type="dictation", text="")

        # Heurísticas rápidas para comandos comuns
        lower = cleaned.lower().strip(".?!, ")
        if lower in ("aumentar volume", "aumenta o volume", "mais volume"):
            return VoiceIntent(type="command", action="volume_up", text="Volume aumentado")
        if lower in ("diminuir volume", "diminui o volume", "menos volume"):
            return VoiceIntent(type="command", action="volume_down", text="Volume diminuído")
        if lower in ("mutar áudio", "mutar som", "mudo", "desmutar"):
            return VoiceIntent(type="command", action="volume_mute", text="Áudio alternado")
        if lower in ("tirar print", "print da tela", "screenshot", "capturar tela"):
            return VoiceIntent(type="command", action="screenshot", text="Screenshot capturado")
        if lower in ("mostrar área de trabalho", "minimizar tudo", "mostrar desktop"):
            return VoiceIntent(type="command", action="show_desktop", text="Desktop exibido")
        if lower in ("fechar janela", "fecha essa janela", "fechar aba"):
            return VoiceIntent(type="command", action="close_window", text="Janela fechada")
        if lower in ("bloquear computador", "bloquear pc", "bloquear tela"):
            return VoiceIntent(type="command", action="lock_pc", text="Computador bloqueado")

        try:
            # Recupera a instrução do modo selecionado (Core, Polish ou Prompt)
            mode_instruction = self.modes_mgr.get_system_instruction()
            system_instruction = (
                f"{BASE_COMMANDS_SYSTEM_PROMPT}\n\n"
                f"MODO DE DITADO ATIVO: [{self.modes_mgr.active_mode.upper()}]\n"
                f"DIRETRIZ DA SKILL DE DITADO:\n{mode_instruction}"
            )

            category_info = context.app_category if context else "general"
            app_info = f"App ativo: {context.process_name} | Categoria: {category_info}" if context else "Geral"
            prompt_content = f"Contexto do Cursor: [{app_info}]\nFala Transcrita do Usuário: \"{cleaned}\""

            # Temperatura: 0.0 para Fiel (Core) para zero alucinações, 0.2 para Polish/Prompt para riqueza textual
            temp = 0.0 if self.modes_mgr.active_mode == MODE_EXACT else 0.2

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=temp,
                    max_output_tokens=1024,
                ),
            )

            raw_resp = response.text or "{}"
            data = json.loads(raw_resp.strip())
            return VoiceIntent(
                type=data.get("type", "dictation"),
                action=data.get("action"),
                parameter=data.get("parameter"),
                text=data.get("text", cleaned),
            )
        except Exception as e:
            logger.warning("Falha no roteamento inteligente com Gemini: %s. Fallback para ditação original.", e)
            return VoiceIntent(type="dictation", text=cleaned)
