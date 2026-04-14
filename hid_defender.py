# ==========================================
# Windows HID Defender - USB Monitoring Tool
# Final Year Project: Cybersecurity Defense
# ==========================================

import os
import sys
import csv
import json
import time
import ctypes
import logging
import winsound
import threading
import subprocess
from datetime import datetime

# WMI is required for Windows hardware events
try:
    import wmi
    import pythoncom
except ImportError:
    print("Error: Please install missing dependencies: pip install wmi pypiwin32")
    sys.exit(1)

# File paths for project data
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
WHITELIST_PATH = os.path.join(DIR_PATH, "trusted_devices.json")
LOG_PATH = os.path.join(DIR_PATH, "hid_alerts.log")

# Globals for logic processing
RECENT_SEEN = {}  # Helps avoid double-logging the same device (debouncing)

# List of major peripheral brands to reduce false positives
# These are used in our heuristic check.
BIG_BRANDS = [
    "logitech", "dell", "hp", "microsoft", "lenovo", "corsair", 
    "razer", "steelseries", "asus", "acer", "apple", "intel"
]

# Hardware Vendor IDs (VIDs) associated with attack tools (Pi Pico, Rubber Ducky, etc.)
# If a device has one of these, it's flagged immediately.
ATTACK_VECTORS = [
    "VID_2E8A", "VID_239A", "VID_16C0", "VID_2341", 
    "VID_1209", "VID_6666", "VID_CAFE", "VID_1B4F"
]

# Mapping for suspicious VIDs to friendly names
SUSPICIOUS_MAPPING = {
    "VID_2E8A": "Raspberry Pi",
    "VID_239A": "Adafruit",
    "VID_16C0": "Teensy/Arduino",
    "VID_2341": "Arduino",
    "VID_1209": "Open Source Platform",
    "VID_6666": "Prototype/Generic",
    "VID_CAFE": "Prototype/BadUSB",
    "VID_1B4F": "SparkFun"
}

class CSVLogFormatter(logging.Formatter):
    """Custom formatter to keep our audit log in CSV format."""
    def format(self, record):
        # If the message is a dict (our device info), format it as CSV
        if isinstance(record.msg, dict):
            info = record.msg
            res = getattr(record, 'result', 'UNKNOWN')
            act = getattr(record, 'action', 'NONE')
            return f"{info['time']},{info['name']},{info['vendor']},{info['product']},{info['id']},{res},{act}"
        return super().format(record)

