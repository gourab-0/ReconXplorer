import requests
from app.config import settings

GSB_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

def fetch_google_safe_browsing(target: str) -> dict:
    payload = {
        "client": {
            "clientId": "ReconXplorer",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": f"http://{target}"},
                {"url": f"https://{target}"}
            ]
        }
    }

    try:
        response = requests.post(
            f"{GSB_URL}?key={settings.GOOGLE_SAFE_BROWSING_API_KEY}",
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "provider": "google_safe_browsing",
                "error": "API error",
                "status_code": response.status_code,
            }

        data = response.json()
        return {
            "provider": "google_safe_browsing",
            "matches": data.get("matches", []),
            "hit": bool(data.get("matches")),
            "raw": data,
        }

    except Exception as e:
        return {
            "provider": "google_safe_browsing",
            "error": str(e),
        }
