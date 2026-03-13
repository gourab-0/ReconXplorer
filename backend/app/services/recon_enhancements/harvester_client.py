import subprocess
import shutil

def run_harvester(domain: str):
    if not shutil.which("theHarvester"):
        return {
            "provider": "theharvester",
            "error": "theHarvester executable not found in PATH",
            "raw": ""
        }

    try:
        cmd = ["theHarvester", "-d", domain, "-b", "google"]
        # Added timeout to prevent hanging forever
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return {
            "provider": "theharvester",
            "raw": result.stdout
        }
    except subprocess.TimeoutExpired:
        return {
            "provider": "theharvester",
            "error": "Timeout expired",
            "raw": ""
        }
    except Exception as e:
        return {
            "provider": "theharvester",
            "error": str(e),
            "raw": ""
        }
