import struct
import time


HEADER_FMT = "!BBB QQ"
BODY_FMT = "!B dd"

VERSION = 1
MSG_TYPE = 1
FLAG = 0

def build_header(seq_num: int, send_ts: int):
    return struct.pack(HEADER_FMT, VERSION, MSG_TYPE, FLAG, seq_num, send_ts)

def build_body(symbol: int, bid: float, ask: float):
    return struct.pack(BODY_FMT, symbol, bid, ask)

def build_packet(seq_num: int, symbol: int, bid: float, ask: float):
    send_ts = int(time.time_ns() // 1000)                 # Get current timestamp in microseconds
    header = build_header(seq_num, send_ts)
    body = build_body(symbol, bid, ask)
    return header + body
