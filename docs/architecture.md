# Arquitetura — Flow Voice AI

## Visão Geral do Pipeline

```
[ Usuário ] ➔ Segura Hotkey ➔ Grava Áudio no Buffer
            ➔ Solta Hotkey  ➔ Dispara Pipeline Assíncrona
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
[ ASR Transcriber ]                                      [ OS Context Detector ]
Whisper Large-v3 (Groq API)                              Captura App Ativo (Win32)
    │                                                               │
    └───────────────────────────────┬───────────────────────────────┘
                                    ▼
                         [ LLM Context Refiner ]
                         Gemini Flash / Llama 3
                         (Remove hesitações, pontua,
                          adapta ao formato do App)
                                    │
                                    ▼
                         [ Text Injector ]
                         Simulação de Paste no Cursor
```

## Módulos
- `src.audio.recorder`: Gerenciador de gravação com sounddevice e stream em memória.
- `src.transcriber.whisper`: Cliente ASR com suporte a Groq Cloud e Faster-Whisper local.
- `src.context.window`: Módulo de inspeção de processos e títulos de janela ativa no Windows.
- `src.refiner.llm`: Engine de prompts com dicionário personalizado e regras por app.
- `src.injector.keyboard`: Módulo de injeção direta no clipboard e disparo de eventos de tecla.
