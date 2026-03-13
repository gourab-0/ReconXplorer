from datetime import datetime

def normalize_whois(raw: dict):
    if not raw:
        return {}
        
    created = raw.get("creation_date")
    # API Ninjas sometimes returns list for dates or different formats. 
    # We'll try to handle the simple case or list case.
    if isinstance(created, list):
        created = created[0] if created else None

    age_days = None
    if created:
        try:
            # Check if it's timestamp (seconds) or string
            if isinstance(created, (int, float)):
                 dt_created = datetime.fromtimestamp(created)
            else:
                 # Try common ISO format or let it fail gracefully
                 # API Ninjas often returns seconds since epoch for creation_date
                 # But the provided code snippet assumed isoformat. 
                 # Let's support both if possible or stick to provided code logic but adding safety.
                 dt_created = datetime.fromisoformat(created) # This might fail if format differs
            
            age_days = (datetime.utcnow() - dt_created).days
        except:
            # If fromisoformat fails, try timestamp if it looks like a number in string
            try:
                 dt_created = datetime.fromtimestamp(float(created))
                 age_days = (datetime.utcnow() - dt_created).days
            except:
                pass

    return {
        "registrar": raw.get("registrar"),
        "country": raw.get("country"),
        "creation_date": created,
        "domain_age_days": age_days,
        "name_servers": raw.get("name_servers"),
        "emails": raw.get("emails")
    }
