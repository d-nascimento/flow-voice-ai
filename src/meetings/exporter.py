import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_OBSIDIAN_VAULT = Path.home() / "OneDrive" / "Documentos" / "Obsidian" / "2nd Brain"
GDRIVE_VAULT = Path("G:/Meu Drive/2nd Brain")


class MeetingExporter:
    """
    Exportador de atas de reuniões para o cofre do Segundo Cérebro:
    1. Sincronização direta na pasta Google Drive (G:/Meu Drive/2nd Brain/00_Inbox).
    2. Sincronização no cofre local Obsidian (00_Inbox).
    3. Backup de segurança local na pasta do projeto (meetings/).
    """

    def __init__(
        self,
        vault_path: Optional[Path] = None,
        gdrive_vault: Optional[Path] = None,
    ) -> None:
        self.vault_path = vault_path or DEFAULT_OBSIDIAN_VAULT
        self.gdrive_vault = gdrive_vault or GDRIVE_VAULT

    def export(self, markdown_content: str, custom_filename: Optional[str] = None) -> Path:
        timestamp_slug = datetime.now().strftime("%Y-%m-%d-%H%M")
        filename = custom_filename or f"reuniao-{timestamp_slug}.md"

        # 1. Backup local de segurança dentro do projeto
        local_dir = Path(__file__).resolve().parent.parent.parent / "meetings"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_file = local_dir / filename
        local_file.write_text(markdown_content, encoding="utf-8")
        logger.info("Backup local salvo em: %s", local_file)

        # 2. Sincronização com o Google Drive (Segundo Cérebro)
        gdrive_file: Optional[Path] = None
        try:
            if self.gdrive_vault.exists():
                gdrive_inbox = self.gdrive_vault / "00_Inbox"
                gdrive_inbox.mkdir(parents=True, exist_ok=True)
                gdrive_file = gdrive_inbox / filename
                gdrive_file.write_text(markdown_content, encoding="utf-8")
                logger.info("✓ Ata sincronizada no Google Drive (Segundo Cérebro): %s", gdrive_file)
        except Exception as e:
            logger.warning("Falha ao gravar no Google Drive: %s", e)

        # 3. Salva no cofre local do Obsidian
        if self.vault_path.exists():
            inbox_dir = self.vault_path / "00_Inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            obsidian_file = inbox_dir / filename
            obsidian_file.write_text(markdown_content, encoding="utf-8")
            logger.info("✓ Ata salva no Obsidian local: %s", obsidian_file)
            return obsidian_file

        return gdrive_file or local_file
