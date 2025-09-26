import socket 
import polars as pl
import argparse

from .packet_utils import build_packet
from .iterator import FXReplayIterator

from .processing import join_parquet_files, extract_data_folders

parser = argparse.ArgumentParser(description='FX Market Data Replay Server')
parser.add_argument('--speed', type=float, default=1, help='Replay speed multiplier')
parser.add_argument('--skip', type=int, default=0, help='Skip initial minutes of data')
args = parser.parse_args()

# Uncomment the following lines if you need to preprocess data (first run only)
# extract_data_folders()
# join_parquet_files()

file_path = "./data/parquet/2025-01.parquet"
df = pl.read_parquet(file_path)

replay_iterator = FXReplayIterator(df, replay_speed=args.speed, skip=args.skip)
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
    print(f"Sent packet {seq_num} for symbol {row['SYMBOL']} with BID {row['BID']} and ASK {row['ASK']}")
    seq_num += 1
