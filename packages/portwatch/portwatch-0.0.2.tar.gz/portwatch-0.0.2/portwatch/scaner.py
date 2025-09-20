# scanner.py

import asyncio
import psutil
from typing import List, Dict, Any

# ✅ Import from file_utils
from .utils import load_dev_ports, get_port_description

# No more global cache — load fresh on every scan (or cache in UI if needed)
def check_for_conflict(port: int) -> bool:
    return port in load_dev_ports()


def _scan_ports_sync(filter_str: str | None = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    try:
        for conn in psutil.net_connections(kind="inet"):
            if not conn.laddr:
                continue
            try:
                port = int(conn.laddr.port)
            except Exception:
                continue

            pid = conn.pid
            status = conn.status or ""
            process_name = ""
            if pid:
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except Exception:
                    process_name = ""

            matches_filter = (
                filter_str is None or
                filter_str.lower() in process_name.lower() or
                filter_str in str(port)
            )

            if matches_filter and pid != 0:
                results.append({
                    "pid": pid,
                    "port": port,
                    "process_name": process_name,
                    "status": status,
                    "note": get_port_description(port) if check_for_conflict(port) else ""
                })

    except Exception:
        return []
    return results


async def scan_ports(filter_str: str | None = None) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_scan_ports_sync, filter_str)


async def scan_changes(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def _diff(old, new):
        return [item for item in new if item not in old]
    return await asyncio.to_thread(_diff, old_data, new_data)