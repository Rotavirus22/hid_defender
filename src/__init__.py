# ==========================================
# HID Defender - Package Init
# ==========================================

"""
HID Defender: Real-time USB HID Device Monitoring
Cross-platform security tool for detecting unauthorized USB input devices
"""

__version__ = "1.0.0"
__author__ = "Cybersecurity Team"

# Handle both package imports and standalone execution
try:
    from hid_defender.config import (
        IS_WINDOWS, IS_MACOS, IS_LINUX,
        ATTACK_VECTORS, BIG_BRANDS,
        KEYSTROKE_THRESHOLD
    )
    from hid_defender.logging_setup import init_logger, log_event
    from hid_defender.keystroke_monitor import KeystrokeMonitor
    from hid_defender.device_monitor import get_macos_usb_devices
    from hid_defender.device_validator import get_whitelist, evaluate
    from hid_defender.alert_system import show_alert
except ImportError:
    # Fallback for direct execution
    pass

__all__ = [
    'init_logger',
    'KeystrokeMonitor',
    'get_macos_usb_devices',
    'get_whitelist',
    'evaluate',
    'show_alert',
    'IS_WINDOWS',
    'IS_MACOS',
    'IS_LINUX',
]
