# tc-tui

A TUI (Text-based User Interface) for creating testcases for C programs.
The testcases are in the format used with this testrunner https://gitlab.tugraz.at/testrunner/testrunner

## Features

- Create testcases for C programs by interactively running the program and capturing input/output
- Edit testcases for C programs
- Regenerate testcases with the previous inputs
- Reorder testcases and set public/private status
- Generate coverage reports

## Installation

### Option 1: Install from PyPI

```bash
pip install tc-tui
```

### Option 2: Install from source

```bash
git clone https://gitlab.tugraz.at/B3D2209CD12BEAA2/tc-tui.git
cd tc-tui
pip install -e .
```

## Dependencies

TestcaseHelper requires the following external dependencies:

- **gcc**: C compiler
- **make**: Build tool
- **gcov**: Coverage analysis tool (usually comes with gcc)
- **lcov**: Coverage report generator
- **genhtml**: HTML report generator (part of lcov package)

### Installing dependencies

#### Ubuntu/Debian

```bash
sudo apt-get install gcc make lcov
```

#### Fedora/RHEL

```bash
sudo dnf install gcc make lcov
```

#### macOS

```bash
brew install gcc make lcov
```

## Usage

Open a terminal in the assigment directory (which contains the source files, the `Makefile` and the testrunner binary) and run:

```bash
tc-tui
```

This will open the TUI in your terminal.

## Configuration

tc-tui uses an optional`config.ini` file for configuration. The default configuration is:

```ini
[files]
source_files = *.c
all_tests_file = test_all.toml
public_tests_file = test.toml

[coverage]
cov_executable = a_cov.out
output_dir = coverage_report/
```

You can create/modify this file to change the default settings.

## License

This project is licensed under the MIT License - see the LICENSE file for details.