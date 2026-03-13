import re

def parse_nmap_output(output: str):
    ports = []

    # Example line:
    # 80/tcp open  http Apache httpd 2.4.41
    pattern = re.compile(
        r"(\d+)/tcp\s+open\s+(\S+)\s*(.*)"
    )

    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            port, service, version = match.groups()
            ports.append({
                "port": int(port),
                "protocol": "tcp",
                "service": service,
                "version": version.strip()
            })

    return {
        "summary": f"{len(ports)} open ports detected",
        "ports": ports
    }
