import errno
import os
import pty
import re
import select
import subprocess
import sys
import time
import tty

from prompt_toolkit.shortcuts import message_dialog

from tc_tui.file_helper import FileHelper
from tc_tui.toml.toml_handler import TomlHandler


class IOCapturer:
    _testcase = None
    _io_file = None
    _input_file = None
    _command = None

    def __cleaned_line(self, line):
        cleaned_line = bytearray()
        for char in line:
            if char == ord('\b'):
                if cleaned_line:
                    cleaned_line.pop()
            else:
                cleaned_line.append(char)
        return bytes(cleaned_line)

    def __input_prompt(self, line):
        pattern = self._testcase.io_prompt.replace("^", "").replace("$", "")
        regex = re.compile(pattern)

        match = regex.search(line)
        if match:
            return match.group(0)
        else:
            return None

    def __parse_output(self, output, input_list):
        captured_output_lines = output.splitlines()
        input_index = 0

        with open(self._io_file, 'w') as io_file:
            io_file.write('> \n')
            for line in captured_output_lines:
                prompt = self.__input_prompt(line)
                if prompt:
                    if input_index >= len(input_list):
                        formatted_line = f"? {prompt}\n< "
                    else:
                        input_list[input_index] = input_list[input_index].replace("\n", "").replace("\r", "")
                        formatted_line = f"? {prompt}\n< {input_list[input_index]}"
                        input_index += 1
                else:
                    formatted_line = '> ' + line

                formatted_line += '\n'
                io_file.write(formatted_line)

    def __start_capturing(self):
        input_log = open(self._input_file, "w")

        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

        stdin_fd = sys.stdin.fileno()
        old_settings = tty.tcgetattr(stdin_fd)

        output = ""
        input_list = []

        try:
            tty.setraw(stdin_fd)
            self._master_fd, self._slave_fd = pty.openpty()

            proc = subprocess.Popen(
                self._command,
                stdin=self._slave_fd,
                stdout=self._slave_fd,
                stderr=self._slave_fd,
                close_fds=True
            )

            line = bytearray()

            while True:
                rlist, _, _ = select.select([stdin_fd, self._master_fd], [], [], 0.1)

                if proc.poll() is not None:
                    break

                if stdin_fd in rlist:
                    user_data = os.read(stdin_fd, 1024)
                    if not user_data:
                        break

                    for char in user_data:
                        if char == ord('\b') or char == 127:
                            if line:
                                line.pop()
                                os.write(sys.stdout.fileno(), b'\b \b')
                        elif char == ord('\n') or char == ord('\r'):
                            os.write(self._master_fd, b'\n')
                            input_log.write(line.decode() + "\n")
                            input_list.append(line.decode())
                            line.clear()
                        else:
                            os.write(self._master_fd, bytes([char]))
                            line.append(char)

                if self._master_fd in rlist:
                    try:
                        proc_data = os.read(self._master_fd, 1024)
                    except OSError as e:
                        if e.errno == errno.EIO:
                            break
                        else:
                            raise

                    if not proc_data:
                        break

                    cleaned_line = self.__cleaned_line(proc_data)
                    os.write(sys.stdout.fileno(), cleaned_line)
                    output += cleaned_line.decode()

            exit_code = proc.wait()

        finally:
            os.close(self._slave_fd)
            tty.tcsetattr(stdin_fd, tty.TCSADRAIN, old_settings)
            input_log.close()

        self.__parse_output(output, input_list)
        return exit_code

    def __rerun_testcase(self):
        input_log = open(self._input_file, "r")

        output = ""
        input_list = input_log.readlines()
        input_index = 0

        try:
            self._master_fd, self._slave_fd = pty.openpty()

            proc = subprocess.Popen(
                self._command,
                stdin=self._slave_fd,
                stdout=self._slave_fd,
                stderr=self._slave_fd,
                close_fds=True
            )

            while True:
                rlist, _, _ = select.select([self._master_fd], [], [], 0.1)

                if proc.poll() is not None:
                    break

                if self._master_fd in rlist:
                    try:
                        proc_data = os.read(self._master_fd, 1024)
                    except OSError as e:
                        if e.errno == errno.EIO:
                            break
                        else:
                            raise

                    if not proc_data:
                        break

                    cleaned_line = self.__cleaned_line(proc_data)
                    output += cleaned_line.decode()

                    prompt = self.__input_prompt(output.splitlines()[-1])

                    if prompt and output[-len(prompt):] == prompt:
                        if input_index >= len(input_list):
                            proc.kill()
                            return None, -1

                        os.write(self._master_fd, input_list[input_index].encode())
                        input_index += 1

            exit_code = proc.wait()

            if input_index != len(input_list):
                return None, 1

        finally:
            os.close(self._slave_fd)
            input_log.close()

        self.__parse_output(output, input_list)
        return exit_code, 0

    def __get_updated_binary(self, timestamp):
        updated = []
        for entry in os.scandir(FileHelper.cwd()):
            if entry.is_file() and os.access(entry.path, os.X_OK) and os.path.getmtime(entry.path) > timestamp:
                updated.append(entry.path)

        if len(updated) == 1:
            return f"./{os.path.relpath(updated[0], FileHelper.cwd())}"

        return None

    def __make_binary(self):
        timestamp = time.time()
        make_targets = TomlHandler().get_make_targets()
        command = ["make"] + make_targets
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"\nERROR: Failed to execute \"{' '.join(command)}\"! Exiting...")
            sys.exit(1)

        path = self.__get_updated_binary(timestamp)
        if path is not None:
            TomlHandler().set_project_binary(path)

    def capture_new_testcase(self, testcase):
        self._testcase = testcase
        self.__make_binary()

        self._command = [TomlHandler().get_project_binary()] + testcase.argv

        directory = os.path.dirname(testcase.io_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        self._io_file = testcase.io_path
        self._input_file = testcase.input_path

        exit_code = self.__start_capturing()

        return exit_code


    def capture_existing_testcases(self, testcases):
        self.__make_binary()
        for index, testcase in testcases:
            self._command = [TomlHandler().get_project_binary()] + testcase.argv
            self._io_file = testcase.io_path
            self._input_file = testcase.input_path
            self._testcase = testcase
            exit_code, error = self.__rerun_testcase()

            if exit_code is None:
                if error == -1:
                    message_dialog(title="Regenerate Testcases", text=f"Failed: Testcase {index} expected more input lines then before...").run()
                elif error == 1:
                    message_dialog(title="Regenerate Testcases", text=f"Failed: Testcase {index} expected less input lines then before...").run()
                return

            TomlHandler().set_exit_code(index, exit_code)
