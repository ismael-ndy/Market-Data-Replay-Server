import socket
import polars as pl

from .packet_utils import build_packet
from .iterator import FXReplayIterator


file_path = "./data/parquet/USDCAD-2025-01.parquet"
df = pl.read_parquet(file_path)

replay_iterator = FXReplayIterator(df, replay_speed=10000000)
seq_num = 0

for row in replay_iterator:
    packet = build_packet(
        seq_num=seq_num,
        symbol=row["SYMBOL"],
        bid=row["BID"],
        ask=row["ASK"]
    )

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(packet, ("192.168.2.31", 12345))
    udp_socket.close()
    print(f"Sent packet {seq_num} for symbol USD/CAD with BID {row['BID']} and ASK {row['ASK']}")
    seq_num += 1
