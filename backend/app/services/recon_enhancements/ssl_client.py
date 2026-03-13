import socket
import ssl

def fetch_ssl_cert(domain: str):
    context = ssl.create_default_context()
    
    # Handle potential connection errors
    try:
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        
        return {
            "provider": "ssl",
            "raw": cert
        }
    except Exception as e:
        return {
            "provider": "ssl",
            "error": str(e),
            "raw": {}
        }
