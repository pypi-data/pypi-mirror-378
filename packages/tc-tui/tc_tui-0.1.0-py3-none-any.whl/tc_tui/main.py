import os
import subprocess
import sys
from shutil import which

from tc_tui.dependency_checker import DependencyChecker
from tc_tui.ui.menu_handler import MenuHandler


def is_interactive():
    return os.isatty(sys.stdin.fileno())


def run_in_terminal():
    script_name = sys.argv[0]

    # common terminal emulators. Feel free to add more
    terminal_emulators = [
        "xterm",
        "gnome-terminal",
        "konsole",
        "xfce4-terminal",
        "mate-terminal",
        "tilix",
        "alacritty",
        "terminator",
    ]
    for terminal in terminal_emulators:
        if which(terminal):
            try:
                command = [terminal, "--", "python3", script_name]
                subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print("\nERROR: Failed to open new terminal! Exiting...")
                sys.exit(1)
            finally:
                return

    print("ERROR: No terminal emulator found. Exiting...")


def main():
    if not is_interactive():
        print("Not running in a real terminal. Opening a new terminal")
        run_in_terminal()
        return

    if not DependencyChecker.check_dependencies():
        print("Missing required dependencies. Please install them and try again.")
        return

    MenuHandler().main_menu()


if __name__ == "__main__":
    main()
