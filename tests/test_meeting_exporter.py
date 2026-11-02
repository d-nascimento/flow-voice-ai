import tempfile
from pathlib import Path
from src.meetings.exporter import MeetingExporter


def test_meeting_exporter_local_and_vault():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "TestVault"
        inbox = vault_path / "00_Inbox"
        inbox.mkdir(parents=True, exist_ok=True)

        exporter = MeetingExporter(vault_path=vault_path)
        content = "---\ntipo: reuniao\n---\n# Ata Teste"
        saved_file = exporter.export(content, custom_filename="teste-reuniao.md")

        assert saved_file.exists()
        assert saved_file.name == "teste-reuniao.md"
        assert saved_file.read_text(encoding="utf-8") == content
