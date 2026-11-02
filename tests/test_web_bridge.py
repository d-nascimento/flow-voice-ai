from src.web.bridge import WebBridge


def test_web_bridge_init():
    bridge = WebBridge()
    assert len(bridge.get_history()) == 0
    mics = bridge.get_microphones()
    assert len(mics) > 0


def test_web_bridge_history_lifecycle():
    bridge = WebBridge()
    bridge.add_history_entry("Transcrição de teste", is_command=False)
    bridge.add_history_entry("Abrir Chrome", is_command=True)

    history = bridge.get_history()
    assert len(history) == 2
    assert history[0]["type"] == "command"
    assert history[1]["type"] == "dictation"

    bridge.clear_history()
    assert len(bridge.get_history()) == 0


def test_web_bridge_meeting_status():
    bridge = WebBridge()
    status = bridge.get_meeting_status()
    assert "is_recording" in status
    assert status["is_recording"] is False
    assert status["duration_sec"] == 0.0
