import socket
import struct
import time

HEADER_FMT = "!BBB QQ"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 12345))

expected_seq = None
lost = 0
total = 0
start_time = time.perf_counter()

while True:
    data, addr = s.recvfrom(1024)
    if len(data) < HEADER_SIZE:
        continue

    
    header = data[:HEADER_SIZE]
    version, msg_type, flag, seq_num, send_ts = struct.unpack(HEADER_FMT, header)

    if expected_seq is not None and seq_num != expected_seq:
        lost += seq_num - expected_seq
    expected_seq = seq_num + 1
    total += 1

    if total % 100 == 0:  # Print stats every 100 packets
        loss_percent = (lost / (lost + total)) * 100 if (lost + total) > 0 else 0
        print(f"Packet loss: {lost} lost, {total} received, {loss_percent:.2f}% loss, PPS: {total/(time.perf_counter()-start_time):.2f}")