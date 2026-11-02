from src.dictation.modes import (
    DictationModesManager,
    MODE_EXACT,
    MODE_POLISH,
    MODE_PROMPT,
)


def test_dictation_modes_defaults(tmp_path):
    cfg = tmp_path / "test_modes.json"
    mgr = DictationModesManager(config_path=cfg)
    assert mgr.active_mode == MODE_EXACT
    instr = mgr.get_system_instruction()
    assert "FIDELIDADE ABSOLUTA" in instr
    assert "PROIBIDO trocar palavras" in instr


def test_dictation_modes_switch_polish(tmp_path):
    cfg = tmp_path / "test_modes.json"
    mgr = DictationModesManager(config_path=cfg)
    assert mgr.set_active_mode(MODE_POLISH) is True
    assert mgr.active_mode == MODE_POLISH
    instr = mgr.get_system_instruction()
    assert "TEM LIBERDADE para trocar palavras" in instr

    # Persistência
    mgr2 = DictationModesManager(config_path=cfg)
    assert mgr2.active_mode == MODE_POLISH


def test_dictation_modes_switch_prompt(tmp_path):
    cfg = tmp_path / "test_modes.json"
    mgr = DictationModesManager(config_path=cfg)
    assert mgr.set_active_mode(MODE_PROMPT) is True
    assert mgr.active_mode == MODE_PROMPT
    instr = mgr.get_system_instruction()
    assert "PROMPT PERFEITO" in instr
    assert "**Role**" in instr
