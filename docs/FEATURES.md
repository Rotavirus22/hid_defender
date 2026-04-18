# HID Defender - Enhanced Version

Cross-platform USB security application protecting against malicious HID attacks like Rubber Ducky, with keystroke monitoring, command detection, and more.

## Features

### 1. **USB Device Monitoring** ✅
- **Windows**: Real-time WMI-based monitoring
- **macOS**: System profiler polling (2-second intervals)
- **Linux**: USB device scanning

### 2. **HID Whitelisting System** ✅
- Maintain trusted device database (`trusted_devices.json`)
- Match trusted devices by:
  - Vendor ID (VID)
  - Product ID (PID)
- Supports descriptive vendor/name metadata
- First-run baseline generation stores currently connected trusted HID devices

### 3. **Malicious VID Detection** ✅
Pre-configured attack tool detection:
- Raspberry Pi Pico
- Adafruit boards
- Arduino variants
- Teensy
- BadUSB/prototype boards

### 4. **Keystroke Speed Detection** ⚡ (NEW)
Detects rapid, automated typing:
- **Normal human typing**: 5-10 keystrokes/sec
- **Detection threshold**: 15+ keystrokes/sec
- Alerts on suspicious fast input
- Requires `pynput` for keystroke monitoring

### 5. **First Input Delay Detection** ⚡ (NEW)
Detects devices that start typing too quickly after connection:
- **Detection window**: < 1 second
- Indicates automated HID payload behavior
- Triggers alert on suspicious first input timing

### 6. **Malicious Command Detection** ⚡ (NEW)
Detects risky command text in typed input:
- `powershell`, `pwsh`
- `cmd.exe`, `cmd`
- `reg add`, `reg delete`
- `Set-MpPreference`
- `taskkill`, `schtasks`, `net user`
- `wget`, `curl`, `bitsadmin`
- `del`, `rmdir`, `attrib`

### 7. **Optional Windows Device Disable** ⚡
- Uses `pnputil /disable-device` on Windows with Admin rights
- Attempts to disable the detected untrusted HID device
- Does not implement global USB port shutdown

### 8. **Comprehensive Logging** ✅
CSV-style audit log in `hid_alerts.log`:
- Timestamp
- Device name, vendor, product
- Hardware ID
- Detection result
- Action taken
- Reason for decision

### 9. **Alert Notifications** ✅
Platform-specific alert behavior:
- **Windows**: popup dialog + beep
- **macOS**: native notification via `osascript`
- **Linux**: notification via `notify-send`
- Always logs the event in the console and audit log

### 10. **Demo Mode** ⚡ (NEW)
Safe simulation for testing:
```bash
python3 hid_defender.py --demo
```
Simulates:
- fast keystroke injection
- malicious command patterns
- alert generation
- no actual system blocking

### 11. **Administrative Dashboard** ✅
- Flask-based web dashboard in `dashboard/app.py`
- Displays recent HID events, timing metrics, and whitelist items
- Summarizes trusted/untrusted/blocked activity and top alert reasons
- Runs locally at `http://localhost:5000`

## Installation

### Basic Installation
```bash
cd /Users/veel/Downloads/hid-defender
pip install -r requirements.txt
```

### Optional: Keystroke Monitoring
```bash
pip install pynput
```

### Windows Only: Full Monitoring
```bash
pip install wmi pypiwin32
```

> On macOS or Linux, `wmi`/`pypiwin32` cannot be installed, so the Windows WMI path is not available.

## Usage

### Run Normal Monitoring
```bash
python3 hid_defender.py
```

### Run Demo Mode
```bash
python3 hid_defender.py --demo
```

### Show Help
```bash
python3 hid_defender.py --help
```

## Detection Mechanisms

### Unknown HID Device
```
[Device Connected] → [Check Whitelist] → [Check Attack VID] → [Alert/Block if needed]
```

### Fast Typing Attack
```
[Keystroke Monitor] → [Detect >15 keys/sec] → [Alert]
```

### Immediate Payload Execution
```
[Device Connected] → [First keystroke <1s] → [Alert]
```

### Malicious Command Detection
```
[Keystroke Monitor] → [Buffer typed input] → [Match known patterns] → [Alert]
```

## Whitelist Format

Use `trusted_devices.json` to define trusted HID devices.
Example:
```json
[
  {
    "hardware_id": "VID_046D&PID_C52B",
    "vendor": "Logitech",
    "name": "Logitech USB Keyboard"
  },
  {
    "hardware_id": "VID_1B1C&PID_1BAC",
    "vendor": "Standard system devices",
    "name": "USB Input Device"
  }
]
```

## Log Format

`hid_alerts.log` contains entries like:
```
Time,Device,Vendor,Product,ID,Result,Action,Reason
2026-04-15 18:24:14,Logitech USB Keyboard,Logitech,Keyboard,VID_046D&PID_C52B,TRUSTED,ALLOWED,Whitelisted device
2026-04-15 18:24:20,Unknown Device,Unknown,Keyboard,VID_239A&PID_XXXX,UNTRUSTED,BLOCKED,Unknown HID device
```

## Requirements

- Python 3.7+
- `pynput` for keystroke monitoring
- `wmi` and `pypiwin32` for Windows-only monitoring

## Troubleshooting

- If `pynput` is missing, install it with `pip install pynput`
- If `wmi`/`pypiwin32` fails, run on Windows
- Run the tool with Admin rights on Windows for device disable functionality


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

- [x] Web dashboard (Flask-based)
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
