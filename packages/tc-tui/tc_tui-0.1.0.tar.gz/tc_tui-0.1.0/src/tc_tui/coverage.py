import glob
import os
import subprocess
import sys

from tc_tui.file_helper import FileHelper
from tc_tui.config import Config
from tc_tui.toml.toml_handler import TomlHandler


class Coverage:
    def __compile_files_with_coverage_args(self):
        try:
            print("\nCompiling the program with coverage flags...")
            self.output_executable = os.path.join(FileHelper.cwd(), Config().get_cov_executable_name())
            compile_command = (['gcc', '-O0', '-fprofile-arcs', '-ftest-coverage'] +
                               Config().get_source_files() + ['-o', self.output_executable])

            subprocess.run(compile_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"Compilation successful!")

        except subprocess.CalledProcessError:
            print("\nERROR: Compilation failed! Exiting...")
            sys.exit(1)

    def __run_single_testcase(self, input_path):
        with open(input_path, 'r') as f:
            inputs = f.readlines()

        process = subprocess.Popen(self.output_executable, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=''.join(inputs))

        if process.returncode != 0:
            print(f"Error running program with input {input_path}: {stderr}")

    def __run_all_testcases(self):
        print("\nRunning all testcases...")
        testcases = TomlHandler().get_all_testcases()
        for index, testcase in enumerate(testcases):
            self.__run_single_testcase(testcase.input_path)
            print(f"[{index + 1} / {len(testcases)}] completed")

    def __run_gcov(self):
        executable_name = os.path.basename(self.output_executable)

        for source_file in Config().get_source_files():
            source_name = os.path.basename(source_file)
            source_dir = os.path.dirname(source_file)

            cov_file = os.path.join(source_dir, f"{executable_name}-{source_name}")
            try:
                print(f"\nRunning gcov on {cov_file}...")
                subprocess.run(["gcov", cov_file], check=True)
            except subprocess.CalledProcessError:
                print(f"\nERROR: can't run gcov on {cov_file}! Exiting...")
                sys.exit(1)

    def __run_lcov(self):
        if not os.path.exists(Config().get_cov_output_dir()):
            os.makedirs(Config().get_cov_output_dir())

        try:
            print("\nGenerating coverage report...")
            subprocess.run(["lcov", "--capture", "--directory", FileHelper.cwd(),
                            "--output-file", os.path.join(Config().get_cov_output_dir(), "coverage.info"),
                            "--rc", "branch_coverage=1"], check=True)
        except subprocess.CalledProcessError:
            print("\nERROR: can't generate coverage report! Exiting...")
            sys.exit(1)

    def __generate_html_report(self):
        try:
            print("\nGenerating HTML report...")
            subprocess.run(["genhtml", os.path.join(Config().get_cov_output_dir(), "coverage.info"), "--output-directory",
                            Config().get_cov_output_dir()], check=True)
        except subprocess.CalledProcessError:
            print("\nERROR: can't generate HTML report! Exiting...")
            sys.exit(1)

    def __open_html_report(self):
        try:
            print("\nOpening HTML report...")
            subprocess.run(["xdg-open", os.path.join(Config().get_cov_output_dir(), "index.html")], check=True)
        except subprocess.CalledProcessError:
            print("\nERROR: can't open HTML report! Exiting...")
            sys.exit(1)

    def __remove_coverage_files(self):
        print("\nRemoving coverage files...")
        cov_files = glob.glob(os.path.join(FileHelper.cwd(), "*.gcda"))
        cov_files.extend(glob.glob(os.path.join(FileHelper.cwd(), "*.gcno")))
        cov_files.extend(glob.glob(os.path.join(FileHelper.cwd(), "*.gcov")))
        cov_files.append(self.output_executable)
        for cov_file in cov_files:
            os.remove(cov_file)

    def __parse_report(self):
        covered_lines = 0
        total_lines = 0

        try:
            # Parse the coverage.info file to extract statistics
            coverage_info_path = os.path.join(Config().get_cov_output_dir(), "coverage.info")
            if os.path.exists(coverage_info_path):
                with open(coverage_info_path, 'r') as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines):
                        if line.startswith("DA:"):
                            # DA:line_number,execution_count
                            parts = line.strip().split(':')[1].split(',')
                            total_lines += 1
                            if int(parts[1]) > 0:
                                covered_lines += 1

            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            return {
                "covered_lines": covered_lines,
                "total_lines": total_lines,
                "coverage_percentage": coverage_percentage
            }
        except Exception as e:
            print(f"Error parsing coverage report: {e}")
            return {
                "covered_lines": 0,
                "total_lines": 0,
                "coverage_percentage": 0
            }

    def generate_coverage_report(self):
        self.__compile_files_with_coverage_args()
        self.__run_all_testcases()
        self.__run_gcov()
        self.__run_lcov()
        self.__generate_html_report()
        self.__open_html_report()
        self.__remove_coverage_files()

        return self.__parse_report()
