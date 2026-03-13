import requests

WAYBACK_URL = "https://archive.org/wayback/available"


def fetch_wayback_data(target: str) -> dict:
    try:
        response = requests.get(
            WAYBACK_URL,
            params={"url": target},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "error": "Wayback API error",
            "details": str(e),
        }
