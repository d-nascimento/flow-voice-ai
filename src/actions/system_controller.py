import os
import sys
import time
import ctypes
import logging
import urllib.parse
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import ImageGrab

logger = logging.getLogger(__name__)

# Códigos de teclas virtuais no Windows (VK Codes)
VK_LWIN = 0x5B
VK_D = 0x44
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_CONTROL = 0x11
VK_W = 0x57
KEYEVENTF_KEYUP = 0x0002


class SystemController:
    """
    Controlador determinístico de ações no sistema operacional Windows.
    Executa comandos de hardware, multimídia, janelas e abertura de aplicações.
    """

    APP_MAP = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "navegador": "chrome",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "notion": "notion:",
        "obsidian": "obsidian:",
        "spotify": "spotify:",
        "whatsapp": "whatsapp:",
        "terminal": "wt",
        "powershell": "powershell",
        "bloco de notas": "notepad",
        "notepad": "notepad",
        "calculadora": "calc",
        "calc": "calc",
        "explorador": "explorer",
        "arquivos": "explorer",
    }

    FOLDER_MAP = {
        "downloads": Path.home() / "Downloads",
        "documentos": Path.home() / "Documents",
        "documents": Path.home() / "Documents",
        "área de trabalho": Path.home() / "Desktop",
        "desktop": Path.home() / "Desktop",
        "imagens": Path.home() / "Pictures",
        "fotos": Path.home() / "Pictures",
        "pictures": Path.home() / "Pictures",
    }

    @staticmethod
    def _press_key_combo(vk_first: int, vk_second: int) -> None:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_first, 0, 0, 0)
        user32.keybd_event(vk_second, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk_second, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(vk_first, 0, KEYEVENTF_KEYUP, 0)

    @classmethod
    def open_app(cls, app_name: str) -> bool:
        """Abre uma aplicação instalada no Windows."""
        if not app_name:
            return False
        clean_name = app_name.lower().strip()
        target = cls.APP_MAP.get(clean_name, clean_name)
        try:
            os.startfile(target)
            logger.info("Aplicativo iniciado: %s (alvo: %s)", app_name, target)
            return True
        except Exception as e:
            logger.error("Erro ao iniciar aplicativo '%s': %s", app_name, e)
            return False

    @classmethod
    def open_folder(cls, folder_name: str) -> bool:
        """Abre uma pasta do usuário no Explorador de Arquivos."""
        if not folder_name:
            return False
        clean_name = folder_name.lower().strip()
        folder_path = cls.FOLDER_MAP.get(clean_name)
        if not folder_path or not folder_path.exists():
            folder_path = Path.home() / clean_name

        if folder_path.exists():
            try:
                os.startfile(str(folder_path))
                logger.info("Pasta aberta: %s", folder_path)
                return True
            except Exception as e:
                logger.error("Erro ao abrir pasta '%s': %s", folder_path, e)
                return False
        logger.warning("Pasta não encontrada: %s", folder_name)
        return False

    @staticmethod
    def search_web(query: str) -> bool:
        """Realiza uma pesquisa no navegador padrão."""
        if not query:
            return False
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            logger.info("Pesquisa na web iniciada: '%s'", query)
            return True
        except Exception as e:
            logger.error("Erro ao abrir pesquisa na web: %s", e)
            return False

    @staticmethod
    def volume_up(steps: int = 4) -> bool:
        """Aumenta o volume do áudio do sistema."""
        user32 = ctypes.windll.user32
        for _ in range(steps):
            user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
        logger.info("Volume aumentado em %d passos.", steps)
        return True

    @staticmethod
    def volume_down(steps: int = 4) -> bool:
        """Diminui o volume do áudio do sistema."""
        user32 = ctypes.windll.user32
        for _ in range(steps):
            user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            user32.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)
        logger.info("Volume diminuído em %d passos.", steps)
        return True

    @staticmethod
    def volume_mute() -> bool:
        """Alterna o mudo do áudio do sistema."""
        user32 = ctypes.windll.user32
        user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
        logger.info("Mudo de volume alternado.")
        return True

    @staticmethod
    def screenshot() -> Optional[str]:
        """Captura a tela inteira e salva na pasta de Screenshots do usuário."""
        try:
            save_dir = Path.home() / "Pictures" / "Screenshots"
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = save_dir / f"Screenshot_{timestamp}.png"

            shot = ImageGrab.grab(all_screens=True)
            shot.save(file_path, "PNG")
            logger.info("Screenshot salvo com sucesso em: %s", file_path)
            return str(file_path)
        except Exception as e:
            logger.error("Falha ao capturar screenshot: %s", e)
            return None

    @classmethod
    def show_desktop(cls) -> bool:
        """Minimiza todas as janelas para exibir a área de trabalho (Win + D)."""
        cls._press_key_combo(VK_LWIN, VK_D)
        logger.info("Atalho Mostrar Área de Trabalho disparado.")
        return True

    @classmethod
    def close_window(cls) -> bool:
        """Fecha a janela ou aba em foco (Ctrl + W)."""
        cls._press_key_combo(VK_CONTROL, VK_W)
        logger.info("Atalho Fechar Janela/Aba disparado.")
        return True

    @staticmethod
    def lock_pc() -> bool:
        """Bloqueia a estação de trabalho do Windows (Win + L)."""
        try:
            ctypes.windll.user32.LockWorkStation()
            logger.info("Estação de trabalho bloqueada com sucesso.")
            return True
        except Exception as e:
            logger.error("Falha ao bloquear estação de trabalho: %s", e)
            return False
