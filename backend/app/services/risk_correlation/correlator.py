from .scorer import score_recon, score_threat, score_active
from .constants import RISK_LEVELS

def correlate(scan, recon_enhancements: dict):
    # recon_enhancements is expected to be a dict mapping module names to their summaries
    recon_score = score_recon(recon_enhancements)
    threat_score = score_threat(scan.threat_summary)
    active_score = score_active(scan.aggregated_result)

    total = recon_score + threat_score + active_score

    risk_level = "low"
    for level, (low, high) in RISK_LEVELS.items():
        if low <= total <= high:
            risk_level = level
            break
    
    # Ensure it doesn't exceed 100
    total = min(total, 100)

    # Calculate Confidence based on source density
    sources_hit = 0
    queried_apis = []
    
    # Passive Sources
    if scan.passive_summary and "sources" in scan.passive_summary:
        for src, data in scan.passive_summary["sources"].items():
            if data and "error" not in str(data):
                sources_hit += 1
                queried_apis.append(src)
    
    # Threat Sources
    if scan.threat_summary and "sources" in scan.threat_summary:
        for src, data in scan.threat_summary["sources"].items():
            if data and "error" not in str(data):
                sources_hit += 1
                queried_apis.append(src)

    confidence = "low"
    if sources_hit >= 5:
        confidence = "high"
    elif sources_hit >= 2:
        confidence = "medium"

    reasons = []
    if recon_score > 15:
        reasons.append("Suspicious infrastructure or new domain")
    if threat_score > 25:
        reasons.append("Threat intelligence indicates malicious activity")
    if active_score > 15:
        reasons.append("Multiple exposed services detected")
        
    if not reasons:
        if total > 0:
            reasons.append("General security findings detected")
        else:
            reasons.append("No significant risks identified")

    return {
        "overall_risk_score": total,
        "risk_level": risk_level,
        "confidence": confidence,
        "breakdown": {
            "recon": recon_score,
            "threat": threat_score,
            "active": active_score
        },
        "reasons": reasons,
        "queried_apis": queried_apis,
        "sources_count": sources_hit
    }
