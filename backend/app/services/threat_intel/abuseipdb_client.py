import requests
from typing import Dict

from app.config import settings

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


def fetch_abuseipdb_report(ip: str) -> Dict:
    """
    Fetch AbuseIPDB reputation for an IP address.
    """
    headers = {
        "Key": settings.ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90,
        "verbose": ""
    }

    try:
        response = requests.get(
            ABUSEIPDB_URL,
            headers=headers,
            params=params,
            timeout=15
        )
    except requests.RequestException as e:
        return {
            "provider": "abuseipdb",
            "error": str(e)
        }

    if response.status_code != 200:
        return {
            "provider": "abuseipdb",
            "error": "AbuseIPDB API error",
            "status_code": response.status_code
        }

    data = response.json().get("data", {})

    return {
        "provider": "abuseipdb",
        "abuseConfidenceScore": data.get("abuseConfidenceScore"),
        "countryCode": data.get("countryCode"),
        "usageType": data.get("usageType"),
        "isp": data.get("isp"),
        "domain": data.get("domain"),
        "totalReports": data.get("totalReports"),
        "lastReportedAt": data.get("lastReportedAt")
    }
