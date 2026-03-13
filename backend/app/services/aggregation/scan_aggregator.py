import json
from datetime import datetime

def aggregate_scan_results(results):
    open_ports = set()
    services = []
    technologies = []
    tools_executed = []

    for result in results:
        tools_executed.append(result.tool)

        parsed = result.parsed_result

        # --- HARD TYPE NORMALIZATION ---
        if isinstance(parsed, str):
            try:
                parsed = json.loads(parsed)
            except Exception:
                continue

        if not isinstance(parsed, dict):
            continue

        # --- NMAP ---
        if result.tool == "nmap":
            for port in parsed.get("open_ports", []):
                if isinstance(port, dict):
                    open_ports.add(port.get("port"))
                elif isinstance(port, int):
                    open_ports.add(port)

            services.extend(parsed.get("services", []))

        # --- WHATWEB ---
        if result.tool == "whatweb":
            technologies.extend(parsed.get("technologies", []))

    return {
        "tools_executed": tools_executed,
        "summary": {
            "open_ports": sorted(list(open_ports)),
            "services": services,
            "technologies": technologies,
            "findings_count": len(open_ports),
            "severity": "info" if not open_ports else "medium"
        },
        "tool_breakdown": {},
        "generated_at": datetime.utcnow().isoformat()
    }
