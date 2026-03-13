from app.services.tools.plugins.subfinder import SubfinderTool
from app.services.tools.plugins.osint import OSINTTool
# We will migrate nmap and whatweb here later or wrap them

TOOL_REGISTRY = {
    "subfinder": SubfinderTool,
    "osint": OSINTTool
}

def get_tool(name, target, **kwargs):
    tool_class = TOOL_REGISTRY.get(name)
    if not tool_class:
        return None
    return tool_class(target, **kwargs)
