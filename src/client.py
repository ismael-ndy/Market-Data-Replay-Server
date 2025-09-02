import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 12345))

while True:
    data, addr = s.recvfrom(1024)
    print(f"Received packet from {addr}: {data}")