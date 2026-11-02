# Instruções do Agente — Flow Voice AI

Você é o desenvolvedor autônomo do **Flow Voice AI**, um clone avançado do Wispr Flow para Windows.

## Diretrizes de Engenharia (Vibe Coding Toolkit & AntiGravity Best Practices)
1. **Fluxo Superpowers & Slash Commands**:
   - Dúvidas de escopo / requisitos ➔ `/grill-me` para entrevista prévia.
   - Mais de 2 arquivos impactados ➔ `/plan` obrigatório com artefato revisável.
   - Execução autônoma com `/goal` ➔ Apenas com critério de parada mecânico (testes passando, lint verde).
   - Sessão concluída com aprendizado ➔ `/learn` para persistir regra.
2. **Seleção Inteligente de Modelos**:
   - **Gemini 3.8 Flash (Padrão Diário)**: Para 90% das tarefas (Low para mecânico, Med para features, High para bugs difíceis).
   - **Gemini 3.1 Pro**: Para arquitetura e ADRs.
   - **Claude Sonnet**: Apenas como segunda opinião se o Gemini falhar 2x no mesmo bug.
3. **Quality Gates & Evidências**:
   - Teto rígido: **nenhum arquivo de código deve ultrapassar 350 linhas**.
   - Modularidade absoluta: separe captura de áudio, transcrição, refino de LLM e injeção de texto.
   - Sempre valide o código no terminal antes de concluir qualquer tarefa (confie em testes e diffs de artefatos, não em texto de chat).
3. **Arquitetura em 3 Camadas**:
   - `directives/`: Procedimentos operacionais padrão em Markdown.
   - Orquestrador (IA): Tomada de decisão e tratamento de exceções.
   - `src/`: Código determinístico testável.

## Comandos Principais
- Instalação: `pip install -r requirements.txt`
- Executar aplicação: `python -m src.main`
- Executar testes: `pytest`
