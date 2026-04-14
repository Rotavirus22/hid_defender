# 🛡️ HID Defender — USB Rubber Ducky Attack Detection

**Cybersecurity Final Year Project — Defensive Module**

A real-time Python-based defensive system that monitors USB HID (Human Interface Device) connections, identifies potential keystroke injection attacks (e.g., USB Rubber Ducky, Raspberry Pi Pico HID), and alerts the user when an untrusted device is detected.

---

## 📁 Project Structure

```
hid-defender/
├── hid_defender.py         ← Main monitoring script
├── trusted_devices.json    ← Whitelist of trusted USB input devices
├── requirements.txt        ← Python dependencies
├── hid_alerts.log          ← Auto-created log file (on first run)
└── README.md               ← This file
```

---

## ⚙️ How It Works

### Architecture Overview

```
USB Device Plugged In
        │
        ▼
  [pyudev Monitor]         ← Listens on the Linux udev 'input' subsystem
        │
        ▼
  is_keyboard_hid_device() ← Filters: only keyboard-like devices proceed
        │
        ▼
  extract_device_info()    ← Reads vendor, product, device node from udev properties
        │
        ▼
  is_trusted()             ← Compares against trusted_devices.json (case-insensitive)
        │
       / \
      /   \
  TRUSTED  UNTRUSTED
     │          │
     ▼          ▼
 log_event()  log_event()  +  send_alert()
 [SAFE]       [ALERT]         (zenity GUI or console banner)
```

### Step-by-Step Flow

1. **Startup** — The script loads `trusted_devices.json` and starts a `pyudev.MonitorObserver` listening on the Linux `input` subsystem in a background thread.

2. **Device Detection** — When any USB input device is connected, udev emits an `add` event. The observer callback fires `handle_device_event()`.

3. **HID Filtering** — `is_keyboard_hid_device()` checks for three signals:
   - `ID_INPUT_KEYBOARD=1` (explicit udev keyboard identification)
   - `"keyboard"` in the sysfs path
   - A USB `input` device with `ID_INPUT=1` (broad HID match)

4. **Info Extraction** — `extract_device_info()` climbs the udev parent device chain to find USB-level attributes (`ID_VENDOR`, `ID_MODEL`, etc.), since these are often not present on the `input` node directly.

5. **Trust Check** — `is_trusted()` does a case-insensitive substring match of vendor+product against every whitelist entry. This tolerates minor name variations.

6. **Response**:
   - **Trusted** → `log_event(..., "SAFE")` — informational log entry only.
   - **Untrusted** → `log_event(..., "ALERT")` + `send_alert()`:
     - Tries a `zenity` GTK popup dialog first.
     - Falls back to a colour-highlighted terminal banner if zenity is unavailable or no display is present.

---

## 🚀 Installation & Usage

### 1. Install Dependencies (Linux)

```bash
# Python library for udev
sudo pip3 install pyudev

# GUI alert tool (optional but recommended)
sudo apt install zenity
```

### 2. Run the Monitor

```bash
# Recommended: run as root for full udev attribute access
sudo python3 hid_defender.py
```

### 3. Expected Output (on plug-in)

**Trusted device:**
```
[2025-04-04 14:30:00]  INFO      ✅ SAFE  | Vendor: Logitech             | Product: USB Keyboard             | Node: /dev/input/event4    | Time: 2025-04-04 14:30:00
```

**Untrusted device (e.g., Pico HID / Rubber Ducky):**
```
[2025-04-04 14:31:00]  WARNING   🚨 ALERT | Vendor: Unknown              | Product: Raspberry Pi Pico        | Node: /dev/input/event5    | Time: 2025-04-04 14:31:00

══════════════════════════════════════════════════════════════════════
  !!!  SECURITY ALERT — UNTRUSTED USB HID DEVICE DETECTED  !!!
══════════════════════════════════════════════════════════════════════
  Vendor  : Unknown
  Product : Raspberry Pi Pico
  Node    : /dev/input/event5
  Time    : 2025-04-04 14:31:00
══════════════════════════════════════════════════════════════════════
  ACTION  : Disconnect the device immediately!
══════════════════════════════════════════════════════════════════════
```

---

## 📋 Whitelist Format (`trusted_devices.json`)

```json
[
  {
    "vendor": "Logitech",
    "product": "USB Keyboard",
    "notes": "Optional description field — ignored by the script"
  }
]
```

- **`vendor`** and **`product`** are matched as **case-insensitive substrings**.
- You can add as many entries as needed.
- To find the exact vendor/product of a connected device, run:
  ```bash
  udevadm info --query=all --name=/dev/input/event4
  # or
  cat /sys/class/input/event4/device/name
  lsusb
  ```

---

## 🔧 Key Functions

| Function | Purpose |
|---|---|
| `load_whitelist(filepath)` | Parses `trusted_devices.json` into a list of dicts |
| `extract_device_info(device)` | Reads vendor, product, node from udev device hierarchy |
| `is_keyboard_hid_device(device)` | Filters to keyboard-class HID devices |
| `is_trusted(device_info, whitelist)` | Substring-matches device against whitelist |
| `log_event(device_info, status)` | Writes a `SAFE`/`ALERT` line to log file + terminal |
| `send_alert(device_info)` | Sends zenity GUI popup or terminal banner |
| `handle_device_event(device, wl)` | Orchestrates the full detection–log–alert pipeline |
| `start_monitor(whitelist)` | Starts the real-time udev background observer |

---

## 🔒 Security Considerations

| Aspect | Detail |
|---|---|
| **Root access** | Full udev attributes require `sudo`. Script warns if non-root. |
| **False positives** | Expand whitelist with real device names found via `lsusb` or `udevadm` |
| **False negatives** | Attacker devices may spoof vendor/product — consider adding USB port-level controls |
| **Log tampering** | Logs are append-only; in production, forward to a remote SIEM |
| **Response escalation** | Extend `send_alert()` to trigger automatic port disabling via `uhubctl` |

---

## 📜 Log File Format (`hid_alerts.log`)

```
[2025-04-04 14:30:00]  INFO      ✅ SAFE  | Vendor: Logitech             | Product: USB Keyboard    | Node: /dev/input/event4 | Time: 2025-04-04 14:30:00
[2025-04-04 14:31:00]  WARNING   🚨 ALERT | Vendor: Unknown              | Product: Pico            | Node: /dev/input/event5 | Time: 2025-04-04 14:31:00
```

---

## 🧪 Testing in the Lab

1. Plug in your **trusted** keyboard → should log `SAFE`.
2. Plug in your **Raspberry Pi Pico** configured as HID → should trigger `ALERT` + popup.
3. Check `hid_alerts.log` for the full audit trail.

To simulate without hardware:
```bash
# List current input devices to understand naming
ls /dev/input/
udevadm monitor --subsystem-match=input  # watch live udev events
```

---

*Built for academic demonstration purposes in a controlled lab environment.*
