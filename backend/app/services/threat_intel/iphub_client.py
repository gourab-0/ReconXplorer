import requests
from app.config import settings

def fetch_iphub(ip: str):
    """
    Checks if an IP is a proxy, VPN, or hosting provider.
    """
    if not settings.IPHUB_API_KEY:
        return {"error": "IPHub API key not configured"}

    url = f"http://v2.api.iphub.info/ip/{ip}"
    headers = {
        "X-Key": settings.IPHUB_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {
                "error": "IPHub API error",
                "status_code": response.status_code,
            }

        data = response.json()

        # Block levels: 0 = residential, 1 = hosting/VPN/proxy
        return {
            "provider": "iphub",
            "country": data.get("countryName"),
            "isp": data.get("isp"),
            "block": data.get("block"),
            "asn": data.get("asn"),
        }
    except Exception as e:
        return {"error": str(e)}
