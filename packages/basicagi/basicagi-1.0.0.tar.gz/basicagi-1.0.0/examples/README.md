# BasicAGI Examples

This directory contains example AGI scripts demonstrating various features and use cases of the BasicAGI library.

## Examples Overview

### 1. `simple_agi.py` - Basic AGI Script
A simple introductory example that demonstrates:
- Basic AGI initialization
- Answering calls
- Playing audio files
- Accessing caller information
- Setting CDR variables

**Usage in dialplan:**
```
exten => 123,1,AGI(simple_agi.py)
same => n,Hangup()
```

### 2. `ivr_menu.py` - Interactive Voice Response
An IVR menu system demonstrating:
- Multiple menu options
- Digit collection with timeouts
- Call routing to different departments
- Error handling and retry logic
- Menu navigation

**Usage in dialplan:**
```
exten => 100,1,AGI(ivr_menu.py)
same => n,Hangup()
```

**Menu Options:**
- Press 1 for Sales
- Press 2 for Support
- Press 3 for Billing
- Press 0 for Operator
- Press * to return to main menu
- Press # to hang up

### 3. `voicemail_notification.py` - Voicemail System
A voicemail checking system demonstrating:
- Database operations
- Text-to-speech functionality
- Date/time speaking
- Conditional logic based on message counts
- Message playback options

**Usage in dialplan:**
```
exten => _VM.,1,AGI(voicemail_notification.py,${EXTEN:2})
same => n,Hangup()
```

### 4. `call_routing.py` - Advanced Call Routing
A comprehensive call routing system demonstrating:
- DID number processing
- Database-driven routing decisions
- Time-based routing (business hours)
- VIP caller handling
- Call forwarding
- Presence checking
- Backup routing

**Usage in dialplan:**
```
exten => _+1XXXXXXXXXX,1,AGI(call_routing.py,${EXTEN})
same => n,Hangup()
```

## Installation and Setup

1. **Copy scripts to AGI directory:**
   ```bash
   sudo cp examples/*.py /var/lib/asterisk/agi-bin/
   sudo chmod +x /var/lib/asterisk/agi-bin/*.py
   ```

2. **Set proper ownership:**
   ```bash
   sudo chown asterisk:asterisk /var/lib/asterisk/agi-bin/*.py
   ```

3. **Install BasicAGI library:**
   ```bash
   pip install basicagi
   ```

## Database Setup

Some examples require database entries. Here are sample database commands for Asterisk CLI:

### For call_routing.py:
```
database put routing did/+15551234567 100:reception:1
database put routing after_hours/reception 999
database put routing backup/100 101
database put callers vip/5551234567 yes
database put presence 100 available
database put greetings reception/incoming welcome-reception
```

### For voicemail_notification.py:
```
database put voicemail 100/count 3
database put voicemail 100/last_message_time 1640995200
```

## Audio Files

The examples reference various audio files. You'll need to have these recorded in your Asterisk sounds directory:

### Required Audio Files:
- `welcome` - Welcome greeting
- `main-menu` - IVR main menu prompt
- `connecting-to-sales` - "Connecting to sales department"
- `connecting-to-support` - "Connecting to support department"
- `connecting-to-billing` - "Connecting to billing department"
- `connecting-to-operator` - "Connecting to operator"
- `invalid-option-try-again` - "Invalid option, please try again"
- `too-many-invalid-attempts` - "Too many invalid attempts"
- `after-hours` - After hours message
- `extension-unavailable` - Extension unavailable message
- Voicemail prompts (vm-*)

## Customization

### Modifying Examples

1. **Update extension numbers** in the scripts to match your Asterisk setup
2. **Modify department names** and routing logic as needed
3. **Add your own audio files** and update file references
4. **Customize database keys** and values for your environment

### Adding New Features

The examples provide a foundation for building more complex AGI applications:

- **Call recording integration**
- **CRM system integration**
- **Call analytics and reporting**
- **Advanced IVR with speech recognition**
- **Conference room management**
- **Call queuing systems**

## Debugging

Enable debugging for troubleshooting:

```bash
export AGI_DEBUG=true
asterisk -rvvv
```

Or in your dialplan:
```
exten => 123,1,Set(AGI_DEBUG=true)
same => n,AGI(your_script.py)
```

## Security Considerations

- Always validate user input
- Sanitize database queries
- Limit script execution time
- Use appropriate file permissions
- Consider rate limiting for external API calls

## Support

For questions about these examples:
1. Check the main BasicAGI documentation
2. Review Asterisk AGI documentation
3. Open an issue on the GitHub repository