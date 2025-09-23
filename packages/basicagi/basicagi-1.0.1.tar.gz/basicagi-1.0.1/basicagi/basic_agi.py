#!/usr/bin/env python3

import os
import sys


class BasicAGI:
    def __init__(self):
        """Initialize AGI interface by reading variables from stdin"""
        self.env = {}
        self.debug_enabled = os.environ.get("AGI_DEBUG", "").lower() == "true"

        # Configure buffering (only if not mocked for testing)
        try:
            sys.stdin.reconfigure(line_buffering=True)
            sys.stdout.reconfigure(line_buffering=True)
            sys.stderr.reconfigure(line_buffering=True)
        except AttributeError:
            # Handle testing environment where stdin/stdout might be StringIO
            pass

        # Read environment variables that Asterisk sends on startup
        self.read_channel()

    def _send_command(self, command, parse_mode=None):
        """
        Send command to Asterisk and get response
        parse_mode:
            None - just send command, no parsing
            1 - parse result and value
            2 - return full response
        """
        if self.debug_enabled:
            self.debug(f"AGI COMMAND: {command}")

        sys.stdout.write(f"{command}\n")
        sys.stdout.flush()

        response = sys.stdin.readline().strip()
        if self.debug_enabled:
            self.debug(f"AGI RESPONSE: {response}")

        if parse_mode is None:
            return None
        elif parse_mode == 1:
            # Parse response of format: 200 result=X (Y)
            try:
                parts = response.split("result=", 1)
                if len(parts) != 2:
                    return None, None

                result_part = parts[1]
                result = result_part.split(" ", 1)[0].strip()

                # Extract value in parentheses if present
                value = None
                if "(" in result_part and ")" in result_part:
                    value = result_part.split("(", 1)[1].rsplit(")", 1)[0]

                return result, value
            except (IndexError, ValueError, AttributeError):
                return None, None
        elif parse_mode == 2:
            return response

    def debug(self, message):
        """Print debug message to Asterisk console"""
        sys.stderr.write(f"{message}\n")
        sys.stderr.flush()

    def read_channel(self):
        """Read and populate AGI channel variables"""
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
            if ":" in line:
                key, value = line.split(":", 1)
                if key.startswith("agi_"):
                    key = key[4:]  # Remove 'agi_' prefix
                self.env[key] = value.strip()
                if self.debug_enabled:
                    self.debug(f"AGI ENV: {key} = {value.strip()}")

    def exec(self, application, *args):
        """Execute an Asterisk application"""
        if not application:
            return
        command = f"EXEC {application}"
        if args:
            command += f' "{",".join(str(arg) for arg in args)}"'
        return self._send_command(command, 2)

    def stream_file(self, audio_file, escape_digits="", offset=None):
        """Stream an audio file"""
        if not audio_file:
            return
        command = f'STREAM FILE {audio_file} "{escape_digits}"'
        if offset is not None:
            command += f" {offset}"
        return self._send_command(command, 1)[0]

    def get_option(self, audio_file, escape_digits="", timeout=0):
        """Stream file and wait for digit"""
        if not audio_file:
            return
        command = f'GET OPTION {audio_file} "{escape_digits}" {timeout}'
        return self._send_command(command, 1)[0]

    def set_callerid(self, number, name=None):
        """Set both caller ID number and name"""
        if not number:
            return

        if name:
            # Set both name and number: "Name" <number>
            self._send_command(f'SET CALLERID ""{name}" <{number}>"')
        else:
            # Set only number
            self._send_command(f"SET CALLERID {number}")

    def set_context(self, context):
        """Set context for continuation upon exit"""
        if not context:
            return
        self._send_command(f"SET CONTEXT {context}")

    def set_extension(self, extension):
        """Set extension for continuation upon exit"""
        if not extension:
            return
        self._send_command(f"SET EXTENSION {extension}")

    def set_priority(self, priority):
        """Set priority for continuation upon exit"""
        if not priority:
            return
        self._send_command(f"SET PRIORITY {priority}")

    def answer(self):
        """Answer channel"""
        self._send_command("ANSWER")

    def hangup(self, channel=None):
        """Hangup channel"""
        command = "HANGUP"
        if channel:
            command += f" {channel}"
        self._send_command(command)

    def noop(self, message=""):
        """Execute NOOP application"""
        self._send_command(f'NOOP "{message}"')

    def channel_status(self, channel=None):
        """Get channel status"""
        command = "CHANNEL STATUS"
        if channel:
            command += f" {channel}"
        return self._send_command(command, 1)[0]

    def verbose(self, message, level=0):
        """Send verbose message"""
        if not message:
            return
        self._send_command(f'VERBOSE "{message}" {level}')

    def send_text(self, text):
        """Send text to channel"""
        if not text:
            return
        return self._send_command(f'SEND TEXT "{text}"', 1)[0]

    def receive_text(self, timeout=0):
        """Receive text from channel"""
        result, text = self._send_command(f"RECEIVE TEXT {timeout}", 1)
        if result == "1":
            return text
        return None

    def get_variable(self, name):
        """Get channel variable"""
        if not name:
            return
        result, value = self._send_command(f"GET VARIABLE {name}", 1)
        if result == "1":
            return value
        return None

    def get_full_variable(self, expr, channel=None):
        """Get channel variable with full evaluation"""
        if not expr:
            return
        command = f"GET FULL VARIABLE {expr}"
        if channel:
            command += f" {channel}"
        result, value = self._send_command(command, 1)
        if result == "1":
            return value
        return None

    def set_variable(self, name, value=""):
        """Set channel variable"""
        if not name:
            return
        self._send_command(f'SET VARIABLE {name} "{value}"')

    def set(self, name, value=""):
        """Generic set method that handles both variables and functions"""
        if not name:
            return

        # Check if it's a function call (contains parentheses)
        if "(" in name and ")" in name:
            # It's a function like CDR(field) or CALLERID(name)
            # Use EXEC SET for functions
            self.exec("SET", f"{name}={value}")
        else:
            # It's a regular variable
            # Use AGI SET VARIABLE command
            self._send_command(f'SET VARIABLE {name} "{value}"')

    def set_cdr_variable(self, name, value=""):
        """Set CDR variable using generic set method"""
        if not name:
            return
        self.set(f"CDR({name})", value)

    def get_data(self, audio_file, timeout=None, max_digits=None):
        """Get data from user"""
        if not audio_file:
            return
        command = f"GET DATA {audio_file}"
        if timeout is not None:
            command += f" {timeout}"
            if max_digits is not None:
                command += f" {max_digits}"
        return self._send_command(command, 2)

    def wait_for_digit(self, timeout=-1):
        """Wait for digit press"""
        return self._send_command(f"WAIT FOR DIGIT {timeout}", 1)[0]

    def gosub(self, context, extension, priority, arg=None):
        """Go to subroutine"""
        if not all([context, extension, priority]):
            return
        command = f"GOSUB {context} {extension} {priority}"
        if arg is not None:
            command += f" {arg}"
        self._send_command(command)

    def database_get(self, family, key):
        """Get value from Asterisk database"""
        if not all([family, key]):
            return
        result, value = self._send_command(f"DATABASE GET {family} {key}", 1)
        if result == "1":
            return value
        return None

    def database_put(self, family, key, value):
        """Put value into Asterisk database"""
        if not all([family, key, value]):
            return
        return self._send_command(f"DATABASE PUT {family} {key} {value}", 2)

    def database_del(self, family, key):
        """Delete key from Asterisk database"""
        if not all([family, key]):
            return
        return self._send_command(f"DATABASE DEL {family} {key}", 2)

    def database_deltree(self, family, key=None):
        """Delete database tree"""
        if not family:
            return
        command = f"DATABASE DELTREE {family}"
        if key:
            command += f" {key}"
        return self._send_command(command, 2)

    # AGI Variable Getter Methods
    def get_agi_var_keys(self):
        """
        Get all available AGI variable keys.

        Returns:
            list: List of AGI variable keys (without 'agi_' prefix)
        """
        return list(self.env.keys())

    def get_agi_var(self, keyname):
        """
        Get the value of a specific AGI variable.

        Args:
            keyname (str): The AGI variable key (with or without 'agi_' prefix)

        Returns:
            str | None: The variable value, or None if not found
        """
        if not keyname:
            return None

        # Try the key as-is first
        if keyname in self.env:
            return self.env[keyname]

        # If key starts with 'agi_', try without the prefix
        if keyname.startswith("agi_"):
            key_without_prefix = keyname[4:]  # Remove 'agi_' prefix
            if key_without_prefix in self.env:
                return self.env[key_without_prefix]

        # If key doesn't start with 'agi_', try with the prefix
        else:
            key_with_prefix = f"agi_{keyname}"
            if key_with_prefix in self.env:
                return self.env[key_with_prefix]

        return None

    def get_all_agi_vars(self):
        """
        Get all AGI variables as key-value pairs.

        Returns:
            dict: Dictionary containing all AGI variable key-value pairs
        """
        return self.env.copy()

    # Audio & Media Commands
    def control_stream_file(
        self,
        audio_file,
        escape_digits="",
        offset=0,
        forward_digits="",
        rewind_digits="",
        pause_digits="",
    ):
        """Stream file with control (fast forward, rewind, pause)"""
        if not audio_file:
            return
        command = f'CONTROL STREAM FILE {audio_file} "{escape_digits}" {offset}'
        if forward_digits:
            command += f' "{forward_digits}"'
        if rewind_digits:
            command += f' "{rewind_digits}"'
        if pause_digits:
            command += f' "{pause_digits}"'
        return self._send_command(command, 1)[0]

    def set_music(self, on_off, music_class=""):
        """Enable/disable music on hold"""
        if on_off.lower() not in ["on", "off"]:
            return
        command = f"SET MUSIC {on_off}"
        if music_class:
            command += f" {music_class}"
        self._send_command(command)

    # Speech & TTS Commands
    def say_alpha(self, string, escape_digits=""):
        """Say character string"""
        if not string:
            return
        return self._send_command(f'SAY ALPHA "{string}" "{escape_digits}"', 1)[0]

    def say_digits(self, number, escape_digits=""):
        """Say digits one by one"""
        if not str(number):
            return
        return self._send_command(f'SAY DIGITS {number} "{escape_digits}"', 1)[0]

    def say_number(self, number, escape_digits="", gender=""):
        """Say number"""
        if number is None:
            return
        command = f'SAY NUMBER {number} "{escape_digits}"'
        if gender:
            command += f" {gender}"
        return self._send_command(command, 1)[0]

    def say_phonetic(self, string, escape_digits=""):
        """Say with phonetic spelling"""
        if not string:
            return
        return self._send_command(f'SAY PHONETIC "{string}" "{escape_digits}"', 1)[0]

    def say_date(self, date, escape_digits=""):
        """Say date (seconds since epoch)"""
        if date is None:
            return
        return self._send_command(f'SAY DATE {date} "{escape_digits}"', 1)[0]

    def say_time(self, time, escape_digits=""):
        """Say time (seconds since epoch)"""
        if time is None:
            return
        return self._send_command(f'SAY TIME {time} "{escape_digits}"', 1)[0]

    def say_datetime(self, time, escape_digits="", format="", timezone=""):
        """Say date and time"""
        if time is None:
            return
        command = f'SAY DATETIME {time} "{escape_digits}"'
        if format:
            command += f' "{format}"'
        if timezone:
            command += f" {timezone}"
        return self._send_command(command, 1)[0]

    # User Input Commands
    def receive_char(self, timeout=0):
        """Receive one character from channels supporting it"""
        return self._send_command(f"RECEIVE CHAR {timeout}", 1)[0]

    # Variables & Data Commands
    def set_autohangup(self, time):
        """Set autohangup time in seconds (0 to disable)"""
        if time is None:
            return
        self._send_command(f"SET AUTOHANGUP {time}")
