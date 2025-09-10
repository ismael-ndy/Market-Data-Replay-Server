import os
import polars as pl
import pytest

from src.processing import add_symbol_to_hashmap, lookup_symbol_id, data_to_parquet, SYMBOL_HASHMAP_PATH

@pytest.fixture(autouse=True)
def cleanup_symbol_hashmap():
    # Remove the symbol hashmap before and after each test for isolation
    if os.path.exists(SYMBOL_HASHMAP_PATH):
        os.remove(SYMBOL_HASHMAP_PATH)
    yield
    if os.path.exists(SYMBOL_HASHMAP_PATH):
        os.remove(SYMBOL_HASHMAP_PATH)

def test_add_and_lookup_symbol():
    assert add_symbol_to_hashmap("USDCAD") is True
    symbol_id = lookup_symbol_id("USDCAD")
    assert symbol_id == 0

def test_data_to_parquet(tmp_path):
    # Create a sample CSV file
    csv_content = "USDCAD,20250101 22:00:41.824,1.23456,1.23478\nUSDCAD,20250101 22:00:42.824,1.23457,1.23479"
    csv_path = tmp_path / "USDCAD-2025-01.csv"
    with open(csv_path, "w") as f:
        f.write(csv_content)
    add_symbol_to_hashmap("USDCAD")
    result = data_to_parquet(str(csv_path), "USDCAD")
    assert result is True

    # Check for the parquet file in the correct data/parquet directory from the project root
    parquet_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "parquet", "USDCAD-2025-01.parquet")
    assert os.path.exists(parquet_path)