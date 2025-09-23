#!/usr/bin/env python3
"""
Interactive Voice Response (IVR) Menu Example

This script demonstrates an IVR system with:
- Multiple menu options
- Digit collection
- Call routing
- Error handling
- Loop back on invalid input

Usage in Asterisk dialplan:
    exten => 100,1,AGI(ivr_menu.py)
    same => n,Hangup()
"""

from basicagi import BasicAGI


def main():
    """Main IVR menu execution"""
    agi = BasicAGI()

    # Answer the call
    agi.answer()

    # Get caller information
    caller_id = agi.get_agi_var("callerid")
    agi.verbose(f"IVR call from {caller_id}", 1)

    # Set CDR variable
    agi.set_cdr_variable("ivr_session", "started")

    # Main menu loop
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        # Play main menu
        # Menu: Press 1 for Sales, 2 for Support, 3 for Billing, 0 for Operator
        digit = agi.get_option("main-menu", "1230*#", 10000)  # 10 second timeout

        if digit == "1":
            # Sales department
            agi.stream_file("connecting-to-sales")
            agi.set_cdr_variable("department", "sales")
            # Transfer to sales extension (replace with your actual extension)
            agi.exec("Dial", "PJSIP/sales@internal,30,t")
            break

        elif digit == "2":
            # Support department
            agi.stream_file("connecting-to-support")
            agi.set_cdr_variable("department", "support")
            # Transfer to support extension
            agi.exec("Dial", "PJSIP/support@internal,30,t")
            break

        elif digit == "3":
            # Billing department
            agi.stream_file("connecting-to-billing")
            agi.set_cdr_variable("department", "billing")
            # Transfer to billing extension
            agi.exec("Dial", "PJSIP/billing@internal,30,t")
            break

        elif digit == "0":
            # Operator
            agi.stream_file("connecting-to-operator")
            agi.set_cdr_variable("department", "operator")
            # Transfer to operator
            agi.exec("Dial", "PJSIP/operator@internal,30,t")
            break

        elif digit == "*":
            # Return to main menu (restart)
            agi.stream_file("returning-to-main-menu")
            attempts = 0  # Reset attempts
            continue

        elif digit == "#":
            # Hang up
            agi.stream_file("goodbye")
            break

        else:
            # Invalid option or timeout
            attempts += 1
            if attempts < max_attempts:
                agi.stream_file("invalid-option-try-again")
            else:
                agi.stream_file("too-many-invalid-attempts")
                agi.stream_file("connecting-to-operator")
                agi.set_cdr_variable("department", "operator_fallback")
                agi.exec("Dial", "PJSIP/operator@internal,30,t")
                break

    # Set final CDR variable
    agi.set_cdr_variable("ivr_session", "completed")

    # Hang up
    agi.hangup()


if __name__ == "__main__":
    main()