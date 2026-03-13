import requests
from app.config import settings

BASE_URL = "https://api.api-ninjas.com/v1/whois"

def fetch_whois(domain: str):
    headers = {
        "X-Api-Key": settings.API_NINJAS_WHOIS_KEY
    }

    try:
        resp = requests.get(
            BASE_URL,
            headers=headers,
            params={"domain": domain},
            timeout=10
        )

        if resp.status_code != 200:
            return {
                "provider": "whois",
                "error": resp.text,
                "status_code": resp.status_code,
                "raw": {}
            }

        return {
            "provider": "whois",
            "raw": resp.json()
        }
    except Exception as e:
        return {
            "provider": "whois",
            "error": str(e),
            "raw": {}
        }
