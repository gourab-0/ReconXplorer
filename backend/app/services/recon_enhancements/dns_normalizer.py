def normalize_dns(raw_dns: dict):
    normalized = {
        "a_records": [],
        "nameservers": [],
        "mail_servers": [],
        "txt_records": [],
        "cname": None
    }

    for rtype, data in raw_dns.items():
        if not isinstance(data, dict):
            continue
            
        answers = data.get("Answer", [])

        for ans in answers:
            value = ans.get("data")

            if rtype == "A":
                normalized["a_records"].append(value)
            elif rtype == "NS":
                normalized["nameservers"].append(value)
            elif rtype == "MX":
                normalized["mail_servers"].append(value)
            elif rtype == "TXT":
                normalized["txt_records"].append(value)
            elif rtype == "CNAME":
                normalized["cname"] = value

    return normalized
