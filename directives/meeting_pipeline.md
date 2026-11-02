# Diretriz de Gravação e Síntese de Reuniões (Meeting Pipeline)

## 1. Objetivo
Capturar áudio contínuo de reuniões e apresentações (de 15 minutos até 2 horas), combinando o microfone do usuário e o áudio da chamada (fone de ouvido/loopback), sintetizando uma Ata Executiva de alta fidelidade com decisões, tarefas e salvando automaticamente no Obsidian.

## 2. Captura de Áudio Híbrida
- **Microfone**: Captura a voz do usuário via `soundcard.default_microphone()`.
- **Loopback (Ouvido/Participantes)**: Captura o som de conferências (Google Meet, Zoom, Teams) via `soundcard.get_microphone(include_loopback=True)`.
- **Mixagem**: Normalização e fusão dos canais em 16kHz mono para manter o tamanho do arquivo leve (< 25MB por hora).

## 3. Síntese Executiva via Gemini Long-Context
O modelo processa o áudio completo e gera um documento em Markdown puro seguindo a estrutura de elite de atas de liderança:
1. **Frontmatter YAML**: Metadados compatíveis com Obsidian (`tipo: reuniao`, `data`, `duracao`, `tags`).
2. **Resumo Executivo (BLUF)**: 1 a 2 frases com o macro-resultado da reunião.
3. **Decisões Tomadas**: O que foi aprovado, reprovado ou acordado com justificativa sucinta.
4. **Action Items & Tarefas**: Tabela com Tarefa (verbo imperativo), Responsável único e Prazo.
5. **Principais Tópicos & Discussões (Key Takeaways)**: Síntese estruturada por assuntos.
6. **Pontos em Aberto (Parking Lot)**: Dúvidas ou temas postergados para o próximo encontro.
7. **Transcrição na Íntegra**: Registro literal para referência futura e auditoria.

## 4. Integração com Obsidian
- O arquivo gerado é gravado diretamente no cofre do usuário em `00_Inbox/reuniao-YYYY-MM-DD-HHMM.md`.
