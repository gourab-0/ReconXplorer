import xml.etree.ElementTree as ET
from typing import Dict, List


def parse_nmap_xml(xml_output: str) -> Dict:
    """
    Parse Nmap XML output into structured JSON.
    """
    if not xml_output or not xml_output.strip():
        return {
            "open_ports": [],
            "services": [],
            "findings_count": 0,
            "severity": "low",
        }

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError:
         return {
            "open_ports": [],
            "services": [],
            "findings_count": 0,
            "severity": "low",
        }

    open_ports: List[Dict] = []
    services: List[Dict] = []
    resolved_ip = None

    for host in root.findall("host"):
        # Extract IP
        addr_elem = host.find("address")
        if addr_elem is not None:
            resolved_ip = addr_elem.attrib.get("addr")

        ports = host.find("ports")
        if ports is None:
            continue

        for port in ports.findall("port"):
            port_id = port.attrib.get("portid")
            if port_id:
                port_id = int(port_id)
            else:
                continue
                
            state_elem = port.find("state")
            state = state_elem.attrib.get("state") if state_elem is not None else "unknown"

            service_elem = port.find("service")
            service_name = service_elem.attrib.get("name") if service_elem is not None else None
            product = service_elem.attrib.get("product") if service_elem is not None else None
            version = service_elem.attrib.get("version") if service_elem is not None else None

            if state == "open":
                open_ports.append({"port": port_id})

                services.append({
                    "port": port_id,
                    "service": service_name,
                    "product": product,
                    "version": version,
                })

    findings_count = len(open_ports)

    # 🔥 Severity logic (simple, extendable)
    if findings_count == 0:
        severity = "low"
    elif findings_count <= 3:
        severity = "medium"
    else:
        severity = "high"

    return {
        "resolved_ip": resolved_ip,
        "open_ports": open_ports,
        "services": services,
        "findings_count": findings_count,
        "severity": severity,
    }
