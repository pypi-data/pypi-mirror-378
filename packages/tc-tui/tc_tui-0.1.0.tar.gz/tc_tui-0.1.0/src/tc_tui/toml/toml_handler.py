import os
import toml

from tc_tui.config import Config
from tc_tui.toml.project_definition import ProjectDefinition
from tc_tui.toml.testcase import TestCase


class TomlHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TomlHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        self.all_testcases_file = Config().get_all_tests_toml_file()
        self.public_testcases_file = Config().get_public_tests_toml_file()
        self._project_definition = ProjectDefinition()
        self._testcases = []
        self._last_modified = 0
        self.load_toml()

    def set_project_binary(self, path):
        if len(self._project_definition.binary_path) == 0:
            self._project_definition.binary_path = path
        if len(self._project_definition.project_name) == 0:
            name = os.path.basename(path)
            self._project_definition.project_name = name.upper()
        self.save_toml()

    def get_project_binary(self):
        return self._project_definition.binary_path

    def get_make_targets(self):
        return self._project_definition.make_targets

    def load_toml(self):
        try:
            with open(self.all_testcases_file, 'r') as f:
                toml_config = toml.load(f)
            self._project_definition = ProjectDefinition(**toml_config.get("project_definition", {}))

            testcases_data = toml_config.get("testcases", [])
            self._testcases = []

            for i, tc_data in enumerate(testcases_data):
                env_list = []
                if "env_vars" in tc_data:
                    existing = tc_data.pop("env_vars")
                    if isinstance(existing, list):
                        env_list = [str(x) for x in existing]
                    else:
                        # Non-list values are ignored (no legacy support).
                        env_list = []

                tc_data["env_vars"] = env_list
                self._testcases.append(TestCase(**tc_data))

            self._last_modified = os.path.getmtime(self.all_testcases_file)
        except FileNotFoundError:
            self._project_definition = ProjectDefinition()
            self._testcases = []
        except toml.TomlDecodeError:
            raise ValueError(f"The file {self.all_testcases_file} is not a valid TOML file.")

    def save_toml(self):
        toml_config = {
            "project_definition": self._project_definition.to_dict(),
            "testcases": [tc.to_dict() for tc in self._testcases]
        }
        with open(self.all_testcases_file, 'w') as f:
            toml.dump(toml_config, f)
        public_testcases = [tc for tc in self._testcases if not tc.protected]
        public_toml_config = {
            "project_definition": self._project_definition.to_dict(),
            "testcases": [tc.to_dict() for tc in public_testcases]
        }
        with open(self.public_testcases_file, 'w') as f:
            toml.dump(public_toml_config, f)
        self._last_modified = os.path.getmtime(self.all_testcases_file)

    def edit_testcase(self, index, changes):
        for key, value in changes.items():
            self._testcases[index].__setattr__(key, value)
        self.save_toml()

    def reload_if_changed(self):
        # Feel free to add a file observer xD
        current_modified = os.path.getmtime(self.all_testcases_file)
        if current_modified > self._last_modified:
            self.load_toml()

    def add_testcase(self, testcase):
        self._testcases.append(testcase)
        self.save_toml()

    def remove_testcase(self, name):
        self._testcases = [tc for tc in self._testcases if tc.name != name]
        self.save_toml()

    def get_all_testcases(self):
        return self._testcases

    def get_next_testcase_id(self):
        return len(self._testcases) + 1

    def get_testcase(self, index):
        if index >= len(self._testcases):
            return None

        return self._testcases[index]

    def set_public_testcases(self, num_testcases):
        public_testcases = self._testcases[:num_testcases]
        private_testcases = self._testcases[num_testcases:]

        for tc in public_testcases:
            tc.protected = False

        for tc in private_testcases:
            tc.protected = True

        self.save_toml()

    def set_exit_code(self, index, exit_code):
        self._testcases[index].exp_exit_code = exit_code
        self.save_toml()
