import configparser
import os

from tc_tui.file_helper import FileHelper


class Config:
    _instance = None

    def __new__(cls, file_path="config.ini"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file="config.ini"):
        self._file_path = config_file
        self._config = configparser.ConfigParser()
        self._config.read(config_file)

        if "files" in self._config:
            self._files = self._config["files"]
        else:
            self._config.add_section("files")
            self._files = self._config["files"]

        if "coverage" in self._config:
            self._coverage = self._config["coverage"]
        else:
            self._config.add_section("coverage")
            self._coverage = self._config["coverage"]

    def __set(self, section, key, value):
        section_name = next(sec_name for sec_name, sec_obj in self._config.items() if sec_obj is section)
        self._config[section_name][key] = value
        with open(self._file_path, 'w') as configfile:
            self._config.write(configfile)

    def get_source_files(self):
        patterns = self._files.get("source_files", "*.c").split(",")
        return FileHelper.find_files_by_pattern(patterns)

    def get_all_tests_toml_file(self):
        return self._files.get("all_tests_file", "test_all.toml")

    def get_public_tests_toml_file(self):
        return self._files.get("public_tests_file", "test.toml")

    def get_cov_executable_name(self):
        return os.path.join(FileHelper.cwd(), self._coverage.get("cov_executable", "a_cov.out"))

    def get_cov_output_dir(self):
        return str(os.path.join(FileHelper.cwd(), self._coverage.get("output_dir", "coverage_report/")))