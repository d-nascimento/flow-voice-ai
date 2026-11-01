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

## Como Iniciar
Consulte o guia detalhado em [`docs/setup.md`](docs/setup.md).
