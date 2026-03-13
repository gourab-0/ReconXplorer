from typing import Dict, Optional
from datetime import datetime


def normalize_threat_intel(
    target: str,
    resolved_ip: Optional[str],
    vt_data: Optional[Dict],
    abuse_data: Optional[Dict],
    urlhaus_data: Optional[Dict],
    ipqs_data: Optional[Dict],
    gsb_data: Optional[Dict],
    iphub_data: Optional[Dict],
) -> Dict:
    risk_score = 0
    signals = {}
    tags = []

    # --------------------
    # IPHub Scoring (Proxy/Hosting)
    # --------------------
    if iphub_data and "block" in iphub_data:
        block_level = iphub_data.get("block")
        signals["iphub_block_level"] = block_level
        if block_level == 1:
            tags.append("hosting-or-proxy")
        elif block_level == 2:
            tags.append("vpn-or-tor")
            risk_score += 10

    # --------------------
    # VirusTotal Scoring
    # --------------------
    # Adapter: VT client returns data nested under 'stats'
    vt_detections = 0
    vt_stats = vt_data.get("stats", {}) if vt_data else {}
    
    if "malicious" in vt_stats:
        vt_detections = vt_stats.get("malicious", 0)
        signals["virustotal_detections"] = vt_detections

        if vt_detections >= 10:
            risk_score += 50
            tags.append("high-vt-detections")
        elif vt_detections >= 5:
            risk_score += 30
            tags.append("medium-vt-detections")
        elif vt_detections > 0:
            risk_score += 15
            tags.append("low-vt-detections") # matches user's new logic: "vt-detections"

    # --------------------
    # AbuseIPDB Scoring
    # --------------------
    # Adapter: AbuseIPDB client returns camelCase 'abuseConfidenceScore'
    abuse_score = 0
    if abuse_data and "abuseConfidenceScore" in abuse_data:
        abuse_score = abuse_data.get("abuseConfidenceScore", 0)
        signals["abuseipdb_score"] = abuse_score

        if abuse_score >= 80:
            risk_score += 40
            tags.append("high-abuse-score")
        elif abuse_score >= 50:
            risk_score += 25
            tags.append("medium-abuse-score")
        elif abuse_score >= 20:
            risk_score += 10
            tags.append("low-abuse-score")

    # --------------------
    # URLhaus Scoring
    # --------------------
    # Adapter: Check query_status and presence of urls
    if urlhaus_data and urlhaus_data.get("query_status") == "ok" and urlhaus_data.get("urls"):
        signals["urlhaus_malware"] = True
        risk_score += 40
        tags.append("malware-hosting")

    # --------------------
    # IPQualityScore Scoring
    # --------------------
    ipqs_score = ipqs_data.get("risk_score", 0) if ipqs_data else 0
    signals["ipqs_risk_score"] = ipqs_score
    if ipqs_score >= 75:
        risk_score += 30
        tags.append("high-ip-risk")
    elif ipqs_score >= 50:
        risk_score += 15
        tags.append("medium-ip-risk")

    # --------------------
    # Google Safe Browsing Scoring
    # --------------------
    if gsb_data and gsb_data.get("hit"):
        signals["gsb_hit"] = True
        risk_score += 40
        tags.append("gsb-hit")

    # --------------------
    # Clamp Score
    # --------------------
    risk_score = min(risk_score, 100)

    # --------------------
    # Verdict Logic (Balanced)
    # --------------------
    if risk_score >= 60:
        verdict = "malicious"
        confidence = "high"
    elif risk_score >= 30:
        verdict = "suspicious"
        confidence = "medium"
    else:
        verdict = "clean"
        confidence = "low"

    return {
        "target": target,
        "resolved_ip": resolved_ip,
        "risk_score": risk_score,
        "verdict": verdict,
        "confidence": confidence,
        "signals": signals,
        "tags": tags,
        "sources": {
            "virustotal": vt_data,
            "abuseipdb": abuse_data,
            "urlhaus": urlhaus_data,
            "ipqualityscore": ipqs_data,
            "google_safe_browsing": gsb_data,
            "iphub": iphub_data,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }