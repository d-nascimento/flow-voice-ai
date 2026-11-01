# Flow Voice AI — Especificação do Produto

## 1. Problema
Os sistemas convencionais de ditação de voz (Samsung Keyboard, Windows Speech Recognition, modelos Whisper puros) transcrevem literalmente o áudio, incluindo vícios de fala ("ééé", "tipo assim"), pontuação inconsistente, falta de formatação adaptativa e erros em nomes próprios ou termos técnicos. Isso obriga o usuário a editar o texto manualmente após falar, destruindo o ganho de produtividade.

## 2. Solução: O Padrão Wispr Flow
O **Flow Voice AI** é um clone de alta performance do Wispr Flow que introduz uma **camada de refino contextual de IA**:
1. O usuário aperta e segura uma tecla global (push-to-talk).
2. Fala naturalmente em português ou inglês.
3. Ao soltar a tecla, o áudio é transcrito em milissegundos via Whisper Large-v3.
4. Um modelo de linguagem (LLM) refina o texto considerando:
   - O aplicativo em foco (WhatsApp, Word, VS Code, Slack, Obsidian).
   - O estilo do usuário e vocabulário personalizado.
   - A remoção inteligente de hesitações e vícios de linguagem.
5. O texto polido é injetado diretamente no cursor do usuário instantaneamente.

## 3. Critérios de Aceitação do MVP
- [ ] Ativação global via atalho de teclado push-to-talk.
- [ ] Transcrição de áudio em < 400ms.
- [ ] Refino de texto em < 500ms (tempo total < 1s).
- [ ] Detecção da janela ativa no Windows.
- [ ] Injeção direta no campo de texto ativo sem erros de codificação de caracteres (UTF-8 com suporte pleno ao Português).
