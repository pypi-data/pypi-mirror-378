#!/usr/bin/env python3
"""
Voicemail Notification Example

This script demonstrates:
- Database operations
- Text-to-speech functionality
- Time/date speaking
- Variable handling
- Complex call flow

Usage in Asterisk dialplan:
    exten => _VM.,1,AGI(voicemail_notification.py,${EXTEN:2})
    same => n,Hangup()
"""

from basicagi import BasicAGI
import time


def main():
    """Voicemail notification script"""
    agi = BasicAGI()

    # Get extension from AGI arguments (passed from dialplan)
    extension = agi.get_agi_var("arg_1") or "100"  # Default to 100 if no arg

    agi.answer()

    # Get caller information
    caller_id = agi.get_agi_var("callerid")
    agi.verbose(f"Voicemail check for extension {extension} by {caller_id}", 1)

    # Check voicemail count from database
    vm_count = agi.database_get("voicemail", f"{extension}/count")
    if vm_count is None:
        vm_count = "0"

    # Convert to integer for processing
    try:
        vm_count_int = int(vm_count)
    except (ValueError, TypeError):
        vm_count_int = 0

    # Play greeting
    agi.stream_file("vm-youhave")

    if vm_count_int == 0:
        # No voicemails
        agi.stream_file("vm-no")
        agi.stream_file("vm-messages")
    elif vm_count_int == 1:
        # One voicemail
        agi.say_number(1)
        agi.stream_file("vm-message")
    else:
        # Multiple voicemails
        agi.say_number(vm_count_int)
        agi.stream_file("vm-messages")

    # Get last voicemail timestamp if any messages exist
    if vm_count_int > 0:
        last_vm_time = agi.database_get("voicemail", f"{extension}/last_message_time")
        if last_vm_time:
            try:
                last_time = int(last_vm_time)
                agi.stream_file("vm-last")
                agi.stream_file("vm-message")
                agi.stream_file("vm-received")

                # Say the date and time of last message
                agi.say_datetime(last_time, "", "ABdY 'digits/at' IMp")

            except (ValueError, TypeError):
                agi.verbose("Invalid timestamp in database", 1)

        # Store access time
        current_time = int(time.time())
        agi.database_put("voicemail", f"{extension}/last_accessed", str(current_time))

    # Menu options
    agi.stream_file("vm-press")
    agi.say_number(1)
    agi.stream_file("vm-to-listen-to-messages")

    # Wait for digit input
    digit = agi.wait_for_digit(5000)  # 5 second timeout

    if digit == "1":
        # Play messages (in real implementation, you'd iterate through messages)
        agi.stream_file("vm-first")
        agi.stream_file("vm-message")

        # Set CDR variable
        agi.set_cdr_variable("vm_action", "listened")

        # In a real implementation, you would:
        # 1. Get message list from database
        # 2. Play each message file
        # 3. Provide options to delete, save, etc.

        # For demo, just play a sample message
        agi.stream_file("vm-message-number")
        agi.say_number(1)
        # agi.stream_file(f"vm/{extension}/msg0001")  # Play actual message

    else:
        # Exit without listening
        agi.set_cdr_variable("vm_action", "checked_only")

    # Update database with access info
    agi.database_put("voicemail", f"{extension}/last_check_by", caller_id or "unknown")

    # Goodbye
    agi.stream_file("vm-goodbye")
    agi.hangup()


if __name__ == "__main__":
    main()