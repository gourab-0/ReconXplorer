import requests

DNS_URL = "https://dns.google/resolve"
TIMEOUT = 10

RECORD_TYPES = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]

def fetch_dns(domain: str):
    results = {}

    for rtype in RECORD_TYPES:
        try:
            response = requests.get(
                DNS_URL,
                params={"name": domain, "type": rtype},
                timeout=TIMEOUT
            )
            # Google DNS API returns 200 even for NXDOMAIN, but we check for valid JSON
            if response.status_code == 200:
                results[rtype] = response.json()
            else:
                results[rtype] = {"error": f"Status {response.status_code}"}
        except Exception as e:
            results[rtype] = {"error": str(e)}

    return {
        "provider": "google_dns",
        "raw": results
    }
