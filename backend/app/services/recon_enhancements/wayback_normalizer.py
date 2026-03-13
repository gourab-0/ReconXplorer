from datetime import datetime


def normalize_wayback(target: str, raw: dict) -> dict:
    snapshots = raw.get("archived_snapshots", {})
    closest = snapshots.get("closest")

    summary = {
        "has_snapshot": bool(closest),
        "timestamp": closest.get("timestamp") if closest else None,
        "url": closest.get("url") if closest else None,
        "status": closest.get("status") if closest else None,
    }

    return {
        "target": target,
        "module": "wayback",
        "summary": summary,
        "sources": raw,
        "timestamp": datetime.utcnow().isoformat(),
    }
