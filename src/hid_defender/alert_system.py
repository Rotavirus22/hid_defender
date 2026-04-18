# ==========================================
# Alert System & Notifications
# ==========================================

import subprocess
import threading
import platform

# Handle both package imports and standalone execution
try:
    from .config import IS_WINDOWS, IS_MACOS, IS_LINUX
except ImportError:
    from config import IS_WINDOWS, IS_MACOS, IS_LINUX

# Import platform-specific modules at module level for patching
import ctypes
if IS_WINDOWS:
    try:
        import winsound
    except ImportError:
        winsound = None
else:
    winsound = None


def play_alert_sound():
    """Play a system alert sound based on platform."""
    if IS_WINDOWS and winsound:
        try:
            winsound.Beep(1000, 400)
            winsound.Beep(1000, 400)
        except:
            pass
    elif IS_MACOS:
        try:
            subprocess.run(["afplay", "/System/Library/Sounds/Alarm.aiff"], timeout=2)
        except:
            pass
    elif IS_LINUX:
        try:
            subprocess.run(["beep"], timeout=2)
        except:
            pass


def show_alert(info):
    """Shows a loud, modal security warning to the user."""
    if IS_WINDOWS and ctypes:
        def _popup():
            try:
                title = "SECURE HID DEFENDER: THREAT DETECTED"
                msg = (
                    "!!! UNAUTHORIZED USB DEVICE DETECTED !!!\n\n"
                    f"Device Name: {info['name']}\n"
                    f"Hardware ID: {info['id']}\n\n"
                    "Action Taken: The workstation was locked and the device has been flagged."
                )
                ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10 | 0x1000 | 0x10000)
            except:
                pass

        threading.Thread(target=_popup, daemon=True).start()
    
    elif IS_MACOS:
        # Use native macOS notification
        def _macos_alert():
            title = "SECURE HID DEFENDER: THREAT DETECTED"
            msg = f"Unauthorized USB device detected: {info['name']}"
            hw_id = info['id']
            script = f'display notification "{msg}" with title "{title}" subtitle "Hardware ID: {hw_id}"'
            try:
                subprocess.run(["osascript", "-e", script], timeout=5)
            except:
                pass
        
        threading.Thread(target=_macos_alert, daemon=True).start()
    
    elif IS_LINUX:
        # Use notify-send for Linux
        def _linux_alert():
            title = "SECURE HID DEFENDER: THREAT DETECTED"
            msg = f"Unauthorized USB device: {info['name']} ({info['id']})"
            try:
                subprocess.run(["notify-send", title, msg], timeout=5)
            except:
                pass
        
        threading.Thread(target=_linux_alert, daemon=True).start()


def lock_workstation():
    """Lock the workstation (Windows only)."""
    if IS_WINDOWS and ctypes:
        try:
            ctypes.windll.user32.LockWorkStation()
            return True
        except:
            return False
    else:
        raise NotImplementedError("Workstation locking is only supported on Windows")
