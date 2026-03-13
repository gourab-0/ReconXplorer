import platform
import shutil
import subprocess
import json
import os
import re

def validate_target(target: str) -> bool:
    """
    Validates if the target is a valid hostname or IP address.
    Strict regex to prevent command injection.
    """
    # Simple regex for domain/IP
    # Allows: example.com, 1.2.3.4, sub.domain.co.uk
    # Disallows: ; & | $ ` ( ) { } [ ] \ ' " < >
    regex = r"^[a-zA-Z0-9.-]+$"
    return bool(re.match(regex, target))

def get_os():
    return platform.system().lower()  # windows / linux / darwin

# Path resolution for bundled tools
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_RUBY_EXE = os.path.join(_BASE_DIR, "ruby", "bin", "ruby.exe" if get_os() == "windows" else "ruby")
_WHATWEB_SCRIPT = os.path.join(_BASE_DIR, "whatweb-bin", "whatweb")

def is_tool_installed(tool_name: str) -> bool:
    if tool_name == "whatweb":
        # Check for bundled whatweb + ruby
        if os.path.exists(_RUBY_EXE) and os.path.exists(_WHATWEB_SCRIPT):
            return True
        # Check if whatweb is in system PATH
        if shutil.which(tool_name) is not None:
            return True
        try:
            import builtwith
            return True
        except ImportError:
            return False
    return shutil.which(tool_name) is not None

def build_nmap_command(target: str, xml_path: str):
    return [
        "nmap",
        "-T5",                 # Insane speed for demo
        "-n",                  # Skip DNS resolution (we do it manually)
        "--top-ports", "100",
        "-sV",
        "--open",
        "--min-rate", "1000",  # Send packets at a decent speed
        "--max-retries", "1",  # Don't waste time on flaky ports
        "-oX", xml_path,
        target
    ]


def build_whatweb_command(target: str):
    # Sanitize target (basic check)
    if not validate_target(target.replace("http://", "").replace("https://", "")):
        raise ValueError(f"Invalid target format: {target}")

    # Check if bundled whatweb exists
    if os.path.exists(_RUBY_EXE) and os.path.exists(_WHATWEB_SCRIPT):
        return [
            _RUBY_EXE,
            _WHATWEB_SCRIPT,
            "-a", "3",
            "--log-json=-",
            "-q",
            target
        ]
    # Check if whatweb is in system PATH
    if shutil.which("whatweb"):
        return [
            "whatweb",
            "-a", "3",
            "--log-json=-",
            "-q",
            target
        ]
    
    # Safe fallback using python libraries
    fallback_code = (
        "import sys, json, requests; "
        "try: import builtwith; "
        "except: builtwith = None; "
        "target = sys.argv[1]; "
        "url = f'http://{target}' if '://' not in target else target; "
        "results = {}; "
        "try: "
        "    if builtwith: results.update(builtwith.parse(url) or {}); "
        "    r = requests.get(url, timeout=10, verify=False, headers={'User-Agent': 'Mozilla/5.0'}); "
        "    server = r.headers.get('Server'); "
        "    if server: "
        "        if 'Web Infrastructure' not in results: results['Web Infrastructure'] = []; "
        "        results['Web Infrastructure'].append(server); "
        "    powered = r.headers.get('X-Powered-By'); "
        "    if powered: "
        "        if 'Programming Languages' not in results: results['Programming Languages'] = []; "
        "        results['Programming Languages'].append(powered); "
        "    print(json.dumps(results)); "
        "except Exception as e: "
        "    print(json.dumps({'error': str(e), 'partial': results}))"
    )
    return ["python", "-c", fallback_code, target]

def execute_command(command: list, timeout: int = 300):
    """
    Executes a system command with a timeout.
    Uses shell=False by default for security and correct process management.
    """
    try:
        # Use subprocess.run with check=False because we handle returncodes manually
        # and we want to capture stdout/stderr even on failure.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False 
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired as e:
        # result.stdout/stderr are partially available in the exception object
        return {
            "stdout": e.stdout.decode() if e.stdout else "",
            "stderr": f"Execution timed out after {timeout}s",
            "returncode": -1,
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }
