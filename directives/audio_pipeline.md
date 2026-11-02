# Diretriz de Captura de Áudio (Audio Pipeline)

## 1. Objetivo
Capturar áudio do microfone do usuário com o menor overhead e sem latência de I/O em disco, ativado pelo padrão Push-to-Talk (PTT).

## 2. Parâmetros Canônicos
- **Taxa de amostragem (Sample Rate)**: 16.000 Hz (16 kHz). Este é o padrão nativo dos modelos Whisper, dispensando reamostragem.
- **Canais**: 1 (Mono).
- **Formato**: PCM 16-bit com sinal (`int16` ou float32 convertido).
- **Armazenamento**: Stream direto em memória (`io.BytesIO`), gravado em formato WAV.

## 3. Regras de Execução
1. Quando o atalho for pressionado (`on_press`), o buffer em memória é limpo e a gravação inicia imediatamente em thread secundária.
2. Quando o atalho for solto (`on_release`), o stream é fechado imediatamente e os bytes WAV são consolidados.
3. Se a duração for inferior a 0.3 segundos ou o volume médio (RMS) for próximo de zero (silêncio absoluto), a gravação é descartada sem consumir chamadas de API.
4. Falhas de hardware ou microfone não devem derrubar o processo principal; deve-se registrar log de aviso e retornar buffer vazio de forma graciosa.
