import shutil

from prompt_toolkit.shortcuts import message_dialog


class DependencyChecker:
    @staticmethod
    def check_dependencies():
        required_dependencies = {
            "gcc": "GCC compiler",
            "make": "Make build tool",
            "gcov": "GCOV coverage tool",
            "lcov": "LCOV coverage report generator",
            "genhtml": "HTML report generator (part of lcov package)",
        }
        
        missing_dependencies = []
        
        for cmd, description in required_dependencies.items():
            if not shutil.which(cmd):
                missing_dependencies.append((cmd, description))
        
        if missing_dependencies:
            DependencyChecker._show_missing_dependencies_dialog(missing_dependencies)
            return False
        
        return True
    
    @staticmethod
    def _show_missing_dependencies_dialog(missing_dependencies):
        message = "The following required dependencies are missing:\n\n"
        
        for cmd, description in missing_dependencies:
            message += f"- {cmd}: {description}\n"
        
        message += "\nPlease install these dependencies before using TestcaseHelper.\n\n"

        message += "Installation instructions:\n"
        message += "- Ubuntu/Debian: sudo apt-get install gcc make lcov\n"
        message += "- Fedora/RHEL: sudo dnf install gcc make lcov\n"
        message += "- macOS: brew install gcc make lcov\n"
        
        message_dialog(
            title="Missing Dependencies",
            text=message
        ).run()
