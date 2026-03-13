def calculate_delta(timeline):
    if len(timeline) < 2:
        return None

    previous = timeline[-2]["risk_score"]
    current = timeline[-1]["risk_score"]

    return {
        "previous": previous,
        "current": current,
        "delta": current - previous
    }
