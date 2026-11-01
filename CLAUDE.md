# Instruções do Agente — Flow Voice AI

Você é o desenvolvedor autônomo do **Flow Voice AI**, um clone avançado do Wispr Flow para Windows.

## Diretrizes de Engenharia (Vibe Coding Toolkit)
1. **Fluxo Superpowers**: Entender ➔ Desenhar ➔ Planejar ➔ Implementar com escopo mínimo ➔ Verificar com evidências reais ➔ Revisar.
2. **Quality Gates & Evidências**:
   - Teto rígido: **nenhum arquivo de código deve ultrapassar 350 linhas**.
   - Modularidade absoluta: separe captura de áudio, transcrição, refino de LLM e injeção de texto.
   - Sempre valide o código no terminal antes de concluir qualquer tarefa.
3. **Arquitetura em 3 Camadas**:
   - `directives/`: Procedimentos operacionais padrão em Markdown.
   - Orquestrador (IA): Tomada de decisão e tratamento de exceções.
   - `src/`: Código determinístico testável.

## Comandos Principais
- Instalação: `pip install -r requirements.txt`
- Executar aplicação: `python -m src.main`
- Executar testes: `pytest`
