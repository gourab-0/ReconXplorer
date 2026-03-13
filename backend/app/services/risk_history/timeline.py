def build_risk_timeline(scans):
    # Filters scans with a risk_score and sorts by finish time
    return [
        {
            "scan_id": scan.id,
            "timestamp": scan.finished_at,
            "risk_score": scan.risk_score,
            "risk_level": scan.risk_level
        }
        for scan in sorted(scans, key=lambda s: s.finished_at if s.finished_at else s.created_at)
        if scan.risk_score is not None
    ]
