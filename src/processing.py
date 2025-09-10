import polars as pl
import os
import json

COLUMN_NAMES = ["SYMBOL", "TIMESTAMP", "BID", "ASK"]
DTYPES = {
    "SYMBOL": pl.Utf8,
    "TIMESTAMP": pl.Utf8,
    "BID": pl.Float64,
    "ASK": pl.Float64
}
SYMBOL_HASHMAP_PATH = './symbol_hashmap.json'


def add_symbol_to_hashmap(symbol: str) -> bool:
    """
    Each unique symbol is assigned a unique integer ID.
    This mapping is stored in a JSON file for future reference.
    """
    if os.path.exists(SYMBOL_HASHMAP_PATH):
        with open(SYMBOL_HASHMAP_PATH, 'r') as f:
            symbol_map = json.load(f)
    else:
        symbol_map = {}

    if symbol not in symbol_map:
        symbol_map[symbol] = len(symbol_map)

    with open(SYMBOL_HASHMAP_PATH, 'w') as f:
        json.dump(symbol_map, f)

    return True


def lookup_symbol_id(symbol: str) -> int | None:
    """
    Retrieve the integer ID for a given symbol from the JSON mapping file.
    """
    if os.path.exists(SYMBOL_HASHMAP_PATH):
        with open(SYMBOL_HASHMAP_PATH, 'r') as f:
            symbol_map = json.load(f)
        return symbol_map.get(symbol, None)
    else:
        return None
    

def data_to_parquet(file_path: str, symbol: str) -> bool | None:
    """
    """
    symbol_id = lookup_symbol_id(symbol)
    if symbol_id is None:
        print(f"Symbol {symbol} not found in hashmap. Please add it first.")
        return None

    data = pl.read_csv(file_path, has_header=False, new_columns=COLUMN_NAMES, schema_overrides=DTYPES)

    data = data.with_columns(
        pl.col("TIMESTAMP").str.strptime(
            pl.Datetime,
            format="%Y%m%d %H:%M:%S%.3f"
        )
    )

    start_time = data["TIMESTAMP"].min()
    data = data.with_columns(
        (pl.col("TIMESTAMP") - start_time).dt.total_milliseconds().alias("DELTA")
    )

    data.drop_in_place("TIMESTAMP")

    data = data.with_columns(
        pl.lit(symbol_id).alias("SYMBOL")
    )

    data.write_parquet(f'./data/parquet/{symbol}-2025-01.parquet')
    return True

def extract_data_folders() -> bool | None:
    """
    Monthly organized folders containing CSV files are processed.
    Each CSV file is converted to Parquet format after updating the symbol hashmap.
    """
    folders_path = './data/raw'
    for folder in os.listdir(folders_path):
        folder_path = os.path.join(folders_path, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('.csv'):
                    symbol = file.split('-')[0]
                    add_symbol_to_hashmap(symbol)
                    new_file_name = f"{symbol}-2025-01.csv"
                    file_path = os.path.join(folder_path, new_file_name)
                    print(f"Processing file: {file_path}")
                    data_to_parquet(file_path, symbol)


def join_parquet_files() -> bool | None:
    """
    Combine multiple Parquet files for a given symbol into a single Parquet file.
    Final file is month's worth of data sorted by DELTA.
    """
    parquet_dir = './data/parquet'
    combined_df = None
    file_count = 0
    
    os.makedirs(parquet_dir, exist_ok=True)
    
    for file in os.listdir(parquet_dir):
        if file.endswith('.parquet') and not file == '2025-01.parquet':
            file_path = os.path.join(parquet_dir, file)
            try:
                df = pl.read_parquet(file_path)
                print(f"Successfully read: {file_path}")
                print(f"File shape: {df.shape}")
                
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pl.concat([combined_df, df])
                
                file_count += 1
                print(f"Combined shape after adding {file}: {combined_df.shape}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    if combined_df is not None and file_count > 0:
        combined_df = combined_df.sort("DELTA")
        output_path = f'{parquet_dir}/2025-01.parquet'
        
        combined_df.write_parquet(output_path)
        print(f"Final combined Parquet file written: {output_path}, shape: {combined_df.shape}")
        
        # Verification
        verification_df = pl.read_parquet(output_path)
        print(f"First 5 rows: {verification_df.head()}")
        print(f"Last 5 rows: {verification_df.tail()}")

        return True
    else:
        print("No files were combined.")
        return None
    