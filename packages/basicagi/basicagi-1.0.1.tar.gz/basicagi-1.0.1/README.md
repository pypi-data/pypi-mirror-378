# BasicAGI

A Python library for creating Asterisk Gateway Interface (AGI) applications.

[![PyPI version](https://badge.fury.io/py/basicagi.svg)](https://badge.fury.io/py/basicagi)
[![Python versions](https://img.shields.io/pypi/pyversions/basicagi.svg)](https://pypi.org/project/basicagi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is AGI?

The Asterisk Gateway Interface (AGI) is a powerful interface that allows external programs to control call flow in Asterisk PBX. AGI scripts can be written in any language and provide a way to add custom logic to your dialplan.

## Features

- **Simple and intuitive API** - Easy-to-use Python interface for AGI commands
- **Comprehensive command support** - Covers all major AGI commands and functions
- **Robust variable handling** - Access to all AGI environment variables
- **Audio and media control** - Stream files, play prompts, and control media
- **Database operations** - Read/write to Asterisk database
- **Call control** - Answer, hangup, transfer, and redirect calls
- **TTS and speech** - Text-to-speech and digit/number speaking functions
- **Debug support** - Built-in debugging capabilities
- **Production ready** - Used in real-world VoIP applications

## Installation

Install BasicAGI using pip:

```bash
pip install basicagi
```

## Quick Start

Here's a simple AGI script that answers a call, plays a welcome message, and hangs up:

```python
#!/usr/bin/env python3

from basicagi import BasicAGI

def main():
    # Create AGI instance
    agi = BasicAGI()

    # Answer the call
    agi.answer()

    # Play welcome message
    agi.stream_file("welcome")

    # Say the caller ID
    caller_id = agi.get_agi_var("callerid")
    if caller_id:
        agi.say_digits(caller_id)

    # Hang up
    agi.hangup()

if __name__ == "__main__":
    main()
```

## Usage Examples

### Basic Call Handling

```python
from basicagi import BasicAGI

agi = BasicAGI()

# Answer the call
agi.answer()

# Get caller information
caller_id = agi.get_agi_var("callerid")
channel = agi.get_agi_var("channel")

# Set caller ID
agi.set_callerid("1234567890", "My Company")

# Play audio file with digit interruption
digit = agi.stream_file("menu", "123456789*0#")

# Process user input
if digit == "1":
    agi.stream_file("option1")
elif digit == "2":
    agi.stream_file("option2")
else:
    agi.stream_file("invalid")

agi.hangup()
```

### Interactive Voice Response (IVR)

```python
from basicagi import BasicAGI

def handle_ivr():
    agi = BasicAGI()
    agi.answer()

    while True:
        # Play main menu
        digit = agi.get_option("main-menu", "123456789*0#", 5000)

        if digit == "1":
            # Sales department
            agi.stream_file("connecting-sales")
            agi.exec("Dial", "PJSIP/sales@internal")
            break
        elif digit == "2":
            # Support department
            agi.stream_file("connecting-support")
            agi.exec("Dial", "PJSIP/support@internal")
            break
        elif digit == "0":
            # Operator
            agi.stream_file("connecting-operator")
            agi.exec("Dial", "PJSIP/operator@internal")
            break
        else:
            # Invalid option
            agi.stream_file("invalid-option")
            continue

    agi.hangup()

if __name__ == "__main__":
    handle_ivr()
```

### Database Operations

```python
from basicagi import BasicAGI

agi = BasicAGI()
agi.answer()

# Store caller information
caller_id = agi.get_agi_var("callerid")
agi.database_put("callers", caller_id, "last_call_time", str(time.time()))

# Retrieve stored data
last_call = agi.database_get("callers", f"{caller_id}/last_call_time")
if last_call:
    agi.verbose(f"Caller {caller_id} last called at {last_call}")

# Set CDR variables
agi.set_cdr_variable("custom_field", "important_call")

agi.hangup()
```

### Text-to-Speech and Number Handling

```python
from basicagi import BasicAGI
import time

agi = BasicAGI()
agi.answer()

# Say current time
current_time = int(time.time())
agi.say_datetime(current_time, "", "ABdY 'digits/at' IMp")

# Say a number
agi.say_number(12345)

# Spell out text
agi.say_alpha("HELLO")

# Say individual digits
agi.say_digits("567890")

agi.hangup()
```

## AGI Environment Variables

Access Asterisk environment variables easily:

```python
from basicagi import BasicAGI

agi = BasicAGI()

# Get specific variable
caller_id = agi.get_agi_var("callerid")
channel = agi.get_agi_var("channel")
extension = agi.get_agi_var("extension")

# Get all available variables
all_vars = agi.get_all_agi_vars()
for key, value in all_vars.items():
    agi.verbose(f"{key}: {value}")

# Get list of all variable keys
var_keys = agi.get_agi_var_keys()
```

## Debugging

Enable debugging by setting the `AGI_DEBUG` environment variable:

```bash
export AGI_DEBUG=true
python your_agi_script.py
```

Or in your Asterisk dialplan:

```
exten => 123,1,Set(AGI_DEBUG=true)
same => n,AGI(your_script.py)
```

## Asterisk Integration

### Using in Dialplan

Add your AGI script to your Asterisk dialplan:

```
[incoming]
exten => _X.,1,AGI(your_script.py)
same => n,Hangup()
```

### File Permissions

Make sure your AGI script is executable:

```bash
chmod +x /var/lib/asterisk/agi-bin/your_script.py
```

### AGI Directory

Place your scripts in the Asterisk AGI directory (typically `/var/lib/asterisk/agi-bin/`)

## API Reference

### Core Methods

- `answer()` - Answer the channel
- `hangup(channel=None)` - Hang up the channel
- `exec(application, *args)` - Execute an Asterisk application

### Audio & Media

- `stream_file(audio_file, escape_digits="", offset=None)` - Stream an audio file
- `get_option(audio_file, escape_digits="", timeout=0)` - Stream file and wait for digit
- `control_stream_file(...)` - Stream file with control (FF/RW/pause)
- `set_music(on_off, music_class="")` - Enable/disable music on hold

### Speech & TTS

- `say_alpha(string, escape_digits="")` - Say character string
- `say_digits(number, escape_digits="")` - Say digits one by one
- `say_number(number, escape_digits="", gender="")` - Say number
- `say_date(date, escape_digits="")` - Say date
- `say_time(time, escape_digits="")` - Say time
- `say_datetime(time, escape_digits="", format="", timezone="")` - Say date and time

### Variables & Data

- `get_variable(name)` - Get channel variable
- `set_variable(name, value="")` - Set channel variable
- `get_agi_var(keyname)` - Get AGI environment variable
- `get_all_agi_vars()` - Get all AGI variables
- `set_cdr_variable(name, value="")` - Set CDR variable

### Database Operations

- `database_get(family, key)` - Get value from Asterisk database
- `database_put(family, key, value)` - Put value into Asterisk database
- `database_del(family, key)` - Delete key from database
- `database_deltree(family, key=None)` - Delete database tree

### Call Control

- `set_callerid(number, name=None)` - Set caller ID
- `set_context(context)` - Set context for continuation
- `set_extension(extension)` - Set extension for continuation
- `set_priority(priority)` - Set priority for continuation
- `channel_status(channel=None)` - Get channel status

### User Input

- `get_data(audio_file, timeout=None, max_digits=None)` - Get data from user
- `wait_for_digit(timeout=-1)` - Wait for digit press
- `receive_char(timeout=0)` - Receive character from channel
- `receive_text(timeout=0)` - Receive text from channel

## Development

### Setup Development Environment

```bash
# Create virtual environment
uv venv .venv

# Install package in development mode with dependencies
source .venv/bin/activate && uv pip install -e .

# Install test and development dependencies
source .venv/bin/activate && uv pip install pytest pytest-cov ruff
```

### Code Quality and Pre-commit Checks

Before submitting any changes, ensure your code passes all quality checks:

```bash
# Sort imports with ruff
source .venv/bin/activate && ruff check --select I --fix basicagi tests examples

# Format code with ruff
source .venv/bin/activate && ruff format basicagi tests examples

# Run linter with ruff
source .venv/bin/activate && ruff check basicagi tests examples

# Fix linting issues automatically
source .venv/bin/activate && ruff check --fix basicagi tests examples

# Run tests
source .venv/bin/activate && python -m pytest tests/

# Run tests with coverage
source .venv/bin/activate && python -m pytest tests/ --cov=basicagi --cov-report=html
```

### Git Pre-commit Hook (Recommended)

Automate code quality checks with a Git pre-commit hook:

```bash
# Install the Git pre-commit hook
./git-hooks-setup.sh
```

The Git pre-commit hook will automatically run before each commit and will:
- Sort imports with ruff
- Format code with ruff
- Run linting with ruff
- Run tests if test files are modified

To bypass the hook for a specific commit: `git commit --no-verify`

### Manual Pre-commit Workflow

If not using pre-commit hooks, run these commands before committing:

1. **Sort imports**: `ruff check --select I --fix basicagi tests examples`
2. **Format code**: `ruff format basicagi tests examples`
3. **Check linting**: `ruff check basicagi tests examples`
4. **Run tests**: `python -m pytest tests/`

This ensures consistent code style and catches issues early.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Asterisk](https://www.asterisk.org/) - The open source PBX
- [pyst2](https://github.com/rdegges/pyst2) - Python library for Asterisk

## Support

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/andrius/asterisk-basicagi/issues) page.

