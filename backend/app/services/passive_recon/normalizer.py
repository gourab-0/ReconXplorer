from datetime import datetime

def normalize_passive_recon(
    target: str,
    resolved_ip: str,
    shodan_data: dict | None,
    securitytrails_data: dict | None,
    ipinfo_data: dict | None,
):
    summary = {
        "resolved_ip": resolved_ip,
        "open_ports": [],
        "technologies": [],
        "subdomains_count": 0,
        "country": None,
        "city": None,
        "region": None,
        "location": None,
        "asn": None,
        "os": None,
        "services": [],
        "vulnerabilities": [],
        "dns": {},
        "whois": {}
    }

    # --- Shodan ---
    if shodan_data and "error" not in shodan_data:
        summary["open_ports"] = shodan_data.get("ports", [])
        summary["os"] = shodan_data.get("os")
        summary["vulnerabilities"] = shodan_data.get("vulnerabilities", [])
        summary["services"] = shodan_data.get("services", [])
        
        # Extract product names as technologies if available
        services = shodan_data.get("services", [])
        technologies = list(set([s.get("product") for s in services if s.get("product")]))
        summary["technologies"] = technologies

    # --- SecurityTrails ---
    if securitytrails_data and "error" not in securitytrails_data:
        summary["subdomains_count"] = securitytrails_data.get("subdomain_count", 0)
        summary["dns"] = securitytrails_data.get("dns", {})
        summary["whois"] = securitytrails_data.get("whois", {})

    # --- IPInfo ---
    if ipinfo_data and "error" not in ipinfo_data:
        summary["country"] = ipinfo_data.get("country")
        summary["city"] = ipinfo_data.get("city")
        summary["region"] = ipinfo_data.get("region")
        summary["location"] = ipinfo_data.get("loc")
        summary["asn"] = ipinfo_data.get("org")

    return {
        "target": target,
        "resolved_ip": resolved_ip,
        "timestamp": datetime.utcnow().isoformat(),
        "sources": {
            "shodan": shodan_data,
            "securitytrails": securitytrails_data,
            "ipinfo": ipinfo_data,
        },
        "summary": summary,
    }
