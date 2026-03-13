from datetime import datetime

def normalize_ssl(cert: dict):
    if not cert:
        return {"error": "No certificate data found"}

    try:
        # Safely get fields
        not_after = cert.get("notAfter")
        expired = False
        if not_after:
            try:
                # Format: "May 26 23:59:59 2024 GMT"
                expiry_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                expired = datetime.utcnow() > expiry_dt
            except ValueError:
                expired = None # Could not parse date

        return {
            "issuer": cert.get("issuer"),
            "subject": cert.get("subject"),
            "valid_from": cert.get("notBefore"),
            "valid_to": not_after,
            "san": cert.get("subjectAltName", []),
            "expired": expired
        }
    except Exception as e:
        return {"error": f"Normalization error: {str(e)}"}
