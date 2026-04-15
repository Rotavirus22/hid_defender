# HID Defender - Enhanced Version

Cross-platform USB security application protecting against malicious HID attacks like Rubber Ducky, with keystroke monitoring, command detection, and more.

## Features

### 1. **USB Device Monitoring** ✅
- **Windows**: Real-time WMI-based monitoring (instant detection)
- **macOS**: System profiler polling (2-second intervals)
- **Linux**: USB device scanning

### 2. **HID Whitelisting System** ✅
- Maintain trusted device database (`trusted_devices.json`)
- Track by:
  - Vendor ID (VID)
  - Product ID (PID)
  - Device name
- Auto-block unknown HID devices
- First-run automatic baseline generation

### 3. **Malicious VID Detection** ✅
Pre-configured attack tool detection:
- Raspberry Pi Pico (Pi Pico)
- Adafruit boards
- Arduino variants
- Teensy
- Custom BadUSB devices
- Prototype boards

### 4. **Keystroke Speed Detection** ⚡ (NEW)
Detects rapid, automated keystroke injection:
- **Normal human typing**: 5-10 keystrokes/second
- **Detection threshold**: 15+ keystrokes/second
- **Blocks**: Automated attacks (Rubber Ducky, keystroke injection)
- Real-time keystroke rate monitoring
- Requires: `pip install pynput`

### 5. **First Input Delay Detection** ⚡ (NEW)
Prevents automated attacks that execute immediately:
- **Detection window**: < 1 second from device connection
- **Indicators**: Automated attack (Rubber Ducky behavior)
- **Action**: Immediately block device
- Tracks connection-to-input timing

### 6. **Malicious Command Detection** ⚡ (NEW)
Monitors and blocks suspicious commands:
- PowerShell execution (`powershell`, `pwsh`)
- Command shell (`cmd.exe`, `cmd`)
- Registry modification (`reg add`, `reg delete`)
- Windows Defender disabling (`Set-MpPreference`)
- Service manipulation (`taskkill`, `schtasks`, `net user`)
- Download utilities (`wget`, `curl`, `bitsadmin`)
- File deletion (`del`, `rmdir`, `attrib`)

### 7. **USB Port Control** ⚡ (NEW)
- **Windows**: Enable/disable USB ports globally
- **macOS/Linux**: Manual control guidance
- Administrative access required
- Policy-based restrictions (framework ready)

### 8. **Comprehensive Logging** ✅
CSV-based audit trail (`hid_alerts.log`):
- Device connection timestamp
- Device name, vendor, product
- Hardware ID
- Detection result (TRUSTED/UNTRUSTED/SAFE)
- Action taken (ALLOWED/BLOCKED/DISABLED)
- Easily importable to Excel/analysis tools

### 9. **Alert Notifications** ✅
Platform-specific alerts:
- **Windows**: Modal popup dialog + system beep
- **macOS**: Native Notification Center
- **Linux**: notify-send integration
- Console-based logging

### 10. **Demo Mode** ⚡ (NEW)
Safe simulation for testing:
```bash
python3 hid_defender.py --demo
```

Simulates:
- Fast keystroke injection (20+ keys/sec)
- Malicious command patterns (PowerShell, registry edits)
- Attack detection and alerting
- No actual system impact
- Perfect for testing and demos

## Installation

### Basic Installation
```bash
cd /Users/veel/Downloads/hid-defender
pip install -r requirements.txt
```

### Optional: Keystroke Monitoring
For keystroke speed and command detection:
```bash
pip install pynput
```

### Windows Only: Full Hardware Control
```bash
pip install wmi pypiwin32
```

## Usage

### Run Normal Monitoring
```bash
python3 hid_defender.py
```

**Windows output:**
```
[+] Running on Windows - Real-time WMI monitoring enabled
[+] Admin rights detected. Hardware blocking is active.
[+] Keystroke monitoring enabled
Monitoring hidden USB events...
```

**macOS/Linux output:**
```
[+] Running on macOS - Polling USB devices every 2 seconds
[+] Keystroke monitoring enabled
Monitoring USB devices...
```

### Run Demo Mode
```bash
python3 hid_defender.py --demo
```

