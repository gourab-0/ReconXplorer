import re

def normalize_harvester(raw: str):
    if not raw:
        return {"emails": [], "subdomains": []}

    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw)
    # Basic subdomain finding regex, might need refinement but good for now
    subdomains = list(set(re.findall(r"\b[\w.-]+\." + r"\w+\b", raw)))

    return {
        "emails": list(set(emails)),
        "subdomains": subdomains
    }
