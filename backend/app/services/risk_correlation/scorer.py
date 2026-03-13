def score_recon(recon_enhancements: dict) -> int:
    score = 0
    if not recon_enhancements:
        return 0

    whois = recon_enhancements.get("whois", {})
    if whois and whois.get("domain_age_days", 9999) < 30:
        score += 10
    if whois and whois.get("domain_age_days", 9999) < 7:
        score += 15

    ip_rep = recon_enhancements.get("ip_reputation", {})
    if ip_rep:
        if ip_rep.get("hosting"):
            score += 5
        if ip_rep.get("vpn") or ip_rep.get("proxy") or ip_rep.get("tor"):
            score += 10

    return min(score, 25)


def score_threat(threat_summary: dict) -> int:
    score = 0
    if not threat_summary:
        return 0

    vt = threat_summary.get("signals", {}).get("virustotal_detections", 0)
    score += min(vt * 10, 30)

    abuse = threat_summary.get("signals", {}).get("abuseipdb_score", 0)
    if abuse > 50:
        score += 20
    elif abuse > 20:
        score += 10

    if threat_summary.get("verdict") == "malicious":
        score += 10

    return min(score, 50)


def score_active(active_summary: dict) -> int:
    score = 0
    if not active_summary:
        return 0

    # Handle scan summary structure
    summary = active_summary.get("summary", {}) if "summary" in active_summary else active_summary
    
    findings = summary.get("findings_count", 0)
    score += min(findings * 3, 10)

    severity = summary.get("severity", "info")
    if severity == "high":
        score += 15
    elif severity == "medium":
        score += 10
    elif severity == "low":
        score += 5

    return min(score, 25)
