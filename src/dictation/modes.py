import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "modes_config.json"

MODE_EXACT = "exact"      # 1. Ditado Fiel (Core do Wispr Flow / Superflow)
MODE_POLISH = "polish"    # 2. Otimização de Texto (Reescrita fluida e formal)
MODE_PROMPT = "prompt"    # 3. Prompt Engineering (Estruturação para LLMs)

MODE_DESCRIPTIONS = {
    MODE_EXACT: {
        "title": "Ditado Fiel (Core)",
        "badge": "Padrão",
        "description": "Fidelidade absoluta às palavras faladas. Ajusta apenas vírgulas, pontos e ortografia básica sem alterar vocabulário ou ordem.",
        "icon": "mic",
    },
    MODE_POLISH: {
        "title": "Otimização de Texto",
        "badge": "Reescrita",
        "description": "Reorganiza o raciocínio, troca termos se necessário e transforma pensamentos soltos em um texto formal, coeso e fluido.",
        "icon": "sparkles",
    },
    MODE_PROMPT: {
        "title": "Prompt Engineering",
        "badge": "Para LLMs",
        "description": "Entende o objetivo por trás da fala e estrutura automaticamente como um prompt profissional (Role, Task, Contexto e Critérios).",
        "icon": "bot",
    },
}

SYSTEM_INSTRUCTIONS = {
    MODE_EXACT: """Você é o pontuador e corretor ortográfico do Flow Voice AI (Core).
Sua missão é estritamente de PONTUAÇÃO e ORTOGRAFIA BÁSICA.

REGRAS RÍGIDAS:
1. FIDELIDADE ABSOLUTA: Mantenha exatamente as palavras que o usuário falou. PROIBIDO trocar palavras por sinônimos, proibido mudar a ordem das frases e proibido resumir ou embelezar.
2. Apenas insira pontos, vírgulas, pontos de interrogação e maiúsculas adequadas.
3. Remova apenas hesitações puras (ex: "ééé", "humm", "tipo").
4. NUNCA TRADUZA: Se o usuário falou em inglês, mantenha em inglês. Se falou em português, mantenha em português.
5. Devolva apenas o texto sem aspas ou introduções.
""",

    MODE_POLISH: """Você é o otimizador e redator sênior do Flow Voice AI.
Sua missão é transformar fragmentos de fala e pensamentos ditados em um texto escrito formal, fluido, elegante e coeso.

DIRETRIZES DE OTIMIZAÇÃO:
1. Você TEM LIBERDADE para trocar palavras, enriquecer o vocabulário e reordenar sentenças para melhorar o encadeamento lógico e a fluidez do raciocínio.
2. Elimine ambiguidades, redundâncias, gaguejos e vícios de linguagem.
3. Se a pessoa falou vários tópicos ou ideias em sequência, estruture em parágrafos bem construídos ou tópicos coesos quando fizer sentido.
4. NUNCA TRADUZA: Mantenha o idioma no qual a pessoa falou (inglês permanece em inglês, português em português).
5. Devolva estritamente o texto reescrito, pronto para ser lido ou enviado em um email, relatório ou mensagem formal.
""",

    MODE_PROMPT: """Você é um especialista em Prompt Engineering do Flow Voice AI.
Sua missão é compreender a intenção, os requisitos e os objetivos por trás das ideias soltas faladas pelo usuário e convertê-los em um PROMPT PERFEITO para LLMs (como Claude, Gemini, GPT-4, Antigravity).

ESTRUTURA DO PROMPT GERADO:
- **Role**: O papel especializado que o modelo deve assumir.
- **Task**: O objetivo principal claro e direto.
- **Context & Constraints**: Detalhes, regras e restrições extraídos da fala.
- **Expected Output**: O formato esperado para a resposta.

DIRETRIZES:
1. Reorganize e complete lacunas lógicas para que o prompt seja inequívoco e altamente executável.
2. NUNCA TRADUZA: Se o usuário falou em português, o prompt resultante deve ser estruturado em português; se falou em inglês, em inglês.
3. Responda ESTRITAMENTE com o prompt final pronto para ser colado na IA. Não adicione saudações como 'Aqui está seu prompt'.
""",
}


class DictationModesManager:
    """
    Gerencia e persiste a seleção entre Ditado Fiel, Otimização de Texto e Prompt Engineering.
    """

    def __init__(self, config_path: Path = CONFIG_FILE) -> None:
        self.config_path = config_path
        self.active_mode: str = MODE_EXACT  # Padrão: Ditado Fiel (Core)
        self._load()

    def _load(self) -> None:
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                mode = data.get("active_mode", MODE_EXACT)
                if mode in (MODE_EXACT, MODE_POLISH, MODE_PROMPT):
                    self.active_mode = mode
            except Exception as e:
                logger.warning("Falha ao carregar modes_config.json: %s", e)

    def save(self) -> None:
        try:
            data = {"active_mode": self.active_mode}
            self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error("Erro ao salvar modes_config.json: %s", e)

    def set_active_mode(self, mode: str) -> bool:
        if mode in (MODE_EXACT, MODE_POLISH, MODE_PROMPT):
            self.active_mode = mode
            self.save()
            return True
        return False

    def get_system_instruction(self) -> str:
        return SYSTEM_INSTRUCTIONS.get(self.active_mode, SYSTEM_INSTRUCTIONS[MODE_EXACT])

    def get_modes_data(self) -> Dict[str, Any]:
        return {
            "active_mode": self.active_mode,
            "modes": MODE_DESCRIPTIONS,
        }
