import requests
from typing import Dict
from app.config import settings

SHODAN_API_KEY = settings.SHODAN_API_KEY
SHODAN_BASE_URL = "https://api.shodan.io/shodan/host"

def fetch_shodan_data(target: str) -> Dict:
    """
    Fetch passive reconnaissance data from Shodan.
    Target should be an IP or domain (Shodan resolves domains).
    """

    if not SHODAN_API_KEY:
        return {"error": "Shodan API key not configured"}

    params = {
        "key": SHODAN_API_KEY,
    }

    try:
        response = requests.get(f"{SHODAN_BASE_URL}/{target}", params=params, timeout=10)

        if response.status_code == 404:
            return {"info": "No Shodan data found"}

        if response.status_code != 200:
            return {
                "error": "Shodan API error",
                "status_code": response.status_code,
            }

        data = response.json()

        # 🔎 Normalize useful fields
        normalized = {
            "ip": data.get("ip_str"),
            "org": data.get("org"),
            "isp": data.get("isp"),
            "country": data.get("country_name"),
            "os": data.get("os"),
            "ports": data.get("ports", []),
            "hostnames": data.get("hostnames", []),
            "services": [],
            "vulnerabilities": data.get("vulns", []),
        }

        for item in data.get("data", []):
            normalized["services"].append({
                "port": item.get("port"),
                "transport": item.get("transport"),
                "product": item.get("product"),
                "version": item.get("version"),
                "banner": item.get("banner"),
            })

        return normalized

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
