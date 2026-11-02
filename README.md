# Flow Voice AI

> Clone inteligente do Wispr Flow para Windows potencializado por IA, com push-to-talk, Whisper Large-v3 e refino contextual de texto por LLM.

## Requisitos
- Windows 10/11
- Python 3.10+
- Chave de API Groq (para Whisper ultra veloz) e/ou Google Gemini API

## Estrutura do Projeto
```text
Flow Voice AI/
├── docs/                 # Documentação de arquitetura, qualidade e setup
├── src/                  # Código modular (teto de 350 linhas por arquivo)
│   ├── audio/            # Gravação de áudio e buffer
│   ├── transcriber/      # ASR (Whisper)
│   ├── refiner/          # Polimento contextual por LLM
│   ├── context/          # Detecção da janela ativa no Windows
│   └── injector/         # Injeção de texto no cursor
├── AGENTS.md             # Instruções canônicas para agentes
├── PRODUCT.md            # Especificação de escopo e MVP
└── requirements.txt      # Dependências
```

## Como Executar

1. **Ative o ambiente virtual**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Execute a aplicação**:
   ```powershell
   python -m src.main
   ```

3. **Uso**:
   - Segure **`Ctrl + Espaço`** (ou o atalho configurado no `.env`).
   - Fale naturalmente. Você pode tanto **ditar texto** quanto **dar comandos no Windows**:
     - **Ditação**: Fale o que quer escrever; o texto é refinado e colado no cursor ativo.
     - **Comandos**: 
       - *"Abra o Chrome"* / *"Abra o Notion"* / *"Abra o VS Code"*
       - *"Pesquise sobre inteligência artificial no Google"*
       - *"Abra a pasta Downloads"* / *"Abra Documentos"*
       - *"Aumente o volume"* / *"Abaixe o volume"* / *"Mutar som"*
       - *"Tire um print da tela"* (salva automaticamente em Imagens/Screenshots)
       - *"Mostre a área de trabalho"* (minimiza janelas)
       - *"Feche esta janela"* / *"Bloqueie o computador"*
   - Solte o atalho para executar instantaneamente!

4. **Executar Testes e Quality Gates**:
   ```powershell
   pytest
   mypy src
   ```
