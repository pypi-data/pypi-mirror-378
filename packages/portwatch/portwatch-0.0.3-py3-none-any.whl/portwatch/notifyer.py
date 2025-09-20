from plyer import notification
import winreg
import subprocess

import platform
import asyncio
import threading



def alert_conflict_sync(port: str, app_name: str = ""):
    """Blocking version — runs in thread."""
    try:
        notification.notify(
            title=f"⚠️ Port {port} in use",
            message=f"Dev port {port} is being used by {app_name or 'unknown process'}.",
            app_name="PortWatch",
            timeout=5
        )
    except Exception as e:
        # Log or ignore — don't crash UI
        print(f"[Notification Error] {e}")

async def alert_conflict(port: str, app_name: str = ""):
    """Async wrapper — runs in background thread."""
    # Don’t await — fire and forget
    asyncio.create_task(
        asyncio.to_thread(alert_conflict_sync, port, app_name)
    )
    
def _windows_notification_is_enebled():
    """
    cheack windows system notification is enebled

    Returns:
        bool : is enabled
    """
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
    """
    cheack linux system notification is enebled

    Returns:
        bool : is enabled
    """
    
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
    """
    cheack macos system notification is enebled

    Returns:
        bool : is enabled
    """
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
    
    