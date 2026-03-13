from sqlalchemy.orm import Session
from uuid import UUID

from app.models.recon_enhancement import ReconEnhancementResult
from app.services.recon_enhancements.wayback_client import fetch_wayback_data
from app.services.recon_enhancements.wayback_normalizer import normalize_wayback
from app.services.recon_enhancements.dns_client import fetch_dns
from app.services.recon_enhancements.dns_normalizer import normalize_dns
from app.services.recon_enhancements.ssl_client import fetch_ssl_cert
from app.services.recon_enhancements.ssl_normalizer import normalize_ssl
from app.services.recon_enhancements.harvester_client import run_harvester
from app.services.recon_enhancements.harvester_normalizer import normalize_harvester
from app.services.recon_enhancements.whois_client import fetch_whois
from app.services.recon_enhancements.whois_normalizer import normalize_whois
from app.services.recon_enhancements.ip_reputation_client import fetch_ip_reputation
from app.services.recon_enhancements.ip_reputation_normalizer import normalize_ip_reputation
from app.utils.network import resolve_ip


def run_wayback_recon(
    target: str,
    db: Session,
    user_id: UUID,
):
    raw = fetch_wayback_data(target)
    normalized = normalize_wayback(target, raw)

    record = ReconEnhancementResult(
        user_id=user_id,
        target=target,
        module="wayback",
        summary=normalized["summary"],
        sources=normalized["sources"],
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return normalized


def run_recon_enhancements(target: str, db: Session, user_id: UUID):
    results = []

    # DNS
    dns_raw = fetch_dns(target)
    dns_summary = normalize_dns(dns_raw["raw"])
    results.append(("dns", dns_summary, dns_raw))

    # SSL
    ssl_raw = fetch_ssl_cert(target)
    ssl_summary = normalize_ssl(ssl_raw["raw"])
    results.append(("ssl", ssl_summary, ssl_raw))

    # Harvester
    harv_raw = run_harvester(target)
    harv_summary = normalize_harvester(harv_raw["raw"])
    results.append(("harvester", harv_summary, harv_raw))

    # WHOIS
    whois_raw = fetch_whois(target)
    if "raw" in whois_raw:
        whois_summary = normalize_whois(whois_raw["raw"])
        results.append(("whois", whois_summary, whois_raw))

    # IP Reputation
    ip = resolve_ip(target)
    if ip:
        rep_raw = fetch_ip_reputation(ip)
        if "raw" in rep_raw:
             rep_summary = normalize_ip_reputation(rep_raw["raw"])
             results.append(("ip_reputation", rep_summary, rep_raw))

    for module, summary, source in results:
        record = ReconEnhancementResult(
            user_id=user_id,
            target=target,
            module=module,
            summary=summary,
            sources=source
        )
        db.add(record)

    db.commit()

    return {
        "target": target,
        "modules_executed": [r[0] for r in results],
        "results": {r[0]: r[1] for r in results}
    }
