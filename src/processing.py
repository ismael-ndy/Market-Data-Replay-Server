import polars as pl
import numpy as np

column_names = ["SYMBOL", "TIMESTAMP", "BID", "ASK"]
dtypes = {
    "SYMBOL": pl.Utf8,
    "TIMESTAMP": pl.Utf8,
    "BID": pl.Float64,
    "ASK": pl.Float64
}

data = pl.read_csv('./data/raw/USDCAD-2025-01.csv', has_header=False, new_columns=column_names, schema_overrides=dtypes)
data = data.with_columns(
    pl.col("TIMESTAMP").str.strptime(
        pl.Datetime,
        format="%Y%m%d %H:%M:%S%.3f"
    )
)

print(data.head())