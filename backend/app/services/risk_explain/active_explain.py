def explain_active(active_results):
    reasons = []
    if not active_results:
        return {"layer": "active", "score": 0, "reasons": []}

    # Based on what scan_aggregator produces
    open_ports = active_results.get("open_ports", [])
    if len(open_ports) >= 5:
        reasons.append("Multiple open services exposed")

    if active_results.get("severity") in ["high", "critical"]:
        reasons.append("Active scan detected high-risk exposure")

    return {
        "layer": "active",
        "score": 30 if reasons else 0, # Simplified score for explanation context
        "reasons": reasons
    }
