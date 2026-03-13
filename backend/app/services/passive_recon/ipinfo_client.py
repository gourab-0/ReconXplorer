import requests
from app.config import settings

def fetch_ipinfo(ip: str):
    if not settings.IPINFO_API_KEY:
        return {"error": "IPInfo API key not configured"}

    url = f"https://ipinfo.io/{ip}"
    params = {
        "token": settings.IPINFO_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": "IPInfo API error",
                "status_code": response.status_code,
            }

        data = response.json()

        return {
            "provider": "ipinfo",
            "ip": data.get("ip"),
            "hostname": data.get("hostname"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "org": data.get("org"),
            "loc": data.get("loc"),
        }
    except Exception as e:
        return {"error": str(e)}
