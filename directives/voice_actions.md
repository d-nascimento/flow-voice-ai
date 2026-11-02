# Diretriz de Ações por Voz no Windows (Voice Actions)

## 1. Objetivo
Permitir que o usuário controle o sistema operacional Windows através da fala natural capturada pelo push-to-talk, discernindo instantaneamente entre comandos de sistema e ditação de texto.

## 2. Roteamento de Intenção (Intent Routing)
O Gemini classifica o texto transcrito em duas categorias fundamentais:
- **`dictation` (Ditação)**: Texto destinado a ser escrito onde o cursor está posicionado. Deve receber refino e injeção via clipboard.
- **`command` (Comando)**: Instrução imperativa para executar uma ação no Windows (ex: abrir aplicativo, ajustar volume, fechar janela, pesquisar na web, capturar tela).

## 3. Catálogo de Ações Suportadas
| Ação (`action`) | Descrição | Parâmetro (`parameter`) |
| :--- | :--- | :--- |
| `open_app` | Inicia um aplicativo no Windows | Nome do app (ex: `chrome`, `code`, `notion`, `obsidian`, `spotify`, `whatsapp`) |
| `open_folder` | Abre uma pasta do sistema no Explorador | `downloads`, `documents`, `desktop`, `pictures` |
| `search_web` | Abre uma nova aba no navegador com a pesquisa | Termo da busca (ex: `notícias do dia`) |
| `volume_up` | Aumenta o volume do áudio do sistema | Nenhum |
| `volume_down` | Diminui o volume do áudio do sistema | Nenhum |
| `volume_mute` | Ativa ou desativa o mudo do som | Nenhum |
| `screenshot` | Captura a tela inteira e salva em Imagens/Screenshots | Nenhum |
| `show_desktop` | Minimiza todas as janelas (Win + D) | Nenhum |
| `close_window` | Fecha a aba ou janela em foco (Ctrl + W / Alt + F4) | Nenhum |
| `lock_pc` | Bloqueia a sessão do Windows (Win + L) | Nenhum |

## 4. Segurança e Robustez
1. Comandos desconhecidos ou ambíguos devem cair com segurança no modo `dictation`.
2. Falhas na abertura de aplicativos ou atalhos devem registrar aviso e não travar o processo principal.
