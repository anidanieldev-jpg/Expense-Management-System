import socket
import sys

targets = [
    ("sheets.googleapis.com", 443),
    ("www.google.com", 443),
    ("8.8.8.8", 53) # IP check
]

print(f"Python executable: {sys.executable}")
print("-" * 30)

for host, port in targets:
    print(f"Testing {host}:{port}...")
    try:
        # 1. DNS Resolution
        if host.replace('.', '').isdigit():
            ip = host
            print(f"  Skipping DNS (IP provided): {ip}")
        else:
            print(f"  Attempting DNS resolution...")
            ip = socket.gethostbyname(host)
            print(f"  DNS Resolved: {ip}")
            
        # 2. Socket Connection
        print(f"  Attempting TCP connection to {ip}:{port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((ip, port))
        s.close()
        
        if result == 0:
            print("  SUCCESS: Connection established.")
        else:
            print(f"  FAILURE: Connection refused/timeout (Error code: {result})")
            
    except Exception as e:
        print(f"  CRITICAL FAILURE: {type(e).__name__}: {e}")
    print("-" * 30)
