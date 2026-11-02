import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_VAULT = Path.home() / "OneDrive" / "Documentos" / "Obsidian" / "2nd Brain"


class MeetingExporter:
    """
    Exportador de atas de reuniões para o cofre do Obsidian e backup local.
    """

    def __init__(self, vault_path: Optional[Path] = None) -> None:
        self.vault_path = vault_path or DEFAULT_VAULT

    def export(self, markdown_content: str, custom_filename: Optional[str] = None) -> Path:
        """
        Salva a ata no cofre do Obsidian (na pasta 00_Inbox) e em backup local.
        Retorna o caminho do arquivo salvo no Obsidian (ou local se o vault não existir).
        """
        timestamp_slug = datetime.now().strftime("%Y-%m-%d-%H%M")
        filename = custom_filename or f"reuniao-{timestamp_slug}.md"

        # 1. Backup local de segurança dentro do projeto
        local_dir = Path(__file__).resolve().parent.parent.parent / "meetings"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_file = local_dir / filename
        local_file.write_text(markdown_content, encoding="utf-8")
        logger.info("Backup local da reunião salvo em: %s", local_file)

        # 2. Salva no cofre do Obsidian
        if self.vault_path.exists():
            inbox_dir = self.vault_path / "00_Inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            obsidian_file = inbox_dir / filename
            obsidian_file.write_text(markdown_content, encoding="utf-8")
            logger.info("Ata salva com sucesso no Obsidian: %s", obsidian_file)
            return obsidian_file

        return local_file