def check_admin():
    """Returns True if the script is running with elevated privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- Logging System ---

def init_logger():
    """Sets up unified logging for both console and CSV audit log."""
    logger = logging.getLogger("HID_Defender")
    logger.setLevel(logging.INFO)
    
    # 1. Console Handler (Friendly output)
    console_fmt = logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(console_fmt)
    logger.addHandler(ch)

    # 2. CSV File Handler (Audit log)
    # Ensure header exists first
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["Time", "Device", "Vendor", "Product", "ID", "Result", "Action"])
    
    fh = logging.FileHandler(LOG_PATH, encoding='utf-8')
    fh.setFormatter(CSVLogFormatter())
    logger.addHandler(fh)
    
    return logger

log = init_logger()

def log_event(info, result, action):
    """Helper to route a detection event through our logging system."""
    # We pass the info dict as the message and extra metadata for the CSV formatter
    log.info(info, extra={'result': result, 'action': action})

# --- Whitelist Management ---

def get_whitelist():
    """Loads the trusted devices from JSON."""
    if not os.path.exists(WHITELIST_PATH):
        return []
    try:
        with open(WHITELIST_PATH, "r") as f:
            return json.load(f)
    except:
        return []

def save_whitelist(data):
    """Saves your currently connected devices as a baseline."""
    with open(WHITELIST_PATH, "w") as f:
        json.dump(data, f, indent=4)

def run_baseline_setup(wmi_obj):
    """First-run logic to trust currently connected hardware."""
    current_whitelist = get_whitelist()
    if current_whitelist:
        return current_whitelist

    print("Initial startup: Establishing trusted hardware baseline...")
    new_baseline = []
    
    for dev in wmi_obj.Win32_PnPEntity():
        if is_valid_hid(dev):
            details = parse_device(dev)
            hw_id = details['id']
            # Extract just the VID/PID part for the signature
            if "VID_" in hw_id and "PID_" in hw_id:
                try:
                    idx = hw_id.index("VID_")
                    hw_id = hw_id[idx:idx+17]
                except: pass

            entry = {"hardware_id": hw_id, "vendor": details['vendor'], "name": details['name']}
            if entry not in new_baseline:
                new_baseline.append(entry)
                
    save_whitelist(new_baseline)
    print(f"Done. {len(new_baseline)} devices registered as trusted.")
    return new_baseline

# --- Hardware Parsing ---

def is_valid_hid(dev):
    """Filters out non-HID system components."""
    try:
        pnp = str(getattr(dev, "PNPDeviceID", "")).upper()
        desc = str(getattr(dev, "Description", "")).lower()
        guid = str(getattr(dev, "ClassGuid", "")).lower()
        
        # We only care about physical USB devices, not generic system bus stuff
        if "USB" not in pnp: return False
        
        # Ignore Root Hubs and Host Controllers (too much noise)
        if "hub" in desc or "host controller" in desc: return False

        # If it's explicitly HID/Input, catch it immediately
        if guid == "{745a17a0-74d3-11d0-b6fe-00a0c90f57da}": return True
        
        # Broaden to catch Audio Interfaces/Composite devices that have buttons
        keywords = ["hid", "keyboard", "mouse", "input", "audio", "composite", "media"]
        return any(x in desc for x in keywords)
    except:
        return False

def parse_device(dev):
    """Builds a friendly dictionary of device details."""
    pnp_id = str(getattr(dev, "PNPDeviceID", "Unknown"))
    name = str(getattr(dev, "Name", "Unknown")).strip()
    manu = str(getattr(dev, "Manufacturer", "Unknown")).strip()
    prod = str(getattr(dev, "Caption", "Unknown")).strip()

    # Smart Vendor Mapping (Fixes generic Windows strings)
    vendor = manu if manu and "standard" not in manu.lower() else "Unknown"
    brand_vids = {
        "VID_1B1C": "Corsair", "VID_046D": "Logitech", "VID_1532": "Razer",
        "VID_045E": "Microsoft", "VID_413C": "Dell", "VID_03F0": "HP", "VID_17EF": "Lenovo"
    }
    for vid, brand in brand_vids.items():
        if vid in pnp_id.upper():
            vendor = brand
            break
            
    # Secondary check for known suspicious/development boards
    if vendor == "Unknown":
        for vid, brand in SUSPICIOUS_MAPPING.items():
            if vid in pnp_id.upper():
                vendor = brand
                break

    # Final Name Refinement
    if ("Input Device" in name or name == "Unknown") and vendor != "Unknown":
        name = f"{vendor} Peripheral"
    elif vendor != "Unknown" and vendor not in name:
        # If the name is generic but we know the vendor, prepend it
        if "HID-compliant" in name or "Standard" in name:
            name = f"{vendor} {name}"

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name, "vendor": vendor, "product": prod, "id": pnp_id
    }

# --- Detection & Response ---

def evaluate(info, whitelist):
    """Analyzes a new connection for suspicious traits."""
    raw_id = info['id'].upper()
    v_low = info['vendor'].lower()
    p_low = info['product'].lower()
    n_low = info['name'].lower()

    # Step 1: Check Blacklist (Attack Tools)
    for bad_vid in ATTACK_VECTORS:
        if bad_vid in raw_id:
            return "UNTRUSTED", "BLOCKED"

    # Step 2: Check Personal Whitelist
    for item in whitelist:
        stored_id = item.get("hardware_id", "").upper()
        if stored_id and stored_id in raw_id:
            return "TRUSTED", "ALLOWED"

    # Step 3: Heuristic Brand Check (Trusted manufacturers)
    if any(brand in v_low or brand in p_low or brand in n_low for brand in BIG_BRANDS):
        return "SAFE", "ALLOWED"
        
    # Step 4: Device Type Heuristic (Mice are usually safe)
    if "mouse" in p_low or "mouse" in n_low:
        return "SAFE", "ALLOWED"

    # Default to safe if nothing else matched (Per requirement)
    return "SAFE", "ALLOWED"

def kill_device(hw_id):
    """Forces Windows to disable the specific hardware port. Requires Admin."""
    log.warning(f"Response Triggered: Disabling hardware {hw_id}")
    try:
        # We wrap in quotes to handle the & symbols in the ID
        proc = subprocess.run(f'pnputil /disable-device "{hw_id}"', 
                             shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            log.info("Success: Device disabled.")
            return True
        log.error(f"Failed to disable: {proc.stderr.strip()}")
    except Exception as e:
        log.error(f"Error executing kill command: {e}")
    return False

def show_alert(info):
    """Shows a loud, modal security warning to the user."""
    def _popup():
        title = "SECURE HID DEFENDER: THREAT DETECTED"
        msg = (
            "!!! UNAUTHORIZED USB DEVICE DETECTED !!!\n\n"
            f"Device Name: {info['name']}\n"
            f"Hardware ID: {info['id']}\n\n"
            "Action Taken: The workstation was locked and the device has been flagged."
        )
        # 0x10 = Error Icon, 0x1000 = System Modal (Top), 0x10000 = Foreground Focus
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10 | 0x1000 | 0x10000)

    threading.Thread(target=_popup, daemon=True).start()

def handle_new_event(dev_obj, whitelist):
    """Main event coordinator for a new hardware plug-in."""
    info = parse_device(dev_obj)
    
    # Debouncing (Prevents multiple logs for a single physical connection)
    base_sig = info['id']
    if "VID_" in base_sig.upper():
        try:
            start = base_sig.upper().index("VID_")
            base_sig = base_sig[start:start+17]
        except: pass
            
    now = time.time()
    if base_sig in RECENT_SEEN and (now - RECENT_SEEN[base_sig] < 5):
        return
    RECENT_SEEN[base_sig] = now

    result, action = evaluate(info, whitelist)
    
    # Log the event IMMEDIATELY before starting response actions
    # This prevents missing logs if a response (like locking/disabling) hangs or crashes
    log_event(info, result, action)

    if result == "TRUSTED":
        # Additional console feedback
        print(f"[*] Trusted device connected: {info['name']}")
    elif result == "SAFE":
        # Additional console feedback
        print(f"[+] Safe device permitted: {info['name']}")
    else:  # UNTRUSTED
        print("\n" + "!"*50)
        print("! SECURITY WARNING: UNTRUSTED HID HARDWARE !")
        print(f"! Target ID: {info['id']}")
        print("!"*50 + "\n")

        # Play sound
        try:
            winsound.Beep(1000, 400)
            winsound.Beep(1000, 400)
        except: pass

        # Instant Mitigation: Lock screen (doesn't need admin)
        try:
            log.info("Locking screen to stop keyboard payloads...")
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            print(f"Warning: Failed to lock station: {e}")

        # Hardware Mitigation: Disable device (needs admin)
        if check_admin():
            action = "DISABLED"
            kill_device(info['id'])
        
        show_alert(info)

def main():
    print("-" * 50)
    print(" HID Defender - Real-time USB Monitor")
    print("-" * 50)

    if not check_admin():
        print("[!] Note: Running without Admin. Hardware blocking is disabled.")
    else:
        print("[+] Admin rights detected. Hardware blocking is active.")

    pythoncom.CoInitialize()
    wmi_client = wmi.WMI()
    
    # Setup initial trust
    trusted_baseline = run_baseline_setup(wmi_client)
    
    print(f"Monitoring hidden USB events... (Log file: {os.path.basename(LOG_PATH)})")
    
    # Watch for hardware creation events from the OS
    watcher = wmi_client.Win32_PnPEntity.watch_for("creation")
    try:
        while True:
            try:
                # This blocks until a new device is connected
                new_dev = watcher() 
                if is_valid_hid(new_dev):
                    handle_new_event(new_dev, trusted_baseline)
            except Exception as e:
                # Catch errors during a single event so the whole monitor doesn't die
                log.error(f"Error processing device event: {e}")
                time.sleep(1) # Brief pause to prevent rapid-fire error loops
                
    except KeyboardInterrupt:
        print("\nStopping monitor...")

if __name__ == "__main__":
    main()
