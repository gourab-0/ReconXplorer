import requests
from typing import Dict

from app.config import settings

VT_BASE_URL = "https://www.virustotal.com/api/v3"


def fetch_virustotal_report(target: str) -> Dict:
    """
    Fetch VirusTotal analysis for a domain or IP.
    Returns raw but structured data.
    """
    headers = {
        "x-apikey": settings.VIRUSTOTAL_API_KEY
    }

    # VT uses different endpoints for IPs vs domains
    if target.replace(".", "").isdigit():
        url = f"{VT_BASE_URL}/ip_addresses/{target}"
    else:
        url = f"{VT_BASE_URL}/domains/{target}"

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as e:
        return {
            "provider": "virustotal",
            "error": str(e)
        }

    if response.status_code != 200:
        return {
            "provider": "virustotal",
            "error": "VirusTotal API error",
            "status_code": response.status_code
        }

    data = response.json()

    attributes = data.get("data", {}).get("attributes", {})
    stats = attributes.get("last_analysis_stats", {})
    results = attributes.get("last_analysis_results", {})

    return {
        "provider": "virustotal",
        "stats": stats,
        "results": results
    }
