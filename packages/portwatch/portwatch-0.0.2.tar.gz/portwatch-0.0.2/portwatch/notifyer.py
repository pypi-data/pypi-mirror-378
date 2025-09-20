from plyer import notification
import winreg
import subprocess

import platform



def alert_conflict(port,app_name):
    notification.notify(
        title="PortWatch Alert",
        message=f"Port {port} is in use by {app_name}.",
        app_name="PortWatch",
        timeout=5  
    )
    
def _windows_notification_is_enebled():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
        )
        value, _ = winreg.QueryValueEx(key, "NOC_GLOBAL_SETTING_TOASTS_ENABLED")
        return bool(value)
    except Exception:
        return True 
    
def _linux_notifications_enabled() -> bool:
    try:
        out = subprocess.check_output(
            ["dbus-send", "--session", "--dest=org.freedesktop.Notifications",
             "--type=method_call", "/org/freedesktop/Notifications",
             "org.freedesktop.Notifications.GetServerInformation"]
        )
        return True if out else False
    except Exception:
        return False
    

def _macos_notifications_enabled() -> bool:
    try:
        out = subprocess.check_output(
            ["defaults", "-currentHost", "read", "com.apple.notificationcenterui", "doNotDisturb"],
            stderr=subprocess.DEVNULL
        ).strip()
        return out != b"1"  # 1 = DND on
    except Exception:
        return True  # assume enabled if cannot check
    
    
def notification_is_enabled():
    system = platform.system().lower()
    
    
    if system == "windows":
        return _windows_notification_is_enebled()
    elif system == "linux":
        return _linux_notifications_enabled()
    elif system == "darwin":
        return _macos_notifications_enabled()
    else:
        return True  # default assume enabled
    
    
# if __name__ == "__main__":
#     print(notification_is_enabled())
#     alert_conflict(500,"Chrome")
    
    