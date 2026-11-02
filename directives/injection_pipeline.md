# Diretriz de Injeção de Texto (Injection Pipeline)

## 1. Objetivo
Inserir o texto refinado diretamente na posição do cursor ativo do usuário, instantaneamente e sem perda de caracteres especiais (UTF-8).

## 2. Padrão de Injeção via Clipboard Seguro
Para garantir suporte completo a acentos, quebras de linha e caracteres unicode em qualquer aplicativo Windows (sem os problemas típicos de simulação tecla-a-tecla com atraso), usamos a injeção atômica via Área de Transferência:
1. **Preservação de Estado**: Salvar o conteúdo atual do clipboard do usuário.
2. **Atualização**: Copiar o texto refinado para o clipboard.
3. **Disparo de Paste**: Simular atalho `Ctrl+V` utilizando eventos de teclado do Windows.
4. **Restauração**: Aguardar tempo curto de processamento do app (~50ms) e restaurar o conteúdo anterior do clipboard do usuário para não perder nada copiado previamente.

## 3. Robustez
- Tratamento de exceções se a área de transferência estiver temporariamente bloqueada por outro processo.
