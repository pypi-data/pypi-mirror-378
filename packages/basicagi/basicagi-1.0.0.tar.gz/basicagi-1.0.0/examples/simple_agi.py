#!/usr/bin/env python3
"""
Simple AGI Script Example

This script demonstrates basic AGI functionality:
- Answering a call
- Playing an audio file
- Getting caller information
- Hanging up

Usage in Asterisk dialplan:
    exten => 123,1,AGI(simple_agi.py)
    same => n,Hangup()
"""

from basicagi import BasicAGI


def main():
    """Main AGI script execution"""
    # Create AGI instance
    agi = BasicAGI()

    # Answer the call
    agi.answer()

    # Get caller information
    caller_id = agi.get_agi_var("callerid")
    channel = agi.get_agi_var("channel")
    extension = agi.get_agi_var("extension")

    # Log call information
    agi.verbose(f"Call from {caller_id} on channel {channel} to extension {extension}", 1)

    # Play welcome message
    agi.stream_file("welcome")

    # Say the caller ID digits
    if caller_id and caller_id != "unknown":
        agi.say_digits(caller_id)

    # Set a CDR variable for tracking
    agi.set_cdr_variable("script_used", "simple_agi")

    # Hang up the call
    agi.hangup()


if __name__ == "__main__":
    main()