import time
import numpy as np
from src.meetings.recorder import MeetingRecorder


def test_meeting_recorder_init():
    rec = MeetingRecorder(sample_rate=16000)
    assert not rec.is_recording
    assert rec.get_duration_sec() == 0.0


def test_meeting_recorder_stop_empty():
    rec = MeetingRecorder()
    assert rec.stop_recording() == b""


def test_meeting_recorder_generate_wav():
    rec = MeetingRecorder(sample_rate=16000)
    rec._is_recording = True
    # 0.5 segundo de áudio simulado
    signal = np.sin(np.linspace(0, 100, 8000)).astype(np.float32)
    rec._audio_chunks = [signal]

    wav_bytes = rec.stop_recording()
    assert len(wav_bytes) > 44
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"
