import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from src.meetings.synthesizer import MeetingSynthesizer


def test_meeting_synthesizer_empty_audio():
    synth = MeetingSynthesizer(api_key="fake_key")
    assert synth.synthesize(b"") == ""


def test_meeting_synthesizer_mock_call():
    synth = MeetingSynthesizer(api_key="fake_key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "# Ata Executiva Teste\n\n### Decisões Tomadas\n* Decisão 1"
    mock_client.models.generate_content.return_value = mock_response
    synth._client = mock_client

    result = synth.synthesize(b"RIFF_SAMPLE", duration_sec=120.0)
    assert "# Ata Executiva Teste" in result
    assert "Decisões Tomadas" in result
    mock_client.models.generate_content.assert_called_once()


def test_meeting_synthesizer_file_upload():
    synth = MeetingSynthesizer(api_key="fake_key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "# Ata Arquivo Teste\n\n### Resumo\nReunião sobre vendas."
    mock_client.models.generate_content.return_value = mock_response
    synth._client = mock_client

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"MOCK_MP3_DATA")
        tmp_path = Path(f.name)

    try:
        res = synth.synthesize_file(tmp_path)
        assert "# Ata Arquivo Teste" in res
        mock_client.models.generate_content.assert_called_once()
    finally:
        tmp_path.unlink(missing_ok=True)
