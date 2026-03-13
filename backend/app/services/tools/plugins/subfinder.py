from app.services.tools.base import BaseTool
import json
import tempfile
import os

class SubfinderTool(BaseTool):
    def __init__(self, target, timeout=300):
        super().__init__(target, timeout)
        self.tool_name = "subfinder"

    def execute(self):
        if not self.is_installed():
            return {"success": False, "error": "Subfinder not installed", "subdomains": []}

        # Use JSON output for easier parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        cmd = [self.tool_name, "-d", self.target, "-silent", "-o", tmp_path, "-oJ"]
        run_result = self._run_command(cmd)

        subdomains = []
        if os.path.exists(tmp_path):
            try:
                with open(tmp_path, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            subdomains.append(data.get("host"))
            except Exception as e:
                run_result["stderr"] += f"\nParsing error: {str(e)}"
            finally:
                os.unlink(tmp_path)

        return {
            "success": run_result["success"],
            "subdomains": list(set(subdomains)),
            "raw": run_result["stdout"],
            "error": run_result["stderr"]
        }
