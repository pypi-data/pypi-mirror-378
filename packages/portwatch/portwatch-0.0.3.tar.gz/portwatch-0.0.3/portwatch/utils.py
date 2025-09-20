# file_utils.py
import yaml
from pathlib import Path
from typing import List, Optional

# Default dev ports with descriptions
DEFAULT_DEV_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3000: "React/Vite Dev",
    5000: "Flask Dev",
    8000: "Django/FastAPI Dev",
    8080: "Tomcat/Java Dev",
    3306: "MySQL",
    5432: "PostgreSQL",
    27017: "MongoDB",
    9092: "Kafka",
}

CONFIG_FILE_NAME = ".portconfig"
CONFIG_PATH = Path(CONFIG_FILE_NAME)


def load_dev_ports() -> List[int]:
    """
    Load developer ports from .portconfig YAML file.
    If file doesn't exist, creates it with defaults.
    Supports:
      - dict: {3000: "React", 8080: "API"}
      - list: [3000, 8080, "5000"]
    Returns sorted list of unique valid ports.
    """
    if not CONFIG_PATH.exists():
        save_dev_ports(list(DEFAULT_DEV_PORTS.keys()))
        return list(DEFAULT_DEV_PORTS.keys())

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️ Failed to load {CONFIG_FILE_NAME}: {e}")
        return list(DEFAULT_DEV_PORTS.keys())

    ports = set()

    if isinstance(data, dict):
        for key in data.keys():
            try:
                port = int(key)
                if 1 <= port <= 65535:
                    ports.add(port)
            except (ValueError, TypeError):
                continue
    elif isinstance(data, list):
        for item in data:
            try:
                port = int(item)
                if 1 <= port <= 65535:
                    ports.add(port)
            except (ValueError, TypeError):
                continue
    else:
        print(f"⚠️ Unsupported config format in {CONFIG_FILE_NAME}. Using defaults.")
        return list(DEFAULT_DEV_PORTS.keys())

    return sorted(ports)


def save_dev_ports(ports: List[int]):
    """
    Save port list to .portconfig as a dictionary with default descriptions.
    Preserves human-readable format.
    """
    port_dict = {}
    for port in sorted(set(ports)):  # dedupe + sort
        if not (1 <= port <= 65535):
            continue  # skip invalid ports
        # Try to preserve existing description, else use default or generic
        port_dict[port] = DEFAULT_DEV_PORTS.get(port, f"Custom Port {port}")

    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                {str(k): v for k, v in port_dict.items()},  # keys as strings for clean YAML
                f,
                sort_keys=False,
                default_flow_style=False,
                indent=2
            )
    except Exception as e:
        print(f"⚠️ Failed to save {CONFIG_FILE_NAME}: {e}")


def add_dev_port(port: int) -> bool:
    """
    Add a single port to config if not already present.
    Returns True if added, False if already exists or invalid.
    """
    if not (1 <= port <= 65535):
        return False
    ports = load_dev_ports()
    if port in ports:
        return False
    ports.append(port)
    save_dev_ports(ports)
    return True


def remove_dev_port(port: int) -> bool:
    """
    Remove a port from config.
    Returns True if removed, False if not found.
    """
    ports = load_dev_ports()
    if port not in ports:
        return False
    ports.remove(port)
    save_dev_ports(ports)
    return True


def reset_dev_ports_to_default():
    """
    Reset .portconfig to default dev ports.
    """
    save_dev_ports(list(DEFAULT_DEV_PORTS.keys()))


def get_port_description(port: int) -> str:
    """
    Get human-readable description for a port.
    """
    ports = load_dev_ports()
    if port not in ports:
        return ""
    # Reload as dict to get description
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, dict):
            desc = data.get(str(port), data.get(port))
            if isinstance(desc, str):
                return desc
    except Exception:
        pass
    return DEFAULT_DEV_PORTS.get(port, f"Port {port}")