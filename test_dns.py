import socket
try:
    print(f"IP: {socket.gethostbyname('quote-api.jup.ag')}")
except Exception as e:
    print(f"Error: {e}")
