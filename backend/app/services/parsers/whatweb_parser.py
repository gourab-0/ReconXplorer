import json
from typing import Dict, Any


def parse_whatweb_json(raw_json: str) -> Dict[str, Any]:
    """
    Parse WhatWeb JSON output and normalize it for frontend & DB storage.
    """

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "technologies": [],
            "categories": [],
            "findings_count": 0,
            "severity": "info",
            "error": "Failed to parse JSON"
        }

    technologies = []
    categories = set()

    # --- Handle builtwith fallback format ---
    if isinstance(data, dict) and "plugins" not in data:
        # builtwith returns { category: [tech1, tech2] }
        for category, techs in data.items():
            if isinstance(techs, list):
                for tech in techs:
                    technologies.append(str(tech))
                    categories.add(category)
            else:
                technologies.append(str(techs))
                categories.add(category)
    
    # --- Handle WhatWeb JSON array format ---
    elif isinstance(data, list):
        for entry in data:
            plugins = entry.get("plugins", {})

            for tech_name, tech_data in plugins.items():
                display_name = tech_name
                
                if isinstance(tech_data, dict):
                    v = tech_data.get("version")
                    if v:
                        if isinstance(v, list): v = v[0]
                        display_name += f" ({v})"

                    if "categories" in tech_data:
                        for cat in tech_data["categories"]:
                            categories.add(cat)
                
                technologies.append(display_name)

    findings_count = len(technologies)

    # Severity logic (simple & safe for now)
    if findings_count == 0:
        severity = "info"
    elif findings_count <= 5:
        severity = "low"
    elif findings_count <= 15:
        severity = "medium"
    else:
        severity = "high"

    normalized = {
        "technologies": technologies,
        "categories": list(categories),
        "findings_count": findings_count,
        "severity": severity,
    }

    return normalized
