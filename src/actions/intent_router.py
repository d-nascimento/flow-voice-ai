import json
import logging
import time
from dataclasses import dataclass
from typing import Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.context.window import WindowContext

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """Você é o roteador de intenção e cérebro do Flow Voice AI no Windows.
Sua função é classificar a fala transcrita em:
1. "command": Uma ordem imperativa para controlar o computador.
2. "dictation": Texto destinado a ser escrito/digitado onde o cursor está localizado.

REGRA DE PRESERVAÇÃO RIGOROSA DA FALA (FIDELIDADE MÁXIMA):
- Seja EXTREMAMENTE fiel ao que o usuário falou. NÃO invente, não reescreva com outras palavras e não faça paráfrase.
- Apenas corrija pontuação básica, maiúsculas no início de frases e remova hesitações puras (ex: "ééé", "humm", "tipo").
- Preserve o vocabulário, o tom, as gírias e o estilo original do usuário exatamente como dito.
- NUNCA TRADUZA! Se a fala for em inglês, o texto DEVE PERMANECER 100% EM INGLÊS. Se for em português, PERMANECE EM PORTUGUÊS.

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

REGRAS DE RESPOSTA (JSON OBRIGATÓRIO):
{
  "type": "command" | "dictation",
  "action": "open_app" | "open_folder" | "search_web" | "volume_up" | "volume_down" | "volume_mute" | "screenshot" | "show_desktop" | "close_window" | "lock_pc" | null,
  "parameter": "string com o parâmetro se aplicável" | null,
  "text": "Se for dictation: o texto fielmente transcrito e pontuado. Se for command: mensagem curta de confirmação."
}

Se houver qualquer dúvida se é comando ou ditação, escolha SEMPRE "dictation".
"""


@dataclass
class VoiceIntent:
    type: str  # "command" ou "dictation"
    action: Optional[str] = None
    parameter: Optional[str] = None
    text: str = ""


class IntentRouter:
    """
    Roteador de inteligência que decide se a fala é um comando do Windows ou texto de ditação fiel.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL) -> None:
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
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

        # Heurísticas rápidas para comandos ultra comuns (economia de latência)
        lower = cleaned.lower().strip(".?!, ")
        if lower in ("aumentar volume", "aumenta o volume", "mais volume"):
            return VoiceIntent(type="command", action="volume_up", text="Volume aumentado.")
        if lower in ("abaixar volume", "abaixa o volume", "diminuir volume", "menos volume"):
            return VoiceIntent(type="command", action="volume_down", text="Volume diminuído.")
        if lower in ("mutar som", "mudo", "tirar som", "desmutar", "mutar áudio"):
            return VoiceIntent(type="command", action="volume_mute", text="Áudio mutado/desmutado.")
        if lower in ("tirar print", "tira print", "captura de tela", "screenshot", "print da tela"):
            return VoiceIntent(type="command", action="screenshot", text="Captura de tela realizada.")
        if lower in ("mostrar área de trabalho", "mostra a área de trabalho", "minimizar tudo", "mostrar desktop"):
            return VoiceIntent(type="command", action="show_desktop", text="Exibindo área de trabalho.")
        if lower in ("fechar janela", "fecha a janela", "fechar aba", "fecha a aba", "fechar essa janela"):
            return VoiceIntent(type="command", action="close_window", text="Janela/aba fechada.")
        if lower in ("bloquear computador", "travar tela", "bloquear pc", "bloquear a tela"):
            return VoiceIntent(type="command", action="lock_pc", text="Computador bloqueado.")

        try:
            category_info = context.app_category if context else "general"
            app_info = f"App ativo: {context.process_name} ({category_info})" if context else "Geral"
            prompt = f"Contexto: {app_info}\nFala original transcrita: \"{cleaned}\""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=INTENT_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.0,
                    max_output_tokens=512,
                ),
            )

            raw_json = response.text.strip() if response.text else "{}"
            data = json.loads(raw_json)

            intent_type = data.get("type", "dictation")
            action = data.get("action")
            parameter = data.get("parameter")
            refined_text = data.get("text", cleaned)

            return VoiceIntent(
                type=intent_type,
                action=action,
                parameter=parameter,
                text=refined_text or cleaned,
            )
        except Exception as e:
            logger.warning("Falha no roteamento de intenção com Gemini: %s. Fallback para transcrição original.", e)
            return VoiceIntent(type="dictation", text=cleaned)
