from plyer import notification

import asyncio
 



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
    
