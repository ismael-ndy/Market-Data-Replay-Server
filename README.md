# Market Data Replay Server

A high-performance UDP-based market data replay system for simulating live FX (Foreign Exchange) market conditions. This server replays historical market data with configurable speed and timing controls, making it ideal for testing trading algorithms, backtesting strategies, and system integration testing.

## Project Overview

The Market Data Replay Server processes historical FX market data from CSV files and streams it via UDP packets to simulate real-time market conditions. It supports multiple currency pairs, configurable replay speeds, and the ability to skip initial periods of data. The system is designed with performance in mind, using efficient data structures and minimal latency packet transmission.

## Features

- **Multi-Symbol Support**: Process multiple currency pairs (AUDJPY, AUDUSD, EURJPY, GBPUSD, etc.)
- **Configurable Replay Speed**: Adjust playback speed with multipliers (e.g., 10000x faster)
- **Time-based Skipping**: Skip initial minutes of data for targeted testing
- **Efficient Data Processing**: Uses Polars for fast data manipulation and Parquet for optimized storage
- **Real-time Streaming**: UDP-based packet transmission with sequence numbering
- **Packet Loss Detection**: Client-side packet loss monitoring and statistics
- **TCP Replay**: Sends lost packets over TCP to ensure delivery
- **Symbol ID Mapping**: Efficient integer-based symbol identification

## Setup Instructions

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Installation

1. Clone the repository:

```bash
git clone https://github.com/ismael-ndy/Market-Data-Replay-Server.git
cd Market-Data-Replay-Server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. The data directory structure should already exist:

```
data/
├── raw/           # Raw CSV files organized by symbol
└── parquet/       # Processed Parquet files
```

### Data Format

Your CSV files should follow this format (no headers):

```
AUDJPY,20250101 00:00:00.000,0.9234,0.9235
AUDJPY,20250101 00:00:01.000,0.9234,0.9236
```

Columns: `SYMBOL,TIMESTAMP,BID,ASK`

### Running the System

1. **Process raw data** (first time setup - uncomment lines in replay_loop.py):

```python
# Uncomment these lines in src/replay_loop.py for first run
extract_data_folders()  # Process raw CSV files
join_parquet_files()    # Combine into single sorted file
```

2. **Start the replay server**:

```bash
python -m src.replay_loop --speed 10000 --skip 30
```

Parameters:

- `--speed`: Replay speed multiplier (default: 1)
- `--skip`: Skip initial minutes of data (default: 0)

3. **Run the client** (for testing/monitoring):

```bash
python -m src.client
```

## Design Decisions

### Data Processing Architecture

**Polars over Pandas**: I chose Polars for data processing due to its superior performance with large datasets and better memory efficiency. The lazy evaluation and columnar storage make it ideal for time-series financial data.

**Parquet Storage**: Raw CSV data is converted to Parquet format for several reasons:

- **Compression**: Significantly smaller file sizes
- **Performance**: Faster read/write operations
- **Type Safety**: Preserves data types without parsing overhead
- **Columnar Access**: Efficient for time-series operations

**Symbol ID Mapping**: Instead of transmitting string symbols in packets, we use integer IDs stored in `symbol_hashmap.json`:

- Reduces packet size for high-frequency transmission
- Maintains referential integrity
- Allows for easy symbol lookup on client side

### Network Architecture

**UDP over TCP**: UDP was chosen for packet transmission because:

- **Lower Latency**: No connection handshake overhead
- **Higher Throughput**: No acknowledgment waiting
- **Real-time Simulation**: Better mimics actual market data feeds
- **Packet Loss Handling**: Allows testing of loss scenarios

**Packet Structure**: Custom binary packet format optimized for market data:

```
Header: [Version][MsgType][Flag][SeqNum][Timestamp] (19 bytes)
Body:   [SymbolID][Bid][Ask] (17 bytes)
Total:  36 bytes per packet
```

### Timing and Synchronization

**Delta-based Timing**: All timestamps are converted to millisecond deltas from the start time:

- Eliminates timezone complexities
- Enables precise replay timing
- Simplifies skip logic implementation
- Reduces computational overhead during replay

**Busy-wait Loop**: Uses `time.perf_counter()` with busy-waiting instead of `time.sleep()` for microsecond precision timing accuracy.

### Iterator Pattern

The `FXReplayIterator` class implements Python's iterator protocol, providing:

- **Memory Efficiency**: Streams data row-by-row instead of loading everything
- **Configurable Speed**: Real-time speed adjustment
- **Skip Functionality**: Efficient data skipping without loading unwanted rows
- **Clean API**: Simple for-loop integration

## What's Left to Implement

### TCP Replay Support

Currently, only UDP transmission is implemented. TCP support would add:

- **Reliable Delivery**: Guaranteed packet delivery for critical applications
- **Error Recovery**: Automatic retransmission of lost packets

## Future Improvements

### Performance Enhancements

- **Multi-threading**: Separate threads for data reading and packet transmission
- **Batch Transmission**: Send multiple packets per UDP datagram

### Protocol Improvements

- **Heartbeat Messages**: Keep-alive packets for connection monitoring

### Monitoring and Analytics

- **Real-time Metrics Dashboard**: Packets/second, latency distribution, client count
- **Web Interface**: Real-time monitoring with charts and graphs

### Configuration Management

- **YAML Configuration**: Replace command-line args with config files
- **Dynamic Reconfiguration**: Change settings without restart
- **Symbol Filtering**: Configure which symbols to replay

### Data Source Expansion

- **Multiple Data Providers**: Support different CSV formats and schemas
- **Database Integration**: Direct database data source support

## File Structure

```
Market-Data-Replay-Server/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── symbol_hashmap.json         # Symbol ID mappings
├── data/
│   ├── raw/                    # Raw CSV files by symbol
│   │   ├── AUDJPY-2025-01/
│   │   ├── AUDUSD-2025-01/
│   │   └── ...
│   └── parquet/                # Processed Parquet files
│       ├── AUDJPY-2025-01.parquet
│       ├── AUDUSD-2025-01.parquet
│       └── 2025-01.parquet     # Combined sorted file
├── src/
│   ├── __init__.py
│   ├── client.py               # UDP client for testing
│   ├── iterator.py             # FX replay iterator
│   ├── packet_utils.py         # Packet serialization
│   ├── processing.py           # Data processing pipeline
│   ├── replay_loop.py          # Main server entry point
│   └── server.py               # Server implementation
└── tests/
    ├── __init__.py
    └── test_processing.py      # Unit tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
