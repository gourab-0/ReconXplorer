import requests
from app.config import settings

BASE_URL = "https://ipqualityscore.com/api/json"

def fetch_ipqualityscore(target: str) -> dict:
    """
    Checks IP or domain reputation.
    """
    url = f"{BASE_URL}/ip/{settings.IPQUALITYSCORE_API_KEY}/{target}"

    params = {
        "strictness": 1,
        "allow_public_access_points": True,
        "lighter_penalties": False,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {
                "provider": "ipqualityscore",
                "error": "API error",
                "status_code": response.status_code,
            }

        data = response.json()
        return {
            "provider": "ipqualityscore",
            "success": data.get("success"),
            "risk_score": data.get("risk_score", 0),
            "is_proxy": data.get("proxy"),
            "is_vpn": data.get("vpn"),
            "is_tor": data.get("tor"),
            "is_crawler": data.get("is_crawler"),
            "fraud_score": data.get("fraud_score", 0),
            "country": data.get("country_code"),
            "asn": data.get("ASN"),
            "organization": data.get("organization"),
            "raw": data,
        }

    except Exception as e:
        return {
            "provider": "ipqualityscore",
            "error": str(e),
        }
