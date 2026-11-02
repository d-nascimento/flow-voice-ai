from unittest.mock import MagicMock
from src.pipeline import VoicePipeline
from src.actions.intent_router import VoiceIntent


def test_pipeline_stop_with_no_audio():
    mock_recorder = MagicMock()
    mock_recorder.stop_recording.return_value = b""
    pipeline = VoicePipeline(recorder=mock_recorder)

    result = pipeline.stop_and_process()
    assert result is None


def test_pipeline_dictation_flow():
    mock_recorder = MagicMock()
    mock_recorder.stop_recording.return_value = b"RIFF_FAKE_WAV"

    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.return_value = "olá mundo"

    mock_router = MagicMock()
    mock_router.route_intent.return_value = VoiceIntent(
        type="dictation", text="Olá, mundo!"
    )

    mock_injector = MagicMock()
    mock_injector.inject.return_value = True

    pipeline = VoicePipeline(
        recorder=mock_recorder,
        transcriber=mock_transcriber,
        router=mock_router,
        injector=mock_injector,
    )

    result = pipeline.stop_and_process()
    assert result == "Olá, mundo!"
    mock_recorder.stop_recording.assert_called_once()
    mock_transcriber.transcribe.assert_called_once_with(b"RIFF_FAKE_WAV")
    mock_router.route_intent.assert_called_once()
    mock_injector.inject.assert_called_once_with("Olá, mundo!")


def test_pipeline_command_flow():
    mock_recorder = MagicMock()
    mock_recorder.stop_recording.return_value = b"RIFF_FAKE_WAV"

    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.return_value = "abra o chrome"

    mock_router = MagicMock()
    mock_router.route_intent.return_value = VoiceIntent(
        type="command", action="open_app", parameter="chrome", text="Abrindo o Chrome..."
    )

    mock_controller = MagicMock()
    mock_controller.open_app.return_value = True

    pipeline = VoicePipeline(
        recorder=mock_recorder,
        transcriber=mock_transcriber,
        router=mock_router,
        controller=mock_controller,
    )

    result = pipeline.stop_and_process()
    assert "[COMANDO EXECUTADO: OPEN_APP]" in result
    mock_controller.open_app.assert_called_once_with("chrome")
