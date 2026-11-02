from unittest.mock import patch
from src.ui.sound import SoundPlayer


@patch("winsound.PlaySound")
def test_sound_player_methods(mock_play):
    SoundPlayer.play_start()
    SoundPlayer.play_stop()
    SoundPlayer.play_paste()
    SoundPlayer.play_error()
    assert mock_play.call_count == 4
