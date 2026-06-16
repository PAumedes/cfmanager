import sys

if __name__ == "__main__":
    # No arguments → double-clicked or run bare → launch TUI
    # Any argument → delegate to CLI (e.g. cfm.exe zones list, cfm.exe --help)
    if len(sys.argv) == 1:
        from cfmanager.tui.app import run_tui_app
        run_tui_app()
    else:
        from cfmanager.cli.app import app
        app()
