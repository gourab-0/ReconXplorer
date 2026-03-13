import requests
from app.config import settings

BASE_URL = "https://api.securitytrails.com/v1"

def fetch_securitytrails(domain: str):
    if not settings.SECURITYTRAILS_API_KEY:
        return {"error": "SecurityTrails API key not configured"}

    headers = {
        "APIKEY": settings.SECURITYTRAILS_API_KEY,
        "Accept": "application/json",
    }

    results = {
        "provider": "securitytrails",
        "subdomains": [],
        "dns": {},
        "whois": {}
    }

    try:
        # 1. Subdomains
        sub_url = f"{BASE_URL}/domain/{domain}/subdomains"
        sub_res = requests.get(sub_url, headers=headers, timeout=10)
        if sub_res.status_code == 200:
            sub_data = sub_res.json()
            results["subdomains"] = [f"{s}.{domain}" for s in sub_data.get("subdomains", [])[:50]]
            results["subdomain_count"] = len(sub_data.get("subdomains", []))

        # 2. DNS Records
        dns_url = f"{BASE_URL}/domain/{domain}"
        dns_res = requests.get(dns_url, headers=headers, timeout=10)
        if dns_res.status_code == 200:
            results["dns"] = dns_res.json()

        # 3. WHOIS (Simplified for basic data)
        whois_url = f"{BASE_URL}/domain/{domain}/whois"
        whois_res = requests.get(whois_url, headers=headers, timeout=10)
        if whois_res.status_code == 200:
            results["whois"] = whois_res.json()

        return results
    except Exception as e:
        return {"error": str(e)}
