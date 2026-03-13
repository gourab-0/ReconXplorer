import requests
from app.config import settings

def fetch_ip_reputation(ip: str):
    results = {}

    # IPQualityScore
    try:
        if settings.IPQUALITYSCORE_API_KEY:
            ipqs_url = f"https://ipqualityscore.com/api/json/ip/{settings.IPQUALITYSCORE_API_KEY}/{ip}"
            ipqs_resp = requests.get(ipqs_url, timeout=10)
            if ipqs_resp.status_code == 200:
                results["ipqualityscore"] = ipqs_resp.json()
            else:
                 results["ipqualityscore"] = {"error": f"Status {ipqs_resp.status_code}"}
        else:
            results["ipqualityscore"] = {"error": "No API Key"}
    except Exception as e:
        results["ipqualityscore"] = {"error": str(e)}

    # IPHub
    try:
        if settings.IPHUB_API_KEY:
            iphub_resp = requests.get(
                f"https://v2.api.iphub.info/ip/{ip}",
                headers={"X-Key": settings.IPHUB_API_KEY},
                timeout=10
            )
            if iphub_resp.status_code == 200:
                results["iphub"] = iphub_resp.json()
            else:
                results["iphub"] = {"error": f"Status {iphub_resp.status_code}"}
        else:
             results["iphub"] = {"error": "No API Key"}
    except Exception as e:
        results["iphub"] = {"error": str(e)}

    return {
        "provider": "ip_reputation",
        "raw": results
    }
