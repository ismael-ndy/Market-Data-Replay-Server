import polars as pl

COLUMN_NAMES = ["SYMBOL", "TIMESTAMP", "BID", "ASK"]
DTYPES = {
    "SYMBOL": pl.Utf8,
    "TIMESTAMP": pl.Utf8,
    "BID": pl.Float64,
    "ASK": pl.Float64
}


def process_data(file_path):
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
    data.sort("DELTA")

    data = data.with_columns(
        pl.lit(1).alias("SYMBOL")
    )

    data.write_parquet('./data/parquet/USDCAD-2025-01.parquet')

    

