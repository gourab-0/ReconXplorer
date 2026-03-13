from typing import Dict
import socket
from sqlalchemy.orm import Session
from uuid import UUID
from concurrent.futures import ThreadPoolExecutor

from app.services.passive_recon.shodan_client import fetch_shodan_data
from app.services.passive_recon.securitytrails_client import fetch_securitytrails
from app.services.passive_recon.ipinfo_client import fetch_ipinfo
from app.services.passive_recon.normalizer import normalize_passive_recon
from app.models.passive_recon import PassiveReconResult
from app.services.api_quota_manager import APICacheManager, APIQuotaManager, CACHE_TTL

def save_passive_recon(db: Session, user_id: UUID, normalized: Dict):
    record = PassiveReconResult(
        user_id=user_id,
        target=normalized["target"],
        resolved_ip=normalized["resolved_ip"],
        summary=normalized["summary"],
        sources=normalized["sources"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def run_passive_recon(target: str, db: Session = None, user_id: UUID = None) -> Dict:
    """
    Runs all passive recon modules on a target.
    Optionally saves to DB if db and user_id are provided.
    """
    # 🧩 Cache & Quota Setup
    cache = APICacheManager(db) if db else None
    quota = APIQuotaManager(db) if db else None

    # Resolve IP safely for tools that prefer/require it
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        ip = None

    # --- MODULE 1: SHODAN ---
    shodan_result = None
    if cache: shodan_result = cache.get(ip if ip else target, "shodan")
    
    if not shodan_result:
        if not quota or quota.can_call("shodan"):
            shodan_result = fetch_shodan_data(ip if ip else target)
            if shodan_result and "error" not in shodan_result and cache:
                quota.record_call("shodan")
                cache.set(ip if ip else target, "shodan", shodan_result, CACHE_TTL["shodan"])
        else:
            shodan_result = {"error": "Quota exceeded"}

    # --- MODULE 2: SECURITYTRAILS ---
    securitytrails_result = None
    if cache: securitytrails_result = cache.get(target, "securitytrails")
    
    if not securitytrails_result:
        if not quota or quota.can_call("securitytrails"):
            securitytrails_result = fetch_securitytrails(target)
            if securitytrails_result and "error" not in securitytrails_result and cache:
                quota.record_call("securitytrails")
                cache.set(target, "securitytrails", securitytrails_result, CACHE_TTL["securitytrails"])
        else:
            securitytrails_result = {"error": "Quota exceeded"}

    # --- MODULE 3: IPINFO ---
    ipinfo_result = None
    if ip:
        if cache: ipinfo_result = cache.get(ip, "ipinfo")
        if not ipinfo_result:
            if not quota or quota.can_call("ipinfo"):
                ipinfo_result = fetch_ipinfo(ip)
                if ipinfo_result and "error" not in ipinfo_result and cache:
                    quota.record_call("ipinfo")
                    cache.set(ip, "ipinfo", ipinfo_result, CACHE_TTL["ipinfo"])
            else:
                ipinfo_result = {"error": "Quota exceeded"}
    else:
        ipinfo_result = {"error": "IP resolution failed"}

    # 🧩 Normalize Results
    normalized = normalize_passive_recon(
        target=target,
        resolved_ip=ip if ip else "0.0.0.0",
        shodan_data=shodan_result,
        securitytrails_data=securitytrails_result,
        ipinfo_data=ipinfo_result
    )

    # 💾 Save to DB if context provided
    if db and user_id:
        save_passive_recon(db, user_id, normalized)

    return normalized
