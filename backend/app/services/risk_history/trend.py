def classify_trend(delta):
    if delta is None:
        return "insufficient-data"

    change = delta["delta"]

    if change >= 15:
        return "rapid-increase"
    if change >= 5:
        return "increasing"
    if change <= -15:
        return "rapid-decrease"
    if change <= -5:
        return "decreasing"

    return "stable"
