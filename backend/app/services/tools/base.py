import subprocess
import shutil
import os
import time

class BaseTool:
    def __init__(self, target, timeout=300):
        self.target = target
        self.timeout = timeout
        self.tool_name = "base"

    def is_installed(self):
        return shutil.which(self.tool_name) is not None

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

    def _run_command(self, cmd):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                shell=False
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Timeout expired", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}
