from src.context.window import WindowTracker, WindowContext


def test_categorize_processes():
    assert WindowTracker._categorize_process("Code.exe") == "code_editor"
    assert WindowTracker._categorize_process("cursor.exe") == "code_editor"
    assert WindowTracker._categorize_process("WindowsTerminal.exe") == "terminal"
    assert WindowTracker._categorize_process("cmd.exe") == "terminal"
    assert WindowTracker._categorize_process("WhatsApp.exe") == "messaging"
    assert WindowTracker._categorize_process("slack.exe") == "messaging"
    assert WindowTracker._categorize_process("chrome.exe") == "browser"
    assert WindowTracker._categorize_process("obsidian.exe") == "notes_and_docs"
    assert WindowTracker._categorize_process("unknown_app.exe") == "general"


def test_get_active_window_fallback():
    ctx = WindowTracker.get_active_window()
    assert isinstance(ctx, WindowContext)
    assert hasattr(ctx, "title")
    assert hasattr(ctx, "process_name")
    assert hasattr(ctx, "app_category")
    assert hasattr(ctx, "hwnd")
