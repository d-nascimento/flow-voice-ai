import numpy as np
from src.audio.recorder import AudioRecorder


def test_audio_recorder_init():
    recorder = AudioRecorder(sample_rate=16000, channels=1)
    assert recorder.sample_rate == 16000
    assert recorder.channels == 1
    assert not recorder.is_recording


def test_audio_recorder_discard_short():
    recorder = AudioRecorder()
    recorder._is_recording = True
    # Frame com apenas 100 amostras (~0.006 segundos)
    recorder._frames = [np.zeros((100, 1), dtype=np.int16)]
    wav_bytes = recorder.stop_recording(min_duration_sec=0.3)
    assert wav_bytes == b""


def test_audio_recorder_discard_silent():
    recorder = AudioRecorder()
    recorder._is_recording = True
    # 1 segundo de silêncio absoluto (zeros)
    recorder._frames = [np.zeros((16000, 1), dtype=np.int16)]
    wav_bytes = recorder.stop_recording(min_duration_sec=0.3)
    assert wav_bytes == b""


def test_audio_recorder_valid_audio():
    recorder = AudioRecorder()
    recorder._is_recording = True
    # 0.5 segundo de sinal audível com energia suficiente
    t = np.linspace(0, 0.5, 8000, False)
    signal = (np.sin(2 * np.pi * 440 * t) * 5000).astype(np.int16).reshape(-1, 1)
    recorder._frames = [signal]
    wav_bytes = recorder.stop_recording(min_duration_sec=0.3)
    assert len(wav_bytes) > 44  # Cabeçalho WAV é 44 bytes
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"
