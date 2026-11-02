# Diretriz de Refino de Texto Contextual (Refinement Pipeline)

## 1. Objetivo
Transformar a transcrição literal em texto polido, inteligente e adaptado ao contexto do aplicativo onde o cursor está localizado.

## 2. Provedor e Modelo
- **Provedor**: Google Gemini API via SDK `google-genai`.
- **Modelo**: `gemini-3.5-flash-lite` (ou `gemini-3.5-flash`).

## 3. Regras de Refino (System Instructions)
1. **Remoção de vícios de fala**: Eliminar hesitações como "humm", "tipo assim", "ééé", "então", repetições acidentais e autocorreções de fala.
2. **Preservação de intenção**: Nunca adicionar comentários, saudações de IA (ex: "Aqui está o texto:") ou inventar fatos. Devolver estritamente o texto formatado.
3. **Adaptação Contextual por Janela Ativa**:
   - **Editores de Código / Terminais** (`code.exe`, `windowsterminal.exe`, `cmd.exe`): Se for ditação de comando ou código, manter formatação técnica precisa; se for comentário, formatar de forma concisa.
   - **Mensageiros Rápidos** (`whatsapp.exe`, `slack.exe`, `telegram.exe`, `discord.exe`): Pontuação natural e parágrafos curtos, sem formalismo excessivo.
   - **Documentos & Notas** (`winword.exe`, `obsidian.exe`, `notion.exe`): Estrutura formal, parágrafos bem pontuados e listas organizadas se ditadas.
   - **Navegadores & Pesquisa** (`chrome.exe`, `msedge.exe`, `firefox.exe`): Concisão direta para buscas ou respostas limpas para formulários.
