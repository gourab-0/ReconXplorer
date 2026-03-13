from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.api_quota import APIQuota
from app.models.scan_cache import ScanCache

# Configuration for different APIs
API_LIMITS = {
    "shodan": {"daily": None, "monthly": 100, "minute": 1},
    "securitytrails": {"daily": None, "monthly": 50, "minute": 1},
    "api_ninjas": {"daily": None, "monthly": 50000, "minute": 30},
    "ipinfo": {"daily": None, "monthly": 50000, "minute": None},
    "virustotal": {"daily": 500, "monthly": 15000, "minute": 4},
    "abuseipdb": {"daily": 1000, "monthly": None, "minute": 1},
    "ipqualityscore": {"daily": None, "monthly": 5000, "minute": 2},
    "google_safe_browsing": {"daily": 10000, "monthly": None, "minute": None},
    "iphub": {"daily": 1000, "monthly": None, "minute": 1},
}

API_FALLBACKS = {
    "securitytrails": ["api_ninjas_dns"],
    "shodan": ["nmap"], # nmap is already a fallback in our tool logic
    "virustotal": ["abuseipdb", "ipqualityscore"],
    "ipqualityscore": ["iphub"],
    "ipinfo": ["api_ninjas"]
}

# Cache TTL in hours
CACHE_TTL = {
    "ipinfo": 720,        # 30 days
    "iphub": 720,         # 30 days
    "shodan": 168,        # 7 days
    "securitytrails": 168,# 7 days
    "virustotal": 72,     # 3 days
    "abuseipdb": 24,      # 1 day
    "ipqualityscore": 72, # 3 days
    "google_safe_browsing": 72, # 3 days
}

class APIQuotaManager:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_quota(self, api_name: str) -> APIQuota:
        try:
            # Use a sub-transaction (savepoint) for safety
            with self.db.begin_nested():
                quota = self.db.query(APIQuota).filter(APIQuota.api_name == api_name).first()
                if not quota:
                    limits = API_LIMITS.get(api_name, {"daily": None, "monthly": None, "minute": None})
                    quota = APIQuota(
                        api_name=api_name,
                        daily_limit=limits["daily"],
                        monthly_limit=limits["monthly"],
                        per_minute_limit=limits["minute"]
                    )
                    self.db.add(quota)
            # Commit the outer transaction or let the caller handle it
            self.db.commit()
            return quota
        except Exception as e:
            # If we are already in a failed transaction, commit() might fail
            try:
                self.db.rollback()
            except:
                pass
            print(f"[QUOTA_DB_ERROR] {e}")
            return APIQuota(api_name=api_name, daily_used=0, monthly_used=0, minute_used=0)

    def _reset_if_needed(self, quota: APIQuota):
        if not quota or not quota.last_daily_reset: return
        
        try:
            now = datetime.now(timezone.utc)
            last_daily = quota.last_daily_reset.replace(tzinfo=timezone.utc) if quota.last_daily_reset.tzinfo is None else quota.last_daily_reset
            last_monthly = quota.last_monthly_reset.replace(tzinfo=timezone.utc) if quota.last_monthly_reset.tzinfo is None else quota.last_monthly_reset
            last_minute = quota.last_minute_reset.replace(tzinfo=timezone.utc) if quota.last_minute_reset.tzinfo is None else quota.last_minute_reset

            changed = False
            if now.date() != last_daily.date():
                quota.daily_used = 0
                quota.last_daily_reset = now
                changed = True

            if now.month != last_monthly.month or now.year != last_monthly.year:
                quota.monthly_used = 0
                quota.last_monthly_reset = now
                changed = True

            if now - last_minute > timedelta(minutes=1):
                quota.minute_used = 0
                quota.last_minute_reset = now
                changed = True
            
            if changed:
                self.db.flush() # Just prepare changes, don't force commit
        except Exception as e:
            print(f"[QUOTA_RESET_ERROR] {e}")

    def can_call(self, api_name: str) -> bool:
        try:
            # We don't want quota checks to ever crash the scan
            quota = self.db.query(APIQuota).filter(APIQuota.api_name == api_name).first()
            if not quota:
                quota = self._get_or_create_quota(api_name)
            
            self._reset_if_needed(quota)

            if quota.daily_limit is not None and quota.daily_used >= quota.daily_limit:
                return False
            if quota.monthly_limit is not None and quota.monthly_used >= quota.monthly_limit:
                return False
            if quota.per_minute_limit is not None and quota.minute_used >= quota.per_minute_limit:
                return False

            return True
        except Exception as e:
            print(f"[QUOTA_CHECK_ERROR] {e}")
            return True 

    def record_call(self, api_name: str):
        try:
            quota = self.db.query(APIQuota).filter(APIQuota.api_name == api_name).first()
            if quota:
                quota.daily_used += 1
                quota.monthly_used += 1
                quota.minute_used += 1
                self.db.flush()
        except Exception as e:
            print(f"[QUOTA_RECORD_ERROR] {e}")

