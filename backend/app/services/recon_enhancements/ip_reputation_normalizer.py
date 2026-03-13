def normalize_ip_reputation(raw: dict):
    if not raw:
        return {}
        
    ipqs = raw.get("ipqualityscore", {})
    iphub = raw.get("iphub", {})
    
    # Handle error responses in raw data
    if "error" in ipqs:
        ipqs = {}
    if "error" in iphub:
        iphub = {}

    return {
        "vpn": ipqs.get("vpn"),
        "proxy": ipqs.get("proxy"),
        "tor": ipqs.get("tor"),
        "fraud_score": ipqs.get("fraud_score"),
        "hosting": iphub.get("block") == 1,
        "asn": iphub.get("asn"),
        "isp": iphub.get("isp")
    }
