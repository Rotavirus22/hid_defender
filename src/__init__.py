# ==========================================
# HID Defender - Package Init
# ==========================================

"""
HID Defender: Real-time USB HID Device Monitoring
Cross-platform security tool for detecting unauthorized USB input devices
"""

__version__ = "1.0.0"
__author__ = "Cybersecurity Team"

from .config import (
    IS_WINDOWS, IS_MACOS, IS_LINUX,
    ATTACK_VECTORS, BIG_BRANDS,
    KEYSTROKE_THRESHOLD
)
from .logging_setup import init_logger, log_event
from .keystroke_monitor import KeystrokeMonitor
from .device_monitor import get_macos_usb_devices
from .device_validator import (
    get_whitelist, save_whitelist, evaluate, parse_device
)
from .alert_system import show_alert, play_alert_sound

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