class APICacheManager:
    def __init__(self, db: Session):
        self.db = db

    def get(self, target: str, api_name: str):
        try:
            now = datetime.now(timezone.utc)
            # Use no_bolt to avoid transaction issues during simple lookups
            entry = self.db.query(ScanCache).filter(
                ScanCache.target == target,
                ScanCache.api_name == api_name
            ).first()

            if entry:
                expires_at = entry.expires_at.replace(tzinfo=timezone.utc) if entry.expires_at.tzinfo is None else entry.expires_at
                if expires_at > now:
                    return entry.data
            return None
        except Exception as e:
            print(f"[CACHE_GET_ERROR] {e}")
            return None

    def set(self, target: str, api_name: str, data: dict, ttl_hours: int = 24):
        try:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(hours=ttl_hours)
            
            entry = self.db.query(ScanCache).filter(
                ScanCache.target == target,
                ScanCache.api_name == api_name
            ).first()

            if entry:
                entry.data = data
                entry.expires_at = expires
                entry.cached_at = now
            else:
                entry = ScanCache(
                    target=target,
                    api_name=api_name,
                    data=data,
                    expires_at=expires
                )
                self.db.add(entry)
            
            self.db.flush()
        except Exception as e:
            print(f"[CACHE_SET_ERROR] {e}")

def unified_api_call(db: Session, api_name: str, func, target: str, *args, **kwargs):
    """
    Handles Caching, Quota Check, Execution, and Fallback.
    """
    cache = APICacheManager(db)
    quota = APIQuotaManager(db)

    # 1. Cache Check
    cached_data = cache.get(target, api_name)
    if cached_data:
        print(f"[CACHE] Hit for {api_name} on {target}")
        return cached_data

    # 2. Quota Check + Primary Execution
    if quota.can_call(api_name):
        try:
            print(f"[API] Calling {api_name} for {target}")
            result = func(target, *args, **kwargs)
            
            # Basic validation that result is not an error
            if result and "error" not in result:
                quota.record_call(api_name)
                # 3. Store in Cache
                ttl = CACHE_TTL.get(api_name, 24)
                cache.set(target, api_name, result, ttl)
                return result
            else:
                print(f"[API] Error in {api_name} result: {result.get('error') if result else 'Empty result'}")
        except Exception as e:
            print(f"[API] Exception calling {api_name}: {e}")
    else:
        print(f"[QUOTA] Exhausted for {api_name}")

    # 4. Fallback Execution
    fallbacks = API_FALLBACKS.get(api_name, [])
    for fallback_api in fallbacks:
        # Note: We need a mapping from api name string to actual function.
        # For now, we'll return None and let the individual runner handle it 
        # OR we could pass a dictionary of functions.
        print(f"[FALLBACK] No primary result for {api_name}, trying fallbacks if available manually.")
        
    return None
