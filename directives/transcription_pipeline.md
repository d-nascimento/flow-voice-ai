# Diretriz de Transcrição ASR (Transcription Pipeline)

## 1. Objetivo
Converter os bytes de áudio WAV em texto bruto com latência inferior a 400ms, preservando termos técnicos e idioma falado.

## 2. Provedor e Modelo
- **Provedor**: Groq Cloud API.
- **Modelo**: `whisper-large-v3-turbo` (ou `whisper-large-v3`).
- **Idioma padrão**: `pt` (Português), com capacidade multilíngue automática se o áudio for em inglês.

## 3. Regras de Execução
1. O payload de áudio deve ser transmitido como tupla `(filename, bytes, "audio/wav")` diretamente da memória RAM.
2. Em caso de timeout (> 3 segundos) ou falha de conexão na API:
   - Capturar a exceção sem quebrar o loop de execução.
   - Retornar string vazia e emitir feedback de erro.
3. Se a transcrição retornar apenas ruídos como `"[música]"`, `"[silêncio]"` ou caracteres vazios, abortar as etapas subsequentes de refino e injeção.
