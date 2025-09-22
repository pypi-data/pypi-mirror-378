import socket


def check_port(host: str = '127.0.0.1', port: int = 22) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except:
        return False
    finally:
        s.close()
