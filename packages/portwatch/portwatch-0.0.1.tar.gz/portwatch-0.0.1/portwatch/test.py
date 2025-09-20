import psutil
from typing import List, Dict, Any
import asyncio


def _test_scan_ports():
    results = []
    try:
        # net_connections(kind="inet") returns IPv4/IPv6 sockets
        for conn in psutil.net_connections(kind="inet"):
            # only interested in local address (listening or established)
            if not conn.laddr:
                continue

            try:
                port = int(conn.laddr.port)
            except Exception:
                continue

            pid = conn.pid  # may be None if permission denied
            status = conn.status or ""
            process_name = ""
            if pid:
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except Exception:
                    # could be AccessDenied or NoSuchProcess
                    process_name = ""
            if filter == None:
                if not pid == 0:
                    results.append({
                        "pid": pid if pid is not None else "",
                        "port": port,
                        "process_name": process_name,
                        "status": status,
                    })
            if not filter == None :
                if (filter in process_name or filter in str(port)) and not pid == 0:
                    results.append({
                        "pid": pid if pid is not None else "",
                        "port": port,
                        "process_name": process_name,
                        "status": status,
                    })
             
    except Exception:
        # On some platforms calling net_connections may raise; fail gracefully with empty list
        return []
    return results

def _test_map_table(list):
    
    table_data = []
    
    if type(list[0]) == dict:
        for l in list:
            # map to tuple dat in map 
            tuple_data = (str(l["pid"]),str(l["port"]),l["process_name"],l["status"])
            table_data.append(tuple_data)
    return table_data
        

# def test_map_table_data():
#     conns = scan_ports()
#     table = map_table(conns)
#     print(table)

def check_for_conflict(port):
    common_dev_ports = [
        # --- System / SSH ---
        500,
        22,  # SSH
        2222,  # Alternative SSH
        # --- Web servers ---
        80,  # HTTP
        443,  # HTTPS
        3000,  # React / Next.js
        4200,  # Angular
        5173,  # Vite
        8000,  # Django / Uvicorn
        8080,  # Tomcat / Generic Dev
        8081,  # Alternative HTTP
        8888,  # Jupyter Notebook
        9000,  # SonarQube
        9090,  # Prometheus
        9091,  # Prometheus PushGateway
        9092,  # Apache Kafka
        9443,  # HTTPS Alt
        # --- Databases ---
        1433,  # MS SQL Server
        1521,  # Oracle DB
        27017,  # MongoDB
        3306,  # MySQL
        5432,  # PostgreSQL
        6379,  # Redis
        7000,  # Redis Cluster
        9200,  # Elasticsearch
        11211,  # Memcached
        # --- Messaging / Queues ---
        4222,  # NATS
        5672,  # RabbitMQ
        61616,  # ActiveMQ
        1883,  # MQTT
        61613,  # STOMP
    ]

    return int(port) in common_dev_ports


    
def scan_changes(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]):
    new_connections = [item for item in new_data if item not in old_data]
    if not new_connections:
        return []
    return new_connections
        
def test_scan_changes():
    old_data = [{"pid": 1234, "port": 3000, "process_name": "node", "status": "LISTEN"}]
    new_data = [{"pid": 1234, "port": 3000, "process_name": "node", "status": "LISTEN"}]
    print(len(scan_changes(old_data, new_data)) > 0)


from pathlib import Path
import yaml
def _get_port_config(config_file: str = ".portconfig") -> dict:
    """
    Load port configuration from YAML file.

    Args:
        config_file (str): Path to YAML config file (default: .portconfig)

    Returns:
        dict: Port configuration dictionary
    """
    ports = []
    config_path = Path(config_file)
    # port_config = None

    if not config_path.exists():
        # return empty dict instead of crashing
        return {}

    with config_path.open("r", encoding="utf-8") as f:
        port_config = yaml.safe_load(f) or {}
        
    for port_str,app in port_config.items():
        try:
            port = int(port_str)
        except ValueError:
            continue
        ports.append(port)
        

    return ports


def check_for_conflict(port):
    common_dev_ports = _get_port_config()
    return int(port) in common_dev_ports


if __name__ == "__main__":
    print(check_for_conflict(500))
