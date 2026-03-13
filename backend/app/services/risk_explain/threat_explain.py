def explain_threat(threat_summary):
    reasons = []
    if not threat_summary:
        return {"layer": "threat", "score": 0, "reasons": []}

    risk_score = threat_summary.get("risk_score", 0)
    if risk_score >= 60:
        reasons.append("Threat intelligence indicates malicious activity")

    signals = threat_summary.get("signals", {})
    if signals.get("virustotal_detections", 0) > 0:
        reasons.append("VirusTotal flagged malicious indicators")

    if signals.get("abuseipdb_score", 0) > 25:
        reasons.append("IP reported for abusive behavior")

    return {
        "layer": "threat",
        "score": risk_score,
        "reasons": reasons
    }