Output:
```
============================================================
  DEMO MODE: Rubber Ducky Attack Simulation
============================================================

[DEMO] Simulating fast keystroke injection...
[DEMO] Typing command: powershell Get-Process | Stop-Service

[ALERT] Detected 3 suspicious command patterns:
        - powershell
        - Get-Process
        - Stop-Service

Demo complete! The application would block this attack.
```

### Show Help
```bash
python3 hid_defender.py --help
```

## Detection Mechanisms

### Scenario 1: Unknown Device Connection
```
[USB Device Connected] → [Check Whitelist] → [Not Found]
→ [Check Attack VIDs] → [Block/Alert]
```

### Scenario 2: Rubber Ducky Attack
```
[Device Connected] → [Watch Keystrokes]
→ [Detect 20+ keys/sec] → [ALERT & DISABLE]
```

### Scenario 3: Malicious Command Execution
```
[Keystroke Monitor] → [Detect "powershell"]
→ [Match Pattern] → [BLOCK INPUT & ALERT]
```

## Configuration Files

### `trusted_devices.json`
Whitelist of trusted devices:
```json
[
  {
    "hardware_id": "VID_046DPID_1234",
    "vendor": "Logitech",
    "name": "MX Master Mouse"
  },
  {
    "hardware_id": "VID_413CPID_2000",
    "vendor": "Dell",
    "name": "Dell Keyboard"
  }
]
```

Auto-generated on first run with currently connected devices.

### `hid_alerts.log`
CSV audit log:
```
Time,Device,Vendor,Product,ID,Result,Action
2025-04-14 10:23:45,MX Master,Logitech,Wireless Mouse,...,TRUSTED,ALLOWED
2025-04-14 10:24:12,Unknown Device,Unknown,Generic HID,...,UNTRUSTED,BLOCKED
```

## Thresholds & Tuning

### Keystroke Monitoring
```python
KEYSTROKE_THRESHOLD = 15  # keys/second (normal: 5-10)
FIRST_INPUT_DELAY_THRESHOLD = 1  # seconds
```

Modify in `hid_defender.py` line ~80 to adjust sensitivity.

### Device Debouncing
```python
DEBOUNCE_WINDOW = 5  # seconds
```

Prevents duplicate alerts for same device within 5 seconds.

## Platform Support

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| USB Monitoring | ✅ WMI | ✅ Polling | ✅ Polling |
| Keystroke Monitor | ✅ | ✅ | ✅ |
| Command Detection | ✅ | ✅ | ✅ |
| Screen Lock | ✅ | ❌ | ❌ |
| Hardware Disable | ✅ | ❌ | ❌ |
| Alerts | ✅ Popup | ✅ Native | ✅ notify-send |
| Whitelisting | ✅ | ✅ | ✅ |
| Logging | ✅ | ✅ | ✅ |
| Demo Mode | ✅ | ✅ | ✅ |

## Requirements

### Core
- Python 3.7+
- Cross-platform compatible

### Optional
| Package | Purpose | Platforms |
|---------|---------|-----------|
| `pynput` | Keystroke monitoring | All |
| `wmi` | WMI hardware access | Windows only |
| `pypiwin32` | Windows COM support | Windows only |

## Troubleshooting

### Keystroke monitoring not working
- Install pynput: `pip install pynput`
- May require input monitoring permissions on some systems

### USB monitoring not detecting devices
- **Windows**: Run with admin rights
- **macOS**: May require privacy permissions
- **Linux**: Ensure udev rules are configured

### Demo mode shows no keystroke alerts
- Keystroke monitoring requires `pynput` installed
- Messages still show command pattern detection

## Security Notes

⚠️ **Important Considerations:**
1. **Admin Rights Required**: Hardware blocking requires elevated privileges
2. **Threshold Tuning**: Adjust keystroke threshold carefully to avoid false positives
3. **Performance**: Keystroke monitoring has minimal overhead
4. **Privacy**: All monitoring is local; no data transmitted
5. **Test First**: Use demo mode to verify detection before deployment

## Future Enhancements

- [ ] Web dashboard (Flask-based)
- [ ] USB port enable/disable on macOS/Linux
- [ ] Machine learning-based behavior detection
- [ ] Network-based threat intelligence
- [ ] Centralized logging to remote server
- [ ] GUI application (Tkinter/PyQt)

## License

Educational - Final Year Project: Cybersecurity Defense

## Author

HID Defender Development Team
Enhanced Version: 2025
