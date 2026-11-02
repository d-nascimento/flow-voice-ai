import logging
import time
from typing import Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.context.window import WindowContext

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é o pontuador e limpador natural do Flow Voice AI.
Sua missão é apenas pontuar corretamente a fala do usuário e remover hesitações puras (ex: "ééé", "humm", "tipo").

DIRETRIZES ESTREITAS:
1. FIDELIDADE MÁXIMA: NUNCA altere as palavras, não faça paráfrase, não reescreva com vocabulário mais sofisticado e não resuma. Mantenha exatamente o texto que a pessoa falou.
2. NUNCA TRADUZA: Se a fala for em inglês, permanece em inglês. Se for em português, permanece em português.
3. Não adicione saudações, introduções ("Aqui está:") nem aspas.
4. Responda ESTRITAMENTE com o texto falado pontuado.
"""


class ContextRefiner:
    """
    Refinador contextual mínimo de texto para pontuação sem artificialidades.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = GEMINI_MODEL,
    ) -> None:
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

    def refine(self, raw_text: str, context: Optional[WindowContext] = None) -> str:
        cleaned = raw_text.strip()
        if not cleaned:
            return ""

        words = cleaned.split()
        if len(words) <= 2 and not any(w.lower() in {"é", "hum", "humm", "tipo"} for w in words):
            return cleaned

        try:
            category_info = context.app_category if context else "general"
            app_info = f"App: {context.process_name} | Categoria: {category_info}" if context else "Geral"
            user_prompt = f"Contexto: [{app_info}]\nTexto falado: {cleaned}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.0,
                    max_output_tokens=1024,
                ),
            )

            refined_text = response.text.strip() if response.text else cleaned
            if refined_text.startswith('"') and refined_text.endswith('"') and len(refined_text) > 2:
                refined_text = refined_text[1:-1].strip()

            return refined_text
        except Exception as e:
            logger.warning("Falha na pontuação com Gemini: %s. Mantendo transcrição original.", e)
            return cleaned
