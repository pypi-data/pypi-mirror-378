#!/usr/bin/env python3

import unittest
import sys
import io
from unittest.mock import patch, MagicMock
from basicagi import BasicAGI


class TestBasicAGI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with mocked stdin/stdout"""
        self.original_stdin = sys.stdin
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Mock stdin for AGI environment variables
        self.mock_stdin = io.StringIO()
        self.mock_stdout = io.StringIO()
        self.mock_stderr = io.StringIO()

        sys.stdin = self.mock_stdin
        sys.stdout = self.mock_stdout
        sys.stderr = self.mock_stderr

    def tearDown(self):
        """Restore original stdin/stdout"""
        sys.stdin = self.original_stdin
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def test_agi_initialization_empty_environment(self):
        """Test AGI initialization with empty environment"""
        # Simulate empty AGI environment (just empty line to end reading)
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        self.assertIsInstance(agi.env, dict)
        self.assertEqual(len(agi.env), 0)

    def test_agi_initialization_with_variables(self):
        """Test AGI initialization with AGI variables"""
        # Simulate AGI environment variables
        agi_vars = (
            "agi_request: basic_agi.py\n"
            "agi_channel: PJSIP/test-00000001\n"
            "agi_language: en\n"
            "agi_type: PJSIP\n"
            "agi_uniqueid: 1234567890.1\n"
            "agi_version: 18.0.0\n"
            "agi_callerid: 1234567890\n"
            "agi_calleridname: Test User\n"
            "agi_callingpres: 0\n"
            "agi_callingani2: 0\n"
            "agi_callington: 0\n"
            "agi_callingtns: 0\n"
            "agi_dnid: 1234567890\n"
            "agi_rdnis: unknown\n"
            "agi_context: default\n"
            "agi_extension: 123\n"
            "agi_priority: 1\n"
            "agi_enhanced: 0.0\n"
            "agi_accountcode: \n"
            "agi_threadid: 140123456789\n"
            "\n"  # Empty line to end variable reading
        )

        self.mock_stdin = io.StringIO(agi_vars)
        sys.stdin = self.mock_stdin

        agi = BasicAGI()

        # Check that variables are parsed correctly (without agi_ prefix)
        self.assertEqual(agi.env["request"], "basic_agi.py")
        self.assertEqual(agi.env["channel"], "PJSIP/test-00000001")
        self.assertEqual(agi.env["language"], "en")
        self.assertEqual(agi.env["uniqueid"], "1234567890.1")
        self.assertEqual(agi.env["callerid"], "1234567890")

    def test_debug_functionality(self):
        """Test debug functionality"""
        # Test with debug disabled
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        agi.debug("Test debug message")

        # Check if message was written to stderr
        stderr_content = self.mock_stderr.getvalue()
        self.assertIn("Test debug message", stderr_content)

    def test_get_agi_var_methods(self):
        """Test AGI variable getter methods"""
        agi_vars = (
            "agi_request: basic_agi.py\n"
            "agi_channel: PJSIP/test-00000001\n"
            "agi_callerid: 1234567890\n"
            "\n"
        )

        self.mock_stdin = io.StringIO(agi_vars)
        sys.stdin = self.mock_stdin

        agi = BasicAGI()

        # Test get_agi_var with different key formats
        self.assertEqual(agi.get_agi_var("request"), "basic_agi.py")
        self.assertEqual(agi.get_agi_var("agi_channel"), "PJSIP/test-00000001")
        self.assertEqual(agi.get_agi_var("callerid"), "1234567890")

        # Test non-existent key
        self.assertIsNone(agi.get_agi_var("nonexistent"))

        # Test get_agi_var_keys
        keys = agi.get_agi_var_keys()
        self.assertIn("request", keys)
        self.assertIn("channel", keys)
        self.assertIn("callerid", keys)

        # Test get_all_agi_vars
        all_vars = agi.get_all_agi_vars()
        self.assertEqual(all_vars["request"], "basic_agi.py")
        self.assertEqual(all_vars["channel"], "PJSIP/test-00000001")

    def test_send_command_parsing(self):
        """Test command sending and response parsing"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()

        # Mock stdin for command responses
        test_response = "200 result=1 (timeout)\n"
        agi._send_command = MagicMock()

        # Test parse_mode=1 (result and value parsing)
        agi._send_command.return_value = ("1", "timeout")
        result, value = agi._send_command("TEST COMMAND", 1)
        self.assertEqual(result, "1")
        self.assertEqual(value, "timeout")

    def test_basic_agi_commands(self):
        """Test basic AGI command methods"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()

        # Mock _send_command to avoid actual AGI communication
        agi._send_command = MagicMock()

        # Test various commands
        agi.answer()
        agi._send_command.assert_called_with("ANSWER")

        agi.hangup()
        agi._send_command.assert_called_with("HANGUP")

        agi.set_variable("testvar", "testvalue")
        agi._send_command.assert_called_with('SET VARIABLE testvar "testvalue"')

        agi.verbose("Test message", 1)
        agi._send_command.assert_called_with('VERBOSE "Test message" 1')

    def test_stream_file_command(self):
        """Test stream file command"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        agi._send_command = MagicMock(return_value=("0", None))

        # Test stream_file without offset
        agi.stream_file("welcome", "123")
        agi._send_command.assert_called_with('STREAM FILE welcome "123"', 1)

        # Test stream_file with offset
        agi.stream_file("welcome", "123", 1000)
        agi._send_command.assert_called_with('STREAM FILE welcome "123" 1000', 1)

    def test_database_commands(self):
        """Test database-related commands"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        agi._send_command = MagicMock()

        # Test database_put
        agi.database_put("family", "key", "value")
        agi._send_command.assert_called_with("DATABASE PUT family key value", 2)

        # Test database_get
        agi._send_command.return_value = ("1", "stored_value")
        result = agi.database_get("family", "key")
        agi._send_command.assert_called_with("DATABASE GET family key", 1)

        # Test database_del
        agi.database_del("family", "key")
        agi._send_command.assert_called_with("DATABASE DEL family key", 2)

    def test_say_commands(self):
        """Test speech/TTS commands"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        agi._send_command = MagicMock(return_value=("0", None))

        # Test say_alpha
        agi.say_alpha("hello", "123")
        agi._send_command.assert_called_with('SAY ALPHA "hello" "123"', 1)

        # Test say_digits
        agi.say_digits("12345", "0")
        agi._send_command.assert_called_with('SAY DIGITS 12345 "0"', 1)

        # Test say_number
        agi.say_number(123, "0", "m")
        agi._send_command.assert_called_with('SAY NUMBER 123 "0" m', 1)

    def test_variable_and_function_set(self):
        """Test the generic set method for variables and functions"""
        self.mock_stdin = io.StringIO("\n")
        sys.stdin = self.mock_stdin

        agi = BasicAGI()
        agi._send_command = MagicMock()
        agi.exec = MagicMock()

        # Test setting a regular variable
        agi.set("MYVAR", "myvalue")
        agi._send_command.assert_called_with('SET VARIABLE MYVAR "myvalue"')

        # Test setting a function (contains parentheses)
        agi.set("CDR(userfield)", "test_value")
        agi.exec.assert_called_with("SET", "CDR(userfield)=test_value")

        # Test set_cdr_variable convenience method
        agi.set_cdr_variable("userfield", "cdr_value")
        agi.exec.assert_called_with("SET", "CDR(userfield)=cdr_value")


if __name__ == "__main__":
    unittest.main()