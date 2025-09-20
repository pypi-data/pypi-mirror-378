import tempfile
import time
import os
import shutil

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window, FormattedTextControl
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog, message_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Label, TextArea, Button, Dialog

from tc_tui.coverage import Coverage
from tc_tui.io_capturer import IOCapturer
from tc_tui.toml.testcase import TestCase
from tc_tui.toml.toml_handler import TomlHandler


class MenuHandler:
    def main_menu(self):
        choices = [
            ("new", "Create a new testcase"),
            ("edit", "Edit an existing testcase"),
            ("regenerate", "Regenerate existing testcases"),
            ("public_private", "Reorder the testcases and set the public/private"),
            ("coverage", "Generate coverage report")
        ]
        while True:
            choice = radiolist_dialog(
                title="TC Gen",
                text="What do you want to do?",
                cancel_text="Exit",
                values=choices
            ).run()

            if choice == "new":
                self.new_submenu()
            elif choice == "edit":
                self.edit_submenu()
            elif choice == "regenerate":
                self.regenerate_submenu()
            elif choice == "public_private":
                self.public_private_submenu()
            elif choice == "coverage":
                self.coverage_submenu()
            elif choice is None:
                print("Exiting...")
                break
            else:
                print(f"ERROR: Main menu choice \"{choice}\" not implemented. Exiting...")

    def __testcase_properties_menu(self, name="", description="", argv=None, env_vars=None):
        if argv is None:
            argv = []
        if env_vars is None:
            env_vars = {}

        args_str = " ".join(argv)
        env_str = "\n".join(env_vars)

        prompts = [
            ("name", "Enter the name: ", name, False),
            ("description", "Enter the description: ", description, True),
            ("argv", "Enter command-line arguments (space-separated): ", args_str, False),
            ("env_vars", "Enter environment variables (one KEY=VALUE per line): ", env_str, True)
        ]

        text_areas = {}
        responses = {}

        widgets = []
        for key, prompt_msg, default_value, multiline in prompts:
            label = Label(prompt_msg)
            text_area = TextArea(multiline=multiline, text=default_value)
            text_areas[key] = text_area
            widgets.append(label)
            widgets.append(text_area)

        def ok_handler():
            for key, text_area in text_areas.items():
                responses[key] = text_area.text
            app.exit()

        def cancel_handler():
            app.exit()

        ok_button = Button("OK", handler=ok_handler)
        cancel_button = Button("Cancel", handler=cancel_handler)

        dialog = Dialog(
            title="Testcase Properties",
            body=HSplit(widgets),
            buttons=[ok_button, cancel_button],
            width=100,
            modal=True,
            with_background=True,
        )

        app = Application(
            layout=Layout(dialog),
            full_screen=True
        )

        app.run()

        return responses

    def __testcase_properties_edit_menu(self, testcase):
        return self.__testcase_properties_menu(testcase.name, testcase.description, testcase.argv, testcase.env_vars)

    def new_submenu(self):
        responses = self.__testcase_properties_menu()

        if len(responses) == 0:
            return

        if "argv" in responses and responses["argv"]:
            responses["argv"] = responses["argv"].split()
        else:
            responses["argv"] = []

        if "env_vars" in responses and responses["env_vars"]:
            env_list = []
            for line in responses["env_vars"].splitlines():
                if line and "=" in line:
                    env_list.append(line.strip())
                    responses["env_vars"] = env_list
        else:
            responses["env_vars"] = []

        responses["type"] = "OrdIO"
        responses["io_file"] = f"./tests/{TomlHandler().get_next_testcase_id():02d}/io.txt"

        testcase = TestCase(**responses)

        exit_code = IOCapturer().capture_new_testcase(testcase)
        testcase.exp_exit_code = exit_code
        TomlHandler().add_testcase(testcase)

    def edit_submenu(self):
        while True:
            index, testcase = self.single_testcase_selection()
            if index is None:
                return

            responses = self.__testcase_properties_edit_menu(testcase)

            if len(responses) == 0:
                return

            if "argv" in responses and responses["argv"]:
                responses["argv"] = responses["argv"].split()
            else:
                responses["argv"] = []

            if "env_vars" in responses and responses["env_vars"]:
                env_list = []
                for line in responses["env_vars"].splitlines():
                    if line and "=" in line:
                        env_list.append(line.strip())
                        responses["env_vars"] = env_list
            else:
                responses["env_vars"] = []

            TomlHandler().edit_testcase(index, responses)

    def regenerate_submenu(self):
        testcases = self.testcase_select_all_option()
        if testcases is None:
            return

        IOCapturer().capture_existing_testcases(testcases)
        message_dialog(title="Regenerate Testcases",
                       text=f"Successfully regenerated {len(testcases)} testcases!").run()

    def public_private_submenu(self):
        all_items = []
        testcases = TomlHandler().get_all_testcases()

        selected_index = -1
        cursor_index = 0
        public_count = 0

        for index, testcase in enumerate(testcases):
            all_items.append((index, f"{index + 1:02d} - {testcase.name}"))
            if not testcase.protected:
                public_count = index + 1

        def get_formatted_text():
            text = []
            for i, item in enumerate(all_items):
                if i == selected_index:
                    prefix = " > ["
                    suffix = "]\n"
                elif i == cursor_index:
                    prefix = " >  "
                    suffix = "\n"
                else:
                    prefix = "    "
                    suffix = "\n"

                status = "(Public)" if i < public_count else "(Private)"

                if i == selected_index:
                    text.append(('[underline]', f"{prefix}{item[1]} {status}{suffix}"))
                elif i == cursor_index:
                    text.append(('[reverse]', f"{prefix}{item[1]} {status}{suffix}"))
                else:
                    text.append(('', f"{prefix}{item[1]} {status}{suffix}"))
            return text

        kb = KeyBindings()

        @kb.add('up')
        def _(_):
            nonlocal selected_index
            nonlocal cursor_index
            if selected_index == -1:
                if cursor_index > 0:
                    cursor_index -= 1
            else:
                if selected_index > 0:
                    all_items[selected_index], all_items[selected_index - 1] = all_items[selected_index - 1], all_items[
                        selected_index]
                    selected_index -= 1
                    cursor_index = selected_index

        @kb.add('down')
        def _(_):
            nonlocal selected_index
            nonlocal cursor_index
            if selected_index == -1:
                if cursor_index < len(all_items) - 1:
                    cursor_index += 1
            else:
                if selected_index < len(all_items) - 1:
                    all_items[selected_index], all_items[selected_index + 1] = all_items[selected_index + 1], all_items[
                        selected_index]
                    selected_index += 1
                    cursor_index = selected_index

        @kb.add('s')
        def _(_):
            nonlocal selected_index
            if selected_index != -1:
                selected_index = -1
            else:
                selected_index = cursor_index

        @kb.add('p')
        def _(_):
            nonlocal public_count
            if cursor_index < public_count:
                public_count = cursor_index
            else:
                public_count = cursor_index + 1

        def ok_handler():
            nonlocal public_count
            reordered_testcases = []
            for item in all_items:
                original_index = item[0]
                reordered_testcases.append(testcases[original_index])

            toml_handler = TomlHandler()
            toml_handler._testcases = reordered_testcases

            toml_handler.set_public_testcases(public_count)

            tmp_test_dir = os.path.join(tempfile.gettempdir(), "tests")

            for i, testcase in enumerate(reordered_testcases):
                io_file = f"./tests/{i + 1:02d}/io.txt"
                if testcase.io_file == io_file:
                    continue

                old_io_path = testcase.io_path
                old_input_path = testcase.input_path

                new_dir = os.path.join(tmp_test_dir, f"{i+1:02d}")
                new_io_path = os.path.join(new_dir, "io.txt")
                new_input_path = os.path.join(new_dir, "input.txt")

                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

                if os.path.exists(old_io_path):
                    shutil.move(old_io_path, new_io_path)

                if os.path.exists(old_input_path):
                    shutil.move(old_input_path, new_input_path)

                testcase.io_file = f"./tests/{i+1:02d}/io.txt"
                testcase.io_path = new_io_path
                testcase.input_path = new_input_path

            if os.path.exists("./tests"):
                shutil.rmtree("./tests")
            shutil.move(tmp_test_dir, "./tests")

            toml_handler.save_toml()
            app.exit(f"Successfully reordered testcases and set {public_count} as public!")

        def cancel_handler():
            app.exit()

        ok_button = Button("OK", handler=ok_handler)
        cancel_button = Button("Cancel", handler=cancel_handler)

        help_text = Label("Use UP/DOWN to navigate, 'S' to select for reordering, 'P' to toggle public/private")

        dialog = Dialog(
            title="Reorder Testcases and Set Public/Private",
            body=HSplit([
                help_text,
                Window(FormattedTextControl(get_formatted_text), height=len(all_items))
            ]),
            with_background=True,
            buttons=[ok_button, cancel_button]
        )

        layout = Layout(dialog)

        style = Style.from_dict({
            "reverse": "bg:#61afef fg:#ffffff",
            "underline": "underline fg:#e06c75"
        })

        app = Application(
            layout=layout,
            style=style,
            key_bindings=kb,
            full_screen=True
        )

        result = app.run()

        # Display success message if one was returned
        if isinstance(result, str):
            message_dialog(
                title="Testcase Reordering",
                text=result
            ).run()

        return result

    def generate_coverage_report(self, coverage, progress_bar):
        try:
            for _ in range(5):
                time.sleep(1)
                progress_bar.increment()
            coverage.generate_coverage_report()
        finally:
            progress_bar.done = True

    def coverage_submenu(self):
        if not TomlHandler().get_all_testcases():
            message_dialog(title="Coverage Report",
                           text="Currently there doesn't exist a single testcase, so please create a new one.").run()
            return

        cov = Coverage()
        cov.generate_coverage_report()

        message_dialog(
            title="Coverage Report",
            text="The coverage report should now be open in your browser."
        ).run()

    def single_testcase_selection(self):
        all_items = []

        for index, testcase in enumerate(TomlHandler().get_all_testcases()):
            all_items.append((index, f"{(index + 1):02d} - {testcase.name}"))

        if len(all_items) == 0:
            message_dialog(title="Testcase Selection",
                           text="Currently there doesn't exist a single testcase, so please create a new one.").run()
            return None, None

        selected_index = radiolist_dialog(
            title="Testcase Selection",
            text="Select testcases:",
            values=all_items
        ).run()

        if selected_index is None:
            return None, None

        return selected_index, TomlHandler().get_testcase(selected_index)

    def testcase_selection(self):
        all_items = []
        testcases = TomlHandler().get_all_testcases()

        for index, testcase in enumerate(testcases):
            all_items.append((index, f"{index + 1} - {testcase.name}"))

        while True:
            selected = checkboxlist_dialog(
                title="Testcase Selection",
                text="Select testcases:",
                values=all_items
            ).run()

            if selected is None:
                return None

            if len(selected) > 0:
                break

            message_dialog(title="Testcase Selection", text="Please select at least one testcase").run()

        result = []
        for index in selected:
            result.append((index, testcases[index]))

        return result

    def testcase_select_all_option(self):
        if not TomlHandler().get_all_testcases():
            message_dialog(title="Testcase Selection",
                           text="Currently there doesn't exist a single testcase, so please create a new one.").run()
            return

        selected = radiolist_dialog(
            title="Testcase Selection",
            text="Select testcases:",
            values=[("select_all", "Select all"), ("select_one_or_more", "Select one or more")]
        ).run()

        if selected == "select_all":
            result = []
            testcases = TomlHandler().get_all_testcases()
            for index, testcase in enumerate(testcases):
                result.append((index, testcase))
            return result
        elif selected == "select_one_or_more":
            return self.testcase_selection()
        else:
            return None
