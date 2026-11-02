import time
import threading
import logging
from typing import Optional
import pyperclip
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)


class TextInjector:
    """
    Injetor atômico de texto com suporte pleno a UTF-8 e preservação do clipboard anterior.
    """

    def __init__(self, paste_delay_sec: float = 0.08) -> None:
        self.paste_delay_sec = paste_delay_sec
        self._keyboard = Controller()
        self._lock = threading.Lock()

    def inject(self, text: str) -> bool:
        """
        Insere o texto no cursor ativo via Área de Transferência e restaura o clipboard original.
        """
        if not text:
            return False

        with self._lock:
            # 1. Salva o clipboard anterior com tratamento de exceção (caso seja imagem ou binário)
            previous_clipboard: Optional[str] = None
            try:
                previous_clipboard = pyperclip.paste()
            except Exception as e:
                logger.debug("Não foi possível ler clipboard anterior: %s", e)

            try:
                # 2. Copia o novo texto formatado
                pyperclip.copy(text)

                # Pequena pausa para garantir sincronia do buffer do Windows
                time.sleep(0.02)

                # 3. Dispara atalho de colagem (Ctrl + V)
                with self._keyboard.pressed(Key.ctrl):
                    self._keyboard.tap("v")

                logger.info("Texto injetado com sucesso no cursor (%d caracteres).", len(text))
                return True

            except Exception as e:
                logger.error("Falha ao simular Ctrl+V para injeção de texto: %s", e)
                return False

            finally:
                # 4. Restaura o clipboard em background para não bloquear o fluxo nem ser sobrescrito pelo paste
                if previous_clipboard is not None:
                    threading.Thread(
                        target=self._restore_clipboard_after_delay,
                        args=(previous_clipboard, self.paste_delay_sec),
                        daemon=True,
                    ).start()

    def _restore_clipboard_after_delay(self, content: str, delay: float) -> None:
        """Aguardar o aplicativo consumidor ler o Ctrl+V antes de restaurar o clipboard original."""
        time.sleep(delay)
        try:
            pyperclip.copy(content)
            logger.debug("Clipboard original restaurado.")
        except Exception as e:
            logger.debug("Falha ao restaurar clipboard original: %s", e)
