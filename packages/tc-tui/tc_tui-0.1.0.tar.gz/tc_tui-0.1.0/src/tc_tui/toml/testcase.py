import os

from tc_tui.file_helper import FileHelper


class TestCase:
    def __init__(self, name, description, type, io_file, exp_exit_code=0, protected=False, io_prompt="^\\s*>\\s*$", argv=None, env_vars=None):
        self.name = name
        self.description = description
        self.type = type
        self.io_file = io_file
        self.io_path = os.path.join(FileHelper.cwd(), io_file)
        self.input_path = os.path.join(os.path.dirname(self.io_path), "input.txt")
        self.exp_exit_code = exp_exit_code
        self.protected = protected
        self.io_prompt = io_prompt
        self.argv = argv if argv is not None else []
        self.env_vars = env_vars if env_vars is not None else []
        # TODO: subclasses for different types of testcases

    def to_dict(self):
        result = {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "io_file": self.io_file,
            "io_prompt": self.io_prompt,
            "exp_exit_code": self.exp_exit_code,
            "protected": self.protected,
            "argv": self.argv,
            "env_vars": self.env_vars,
        }

        return result
