import socket

def resolve_ip(target: str) -> str:
    try:
        return socket.gethostbyname(target)
    except Exception:
        return None
