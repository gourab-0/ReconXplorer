from typing import Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from app.services.threat_intel.virustotal_client import fetch_virustotal_report
from app.services.threat_intel.abuseipdb_client import fetch_abuseipdb_report
from app.services.threat_intel.urlhaus_client import fetch_urlhaus_report
from app.services.threat_intel.ipqualityscore_client import fetch_ipqualityscore
from app.services.threat_intel.gsb_client import fetch_google_safe_browsing
from app.services.threat_intel.iphub_client import fetch_iphub
from app.services.threat_intel.normalizer import normalize_threat_intel
from app.services.api_quota_manager import APICacheManager, APIQuotaManager, CACHE_TTL

from app.models.threat_intel import ThreatIntelResult


def save_threat_intel(
    db: Session,
    user_id: UUID,
    normalized: Dict
):
    record = ThreatIntelResult(
        user_id=user_id,
        target=normalized["target"],
        resolved_ip=normalized["resolved_ip"],
        risk_score=str(normalized["risk_score"]),
        verdict=normalized["verdict"],
        confidence=normalized["confidence"],
        signals=normalized["signals"],
        tags=normalized["tags"],
        sources=normalized["sources"],
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def resolve_ip(target: str) -> Optional[str]:
    try:
        return socket.gethostbyname(target)
    except Exception:
        return None

def run_threat_intel(
    target: str,
    db: Session = None,
    user_id: UUID = None
) -> Dict:
    """
    Runs threat intelligence checks and optionally stores results.
    """
    # 🧩 Cache & Quota Setup
    cache = APICacheManager(db) if db else None
    quota = APIQuotaManager(db) if db else None

    resolved_ip = resolve_ip(target)

    def get_module_data(api_name, func, lookup_val):
        if not lookup_val: return None
        res = None
        if cache: res = cache.get(lookup_val, api_name)
        if not res:
            if not quota or quota.can_call(api_name):
                res = func(lookup_val)
                if res and "error" not in res and cache:
                    quota.record_call(api_name)
                    cache.set(lookup_val, api_name, res, CACHE_TTL.get(api_name, 24))
            else:
                res = {"error": "Quota exceeded"}
        return res

    vt_data = get_module_data("virustotal", fetch_virustotal_report, target)
    abuse_data = get_module_data("abuseipdb", fetch_abuseipdb_report, resolved_ip)
    urlhaus_data = get_module_data("urlhaus", fetch_urlhaus_report, target)
    ipqs_data = get_module_data("ipqualityscore", fetch_ipqualityscore, resolved_ip or target)
    gsb_data = get_module_data("google_safe_browsing", fetch_google_safe_browsing, target)
    iphub_data = get_module_data("iphub", fetch_iphub, resolved_ip)

    normalized = normalize_threat_intel(
        target=target,
        resolved_ip=resolved_ip,
        vt_data=vt_data,
        abuse_data=abuse_data,
        urlhaus_data=urlhaus_data,
        ipqs_data=ipqs_data,
        gsb_data=gsb_data,
        iphub_data=iphub_data,
    )

    # 💾 Persist if context provided
    if db and user_id:
        save_threat_intel(db, user_id, normalized)

    return normalized
