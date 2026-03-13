def explain_recon(recon_data):
    reasons = []
    if not recon_data:
        return {"layer": "recon", "score": 0, "reasons": []}

    if recon_data.get("ssl", {}).get("expired"):
        reasons.append("Expired SSL certificate detected")

    # The dns_normalizer uses 'mail_servers' key
    if recon_data.get("dns", {}).get("mail_servers"):
        reasons.append("Mail services exposed (MX records found)")

    if recon_data.get("harvester", {}).get("emails"):
        reasons.append("Email addresses exposed via OSINT")

    return {
        "layer": "recon",
        "score": 25 if reasons else 0, # Simplified score for explanation context
        "reasons": reasons
    }
