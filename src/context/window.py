import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Fallback gracioso caso pywin32 falhe em carregar em algum ambiente
try:
    import win32gui
    import win32process
    import win32api
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    logger.warning("pywin32 não disponível. Detecção de janela ativa operará em modo fallback.")


@dataclass
class WindowContext:
    title: str
    process_name: str
    app_category: str
    hwnd: int


class WindowTracker:
    """
    Rastreia e identifica o aplicativo em foco no Windows para contextualizar o refino de IA.
    """

    CATEGORIES = {
        "code_editor": {
            "code.exe", "cursor.exe", "pycharm64.exe", "devenv.exe",
            "sublime_text.exe", "windsurf.exe", "notepad++.exe"
        },
        "terminal": {
            "windowsterminal.exe", "cmd.exe", "powershell.exe",
            "powershell_ise.exe", "mintty.exe", "wt.exe"
        },
        "messaging": {
            "whatsapp.exe", "slack.exe", "discord.exe", "telegram.exe",
            "teams.exe", "skype.exe"
        },
        "notes_and_docs": {
            "obsidian.exe", "notion.exe", "winword.exe", "excel.exe",
            "powerpnt.exe", "onenote.exe", "notepad.exe"
        },
        "browser": {
            "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"
        },
    }

    @classmethod
    def get_active_window(cls) -> WindowContext:
        """
        Retorna informações da janela em primeiro plano do Windows.
        """
        if not PYWIN32_AVAILABLE:
            return WindowContext(title="", process_name="unknown", app_category="general", hwnd=0)

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return WindowContext(title="", process_name="unknown", app_category="general", hwnd=0)

            title = win32gui.GetWindowText(hwnd) or ""
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            process_name = cls._get_process_name_by_pid(pid)
            category = cls._categorize_process(process_name)

            return WindowContext(
                title=title,
                process_name=process_name,
                app_category=category,
                hwnd=hwnd,
            )
        except Exception as e:
            logger.debug("Falha ao inspecionar janela ativa: %s", e)
            return WindowContext(title="", process_name="unknown", app_category="general", hwnd=0)

    @staticmethod
    def _get_process_name_by_pid(pid: int) -> str:
        if pid <= 0:
            return "unknown"
        try:
            handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
            )
            try:
                proc_path = win32process.GetModuleFileNameEx(handle, 0)
                return os.path.basename(proc_path).lower()
            finally:
                win32api.CloseHandle(handle)
        except Exception:
            return "unknown"

    @classmethod
    def _categorize_process(cls, process_name: str) -> str:
        proc_lower = process_name.lower()
        for category, exes in cls.CATEGORIES.items():
            if proc_lower in exes:
                return category
        return "general"
