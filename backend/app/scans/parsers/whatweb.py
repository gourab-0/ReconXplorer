import re

def parse_whatweb_output(output: str):
    technologies = set()

    # Example:
    # Apache[2.4.41], Country[UNITED STATES]
    matches = re.findall(r"([A-Za-z0-9\-_]+)\[", output)

    for tech in matches:
        technologies.add(tech)

    return {
        "summary": "Web technologies identified",
        "technologies": list(technologies)
    }
