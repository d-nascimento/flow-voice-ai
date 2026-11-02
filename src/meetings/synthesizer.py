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

MEETING_SYSTEM_PROMPT = """Você é um especialista em síntese executiva e secretariado de alta liderança.
Sua missão é analisar o áudio gravado de uma reunião/apresentação e gerar uma ATA EXECUTIVA DE ALTO IMPACTO em Markdown puro.

A estrutura DEVE seguir RIGOROSAMENTE o padrão abaixo:

---
tipo: reuniao
data: {DATA_ATUAL}
duracao: {DURACAO}
tags: [reuniao, ata-executiva, flow-voice-ai]
participantes: []
status: concluida
---

# 📋 Ata Executiva: {TITULO_SUGERIDO}

### 🚀 Resumo Executivo (BLUF — Bottom Line Up Front)
> [1 a 2 frases concisas e diretas resumindo o objetivo central da reunião e o macro-resultado alcançado.]

---

### ⚖️ Decisões Tomadas
* **[Título da Decisão 1]**: [Descrição clara do que foi aprovado, rejeitado ou alinhado e o "Porquê" / justificativa sucinta].
* **[Título da Decisão 2]**: [Descrição da decisão e justificativa].

---

### ✅ Matriz de Ação & Próximos Passos (Action Items)
| Tarefa (Começando com Verbo) | Responsável Único | Prazo (YYYY-MM-DD ou Data) |
| :--- | :--- | :--- |
| [Ex: Finalizar documentação da API] | [Nome ou Cargo do Responsável] | [Prazo citado ou 'A definir'] |
| [Ex: Agendar alinhamento com cliente] | [Nome ou Cargo] | [Prazo citado] |

---

### 💡 Principais Tópicos & Discussões (Key Takeaways)
* **[Tópico 1]**:
  - [Ponto relevante discutido]
  - [Dado, métrica ou consideração importante]
* **[Tópico 2]**:
  - [Ponto relevante discutido]

---

### 📌 Dúvidas em Aberto / Estacionamento (Parking Lot)
* [Tópicos que necessitam de mais dados ou foram postergados para a próxima reunião].

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

    def synthesize(self, audio_bytes: bytes, duration_sec: float = 0.0, mime_type: str = "audio/wav") -> str:
        """Sintetiza áudio em memória."""
        if not audio_bytes:
            return ""

        dur_min = int(duration_sec // 60)
        dur_s = int(duration_sec % 60)
        dur_str = f"{dur_min:02d}:{dur_s:02d}" if duration_sec > 0 else "Áudio gravado"
        title = f"Reunião de {datetime.now().strftime('%d/%m/%Y')}"

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        return self._call_gemini([audio_part], title=title, dur_str=dur_str)

    def synthesize_file(self, file_path: Path, custom_title: Optional[str] = None) -> str:
        """Sintetiza áudio a partir de um arquivo carregado pelo usuário (MP3, M4A, WAV, etc.)."""
        if not file_path.exists():
            return f"# Erro\nArquivo não encontrado: {file_path}"

        ext = file_path.suffix.lower()
        mime_type = AUDIO_MIME_MAP.get(ext, "audio/mp3")
        file_size = file_path.stat().st_size
        title = custom_title or file_path.stem.replace("_", " ").replace("-", " ").title()

        logger.info("Processando arquivo de reunião: %s (%s, %.1f MB)", file_path.name, mime_type, file_size / (1024 * 1024))

        # Se menor que 20MB, envia diretamente em memória; se maior, usa a Files API
        if file_size <= 20 * 1024 * 1024:
            data = file_path.read_bytes()
            content_part = types.Part.from_bytes(data=data, mime_type=mime_type)
            return self._call_gemini([content_part], title=title, dur_str="Arquivo Importado")
        else:
            try:
                uploaded = self.client.files.upload(file=str(file_path))
                return self._call_gemini([uploaded], title=title, dur_str="Arquivo Importado")
            except Exception as e:
                logger.error("Falha no upload de arquivo grande para Gemini: %s", e)
                return f"# Erro no Upload de Arquivo\n\n{e}"

    def _call_gemini(self, content_parts: list, title: str, dur_str: str) -> str:
        start_time = time.perf_counter()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        system_instruction = (
            MEETING_SYSTEM_PROMPT.replace("{DATA_ATUAL}", now_str)
            .replace("{DURACAO}", dur_str)
            .replace("{TITULO_SUGERIDO}", title)
        )

        try:
            contents = content_parts + [
                "Ouça o áudio completo da reunião com atenção máxima. Identifique os tópicos, as decisões, os responsáveis pelas tarefas e transcreva fielmente o conteúdo seguindo a estrutura executiva solicitada."
            ]
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    max_output_tokens=8192,
                ),
            )
            result_markdown = response.text.strip() if response.text else ""
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info("Síntese da reunião concluída em %.0fms (%d caracteres).", elapsed_ms, len(result_markdown))
            return result_markdown
        except Exception as e:
            logger.error("Falha na chamada Gemini: %s", e)
            return f"# Erro na Síntese da Reunião\n\n{e}"
