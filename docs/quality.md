# Quality Gates & Padrões — Flow Voice AI

Seguindo as diretrizes do **Vibe Coding Toolkit**:

## 1. Teto de Linhas por Arquivo
- **Máximo de 350 linhas por arquivo de código**.
- Se um módulo crescer além de 350 linhas, fatie em submódulos coesos.

## 2. Padrão de Tratamento de Erros
- Gravação de áudio não deve travar o processo principal se o microfone falhar.
- Falhas na API de ASR ou LLM devem emitir feedback claro (ex: som curto de alerta ou log no system tray) e não fechar o app.

## 3. Verificação Canônica
- Checagem de tipagem com `mypy`.
- Testes unitários com `pytest`.
- Nenhuma feature é declarada concluída sem teste real de execução.
