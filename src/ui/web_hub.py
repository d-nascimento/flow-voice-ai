import sys
import logging
import threading
from pathlib import Path
from typing import Optional, Any
import webview

from src.web.bridge import WebBridge

logger = logging.getLogger(__name__)

HTML_PATH = Path(__file__).resolve().parent.parent / "web" / "index.html"
ICON_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico"


class WebHubManager:
    """
    Gerenciador da Janela Moderna do Hub em Edge WebView2 (Chromium).
    Empacotado em background thread para coexistir com o Tray e a VoicePipeline.
    """

    def __init__(self, bridge: Optional[WebBridge] = None) -> None:
        self.bridge = bridge or WebBridge()
        self.window: Optional[Any] = None
        self._is_open = False
        self._lock = threading.Lock()

    def show(self) -> None:
        """Abre ou traz para frente a janela Web do Hub."""
        with self._lock:
            if self.window is not None and self._is_open:
                try:
                    self.window.restore()
                    self.window.show()
                    return
                except Exception as e:
                    logger.debug("Janela anterior descartada: %s", e)
                    self.window = None

            threading.Thread(target=self._launch_webview, daemon=True).start()

    def _launch_webview(self) -> None:
        try:
            self.window = webview.create_window(
                title="Flow Voice AI — Hub",
                url=str(HTML_PATH),
                js_api=self.bridge,
                width=880,
                height=640,
                resizable=True,
                frameless=False,
                easy_drag=False,
                text_select=True,
                background_color="#eeebe3",
            )
            self.bridge.set_window(self.window)
            self._is_open = True

            def on_closing() -> None:
                self._is_open = False

            self.window.events.closing += on_closing
            webview.start(gui="edgechromium", debug=False)
        except Exception as e:
            logger.error("Falha ao abrir Hub em WebView2: %s", e)
        finally:
            self._is_open = False
            self.window = None

    def add_history(self, text: str, is_command: bool = False) -> None:
        self.bridge.add_history_entry(text, is_command=is_command)
