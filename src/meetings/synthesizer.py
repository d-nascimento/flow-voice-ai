import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

AUDIO_MIME_MAP = {
    ".mp3": "audio/mp3",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".wma": "audio/x-ms-wma",
}

MEETING_SYSTEM_PROMPT = """Você é um analista executivo sênior e especialista em síntese de inteligência do Flow Voice AI.
Sua missão é analisar o áudio gravado e gerar uma ATA EXECUTIVA ADAPTATIVA DE ALTO IMPACTO em Markdown puro.

DIRETRIZ DE ADAPTABILIDADE AO CONTEXTO (CRÍTICO):
Antes de gerar o documento, identifique qual é a NATUREZA da gravação e adapte as seções em conformidade:

1. CASO SEJA UMA REUNIÃO DE TIME / PROJETO:
   - Foco: Decisões colegiadas, alinhamentos e Matriz de Ação rigorosa com Single Owner (Responsável Único) e Prazos.

2. CASO SEJA UMA ENTREVISTA DE CANDIDATO / PROCESSO SELETIVO:
   - Destaque o Perfil do Candidato e mapeie suas Competências Técnicas & Comportamentais (Soft Skills).
   - Avalie o FIT CULTURAL e aderência à vaga (Pontos Fortes vs Pontos de Atenção).
   - Analise a CLAREZA e CONSISTÊNCIA da comunicação (se o candidato foi direto, se demonstrou domínio ou se foi prolixo/inseguro).

3. CASO SEJA UMA APRESENTAÇÃO DE NEGÓCIO, PALESTRA OU EVENTO DE CONTEÚDO:
   - Foco: Tese Central / Proposta de Valor apresentada, Argumentos-chave, Insights acionáveis e Aprendizados para a audiência.

ESTRUTURA CANÔNICA EM MARKDOWN:
---
tipo: reuniao | entrevista | apresentacao
data: {DATA_ATUAL}
tags: [ata-executiva, segundo-cerebro, flow-voice-ai]
participantes: []
status: concluida
---

# 📋 Síntese Executiva: {TITULO_SUGERIDO}

### 🚀 Resumo Executivo (BLUF — Bottom Line Up Front)
> [1 a 2 frases concisas e diretas resumindo o objetivo central e o macro-resultado alcançado.]

---

### ⚖️ Decisões Tomadas / Parecer de Avaliação
* [Decisões aprovadas com justificativa OU, se for entrevista, o Parecer Inicial sobre o candidato e fit com a vaga].

---

### ✅ Matriz de Ação & Próximos Passos
| Tarefa (Começando com Verbo) | Responsável Único | Prazo |
| :--- | :--- | :--- |
| [Ação acordada] | [Responsável] | [Prazo citado ou 'A definir'] |

---

### 💡 Principais Tópicos & Key Takeaways
* **[Tópico / Competência 1]**:
  - [Pontos discutidos, evidências ou dados citados]
* **[Tópico / Competência 2]**:
  - [Pontos discutidos]

---

### 📌 Dúvidas em Aberto / Tópicos de Atenção
* [Pontos postergados, tópicos a checar ou inconsistências observadas].

---

### 📝 Transcrição na Íntegra
{TRANSCRICAO_LITERAL_COM_FALANTES_E_TIMESTAMPS}
"""


class MeetingSynthesizer:
    """
    Sintetizador executivo de reuniões utilizando Gemini Flash Long-Context.
    Processa arquivos completos de áudio gravados ou carregados e gera atas em Markdown.
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

    def synthesize(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        duration_sec: float = 0.0,
    ) -> str:
        """Processa áudio da reunião gravado em memória."""
        if not audio_bytes:
            return ""

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        system_instruction = MEETING_SYSTEM_PROMPT.replace("{DATA_ATUAL}", now_str)

        start_time = time.perf_counter()
        logger.info("Enviando %d bytes de áudio para o Gemini Long-Context...", len(audio_bytes))

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                "Por favor, transcreva e gere a ata executiva adaptativa completa em Markdown puro conforme as diretrizes do sistema.",
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                max_output_tokens=8192,
            ),
        )

        elapsed = time.perf_counter() - start_time
        logger.info("Síntese executiva concluída em %.1fs.", elapsed)
        return response.text or ""

    def synthesize_file(self, file_path: Path) -> str:
        """Processa arquivo de áudio carregado via upload."""
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        ext = file_path.suffix.lower()
        mime_type = AUDIO_MIME_MAP.get(ext, "audio/mp3")

        logger.info("Carregando arquivo de áudio: %s (MIME: %s)", file_path.name, mime_type)
        audio_bytes = file_path.read_bytes()
        return self.synthesize(audio_bytes, mime_type=mime_type)
