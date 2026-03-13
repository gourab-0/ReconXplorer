def compose_explanation(recon, threat, active):
    all_reasons = list(set(
        recon["reasons"]
        + threat["reasons"]
        + active["reasons"]
    ))

    return {
        "overall_reasoning": all_reasons,
        "by_layer": {
            "recon": recon,
            "threat": threat,
            "active": active
        }
    }
