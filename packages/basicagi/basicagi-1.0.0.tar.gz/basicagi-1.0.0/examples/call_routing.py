#!/usr/bin/env python3
"""
Advanced Call Routing Example

This script demonstrates:
- Complex call routing logic
- Database lookups for routing decisions
- Time-based routing
- DID number processing
- Call forwarding and transfer

Usage in Asterisk dialplan:
    exten => _+1XXXXXXXXXX,1,AGI(call_routing.py,${EXTEN})
    same => n,Hangup()
"""

from basicagi import BasicAGI
import time


def get_business_hours():
    """Check if current time is within business hours"""
    current_hour = time.localtime().tm_hour
    current_day = time.localtime().tm_wday  # 0 = Monday, 6 = Sunday

    # Business hours: Monday-Friday 9 AM to 5 PM
    if 0 <= current_day <= 4 and 9 <= current_hour < 17:
        return True
    return False


def main():
    """Advanced call routing script"""
    agi = BasicAGI()

    # Get DID number from arguments
    did_number = agi.get_agi_var("arg_1") or agi.get_agi_var("extension")
    caller_id = agi.get_agi_var("callerid")

    agi.answer()

    # Log the call
    agi.verbose(f"Routing call from {caller_id} to DID {did_number}", 1)

    # Set initial CDR variables
    agi.set_cdr_variable("routing_script", "call_routing")
    agi.set_cdr_variable("did_number", did_number)

    # Look up routing information in database
    route_info = agi.database_get("routing", f"did/{did_number}")

    if route_info:
        # Parse route info (format: "extension:department:priority")
        try:
            extension, department, priority = route_info.split(":")
            agi.verbose(f"Found routing: {extension} in {department} (priority {priority})", 1)
        except ValueError:
            # Fallback if format is incorrect
            extension = route_info
            department = "unknown"
            priority = "1"
    else:
        # No specific routing found, use default
        agi.verbose(f"No routing found for DID {did_number}, using default", 1)
        extension = "100"  # Default reception
        department = "reception"
        priority = "1"

    # Check for call forwarding
    forward_info = agi.database_get("routing", f"forward/{extension}")
    if forward_info:
        agi.verbose(f"Call forwarding active for {extension} -> {forward_info}", 1)
        extension = forward_info
        agi.set_cdr_variable("forwarded", "yes")

    # Check business hours
    is_business_hours = get_business_hours()
    agi.set_cdr_variable("business_hours", "yes" if is_business_hours else "no")

    if not is_business_hours:
        # After hours routing
        after_hours_ext = agi.database_get("routing", f"after_hours/{department}")
        if after_hours_ext:
            extension = after_hours_ext
            agi.verbose(f"After hours routing to {extension}", 1)
        else:
            # Default after hours - go to voicemail
            agi.stream_file("after-hours")
            agi.exec("Voicemail", f"{extension},u")
            agi.hangup()
            return

    # Check if caller is in VIP list
    vip_status = agi.database_get("callers", f"vip/{caller_id}")
    if vip_status:
        agi.verbose(f"VIP caller {caller_id} detected", 1)
        agi.set_cdr_variable("vip_caller", "yes")
        # VIP callers get priority routing
        vip_extension = agi.database_get("routing", f"vip/{department}")
        if vip_extension:
            extension = vip_extension

    # Check if extension is available (simple presence check)
    presence = agi.database_get("presence", extension)
    if presence == "unavailable":
        agi.verbose(f"Extension {extension} is unavailable", 1)
        # Try backup extension
        backup_ext = agi.database_get("routing", f"backup/{extension}")
        if backup_ext:
            extension = backup_ext
            agi.set_cdr_variable("used_backup", "yes")
        else:
            # Send to voicemail
            agi.stream_file("extension-unavailable")
            agi.exec("Voicemail", f"{extension},u")
            agi.hangup()
            return

    # Set final routing information
    agi.set_cdr_variable("final_extension", extension)
    agi.set_cdr_variable("department", department)

    # Play custom greeting if available
    greeting_file = agi.database_get("greetings", f"{department}/incoming")
    if greeting_file:
        agi.stream_file(greeting_file)

    # Perform the actual call routing
    agi.verbose(f"Routing call to extension {extension}", 1)

    # Set caller ID name with department info
    agi.exec("Set", f"CALLERID(name)={department.upper()}: {agi.get_agi_var('calleridname') or caller_id}")

    # Dial with appropriate options
    dial_options = "t"  # Allow transfer
    if vip_status:
        dial_options += "r"  # Ring instead of music on hold for VIP

    # Record call start time
    agi.database_put("call_logs", f"{int(time.time())}", f"{caller_id}->{extension}")

    # Execute the dial
    dial_result = agi.exec("Dial", f"PJSIP/{extension}@internal,30,{dial_options}")

    # Check dial status
    dial_status = agi.get_variable("DIALSTATUS")
    agi.set_cdr_variable("dial_status", dial_status or "unknown")

    if dial_status in ["NOANSWER", "BUSY", "CHANUNAVAIL"]:
        # Call wasn't answered, offer voicemail
        agi.stream_file("call-not-answered")
        agi.stream_file("leaving-voicemail")
        agi.exec("Voicemail", f"{extension},u")

    agi.hangup()


if __name__ == "__main__":
    main()