import requests
from typing import Dict

URLHAUS_API = "https://urlhaus-api.abuse.ch/v1/host/"


def fetch_urlhaus_report(host: str) -> Dict:
    """
    Fetch URLhaus malware hosting information.
    """
    try:
        response = requests.post(
            URLHAUS_API,
            data={"host": host},
            timeout=15
        )
    except requests.RequestException as e:
        return {
            "provider": "urlhaus",
            "error": str(e)
        }

    if response.status_code != 200:
        return {
            "provider": "urlhaus",
            "error": "URLhaus API error",
            "status_code": response.status_code
        }

    data = response.json()

    return {
        "provider": "urlhaus",
        "query_status": data.get("query_status"),
        "urls": data.get("urls", [])
    }
