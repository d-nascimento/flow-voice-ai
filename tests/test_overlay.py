from PyQt6.QtWidgets import QApplication
from src.ui.overlay import VoiceOverlay, WaveformWidget

# Garante uma instância de QApplication para o teste
app = QApplication.instance() or QApplication([])


def test_waveform_widget_init():
    wave = WaveformWidget()
    assert not wave._is_active
    wave.set_active(True)
    assert wave._is_active


def test_voice_overlay_init_and_signals():
    overlay = VoiceOverlay()
    assert overlay.status_label.text() == "Ouvindo..."
    assert overlay.icon_label.text() == "●"

    # Testa métodos de mudança de estado
    overlay.show_listening()
    assert overlay.status_label.text() == "Ouvindo..."

    overlay.show_processing()
    assert overlay.status_label.text() == "Processando..."

    overlay.show_done("Injetado!")
    assert overlay.status_label.text() == "Injetado!"

    overlay.show_error("Erro de áudio")
    assert overlay.status_label.text() == "Erro de áudio"
