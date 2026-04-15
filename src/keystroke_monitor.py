# ==========================================
# Keystroke Monitoring Module
# ==========================================

import time
import io
import contextlib
from collections import deque
from .config import IS_MACOS, IS_WINDOWS, KEYSTROKE_THRESHOLD, MALICIOUS_PATTERNS

# Keystroke monitoring
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class KeystrokeMonitor:
    """Monitors keystroke patterns to detect automated attacks."""
    
    def __init__(self, logger):
        self.logger = logger
        self.keystroke_times = deque(maxlen=20)  # Keep last 20 keystrokes
        self.device_first_input = {}  # Track first input time per device
        self.is_monitoring = False
        self.listener = None
        self.blocked_devices = set()
        
    def on_press(self, key):
        """Callback when a key is pressed."""
        try:
            self.keystroke_times.append(time.time())
            
            # Check keystroke speed
            if len(self.keystroke_times) >= 5:
                time_span = self.keystroke_times[-1] - self.keystroke_times[0]
                if time_span > 0:
                    keystroke_speed = len(self.keystroke_times) / time_span
                    if keystroke_speed > KEYSTROKE_THRESHOLD:
                        self.logger.warning(
                            f"⚠️ SUSPICIOUS KEYSTROKE SPEED: {keystroke_speed:.1f} keys/sec "
                            f"(threshold: {KEYSTROKE_THRESHOLD})"
                        )
                        self.trigger_keystroke_alert(keystroke_speed)
            
            # Check for malicious commands
            if hasattr(key, 'char') and key.char:
                self.check_command_patterns(key.char)
                
        except AttributeError:
            pass
    
    def on_release(self, key):
        """Callback when a key is released."""
        pass
    
    def check_command_patterns(self, char):
        """Detect malicious command patterns in typed input."""
        # This is a simplified version - in production, you'd buffer input
        pass
    
    def trigger_keystroke_alert(self, speed):
        """Alert when suspicious keystroke speed detected."""
        msg = f"Automated keystroke attack detected: {speed:.1f} keys/sec"
        self.logger.error(msg)
        
        # Play alert sound
        if IS_WINDOWS:
            try:
                import winsound
                winsound.Beep(1200, 200)
                winsound.Beep(1200, 200)
            except:
                pass
    
    def start(self):
        """Start monitoring keystrokes."""
        if not PYNPUT_AVAILABLE:
            self.logger.warning("Keystroke monitoring requires pynput. Install with: pip install pynput")
            return
            
        if self.is_monitoring:
            return
        
        try:
            self.is_monitoring = True
            
            # On macOS, suppress stderr to hide permission warnings, then provide our own message
            if IS_MACOS:
                # Try to start with stderr suppressed
                with contextlib.redirect_stderr(io.StringIO()) as stderr_capture:
                    self.listener = keyboard.Listener(
                        on_press=self.on_press, 
                        on_release=self.on_release
                    )
                    self.listener.start()
                    time.sleep(0.1)  # Brief moment for listener to initialize
                
                # Check if the listener is working
                stderr_output = stderr_capture.getvalue()
                if "not trusted" in stderr_output.lower() or not self.listener.is_alive():
                    self.is_monitoring = False
                    self.listener = None
                    self.logger.warning("⚠️  Keystroke monitoring disabled - requires accessibility permissions")
                    self.logger.warning("   On macOS, grant access via: System Preferences → Privacy & Security → Accessibility")
                    self.logger.warning("   Add your Terminal or Python to the list, then restart this script")
                    self.logger.warning("   → Continuing with USB device monitoring only")
                    return
                else:
                    self.logger.info("Keystroke monitoring started")
            else:
                self.listener = keyboard.Listener(
                    on_press=self.on_press, 
                    on_release=self.on_release
                )
                self.listener.start()
                self.logger.info("Keystroke monitoring started")
                
        except Exception as e:
            self.is_monitoring = False
            self.listener = None
            self.logger.warning(f"Failed to start keystroke monitoring: {e}")
            self.logger.warning("→ Continuing with USB device monitoring only")
    
    def stop(self):
        """Stop monitoring keystrokes."""
        if self.listener and self.is_monitoring:
            self.listener.stop()
            self.is_monitoring = False
            self.logger.info("Keystroke monitoring stopped")
