import logging
import time
from typing import Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.context.window import WindowContext

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é o motor de refino contextual do Flow Voice AI (padrão Wispr Flow).
Sua missão é transformar a fala transcrita em texto polido, natural e perfeitamente formatado.

DIRETRIZES FUNDAMENTAIS:
1. Remova todos os vícios de linguagem, hesitações e gaguejos (ex: "ééé", "tipo assim", "humm", "sabe?", repetições involuntárias).
2. Corrija a pontuação, maiúsculas e concordância gramatical com extrema fidelidade ao sentido original.
3. NUNCA adicione explicações, comentários, introduções ("Aqui está:") ou aspas ao redor do texto gerado.
4. Responda ESTRITAMENTE com o texto final pronto para ser colado no aplicativo.

ADAPTAÇÃO CONTEXTUAL:
- messaging (WhatsApp/Slack/Discord): Tom ágil, informal e fluido, pontuação natural.
- code_editor (VS Code/Cursor): Preserve termos técnicos em inglês, convenções de código (camelCase, snake_case) e formatação de comentários/mensagens de commit.
- terminal (PowerShell/CMD): Se a fala ditar comandos, forneça sintaxe de comando exata e sem pontuação gramatical indevida.
- notes_and_docs (Word/Obsidian/Notion): Texto estruturado, parágrafos bem pontuados e listas organizadas se ditadas.
- browser/general: Fluente, claro e direto ao ponto.
"""


class ContextRefiner:
    """
    Refinador contextual de texto utilizando Google Gemini Flash.
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
        """
        Refina o texto transcrito com base no contexto da janela ativa.
        Se ocorrer erro ou timeout, retorna com segurança o raw_text original.
        """
        cleaned = raw_text.strip()
        if not cleaned:
            return ""

        # Se for apenas 1 ou 2 palavras simples, não precisa do overhead de LLM
        words = cleaned.split()
        if len(words) <= 2 and not any(w.lower() in {"é", "hum", "humm", "tipo"} for w in words):
            return cleaned

        start_time = time.perf_counter()
        try:
            category_info = context.app_category if context else "general"
            app_info = f"App: {context.process_name} | Categoria: {category_info}" if context else "Geral"

            user_prompt = f"Contexto do Cursor: [{app_info}]\nTexto falado transcrito: {cleaned}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=1024,
                ),
            )

            refined_text = response.text.strip() if response.text else cleaned
            # Remove aspas acidentais se o modelo colocar o texto entre aspas
            if refined_text.startswith('"') and refined_text.endswith('"') and len(refined_text) > 2:
                refined_text = refined_text[1:-1].strip()

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info("Refino Gemini concluído em %.1fms: '%s'", elapsed_ms, refined_text)
            return refined_text

        except Exception as e:
            logger.warning("Falha no refino Gemini (retornando texto bruto como fallback): %s", e)
            return cleaned
