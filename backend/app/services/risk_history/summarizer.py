from .timeline import build_risk_timeline
from .delta import calculate_delta
from .trend import classify_trend

def summarize_history(scans):
    timeline = build_risk_timeline(scans)
    delta = calculate_delta(timeline)
    trend = classify_trend(delta)

    return {
        "timeline": timeline[-10:],  # cap history to last 10 scans
        "delta": delta or {"previous": 0, "current": 0, "delta": 0},
        "trend": trend,
        "confidence": "high" if len(timeline) >= 3 else "medium"
    }
