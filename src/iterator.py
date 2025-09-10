import time
import polars as pl


class FXReplayIterator:
    def __init__(self, df, replay_speed=1.0, skip=0):
        # Skip minutes by filtering rows where DELTA is less than skip_ms
        if skip > 0:
            skip_ms = skip * 60 * 1000  # Convert minutes to milliseconds
            df = df.filter(pl.col("DELTA") >= skip_ms)
            print(f"Skipping data for the first {skip} minutes ({skip_ms} ms)")
        
        self.rows = df.iter_rows(named=True)
        self.start_time = time.perf_counter()
        self.replay_speed = replay_speed
        self.skip = skip

    def __iter__(self):
        return self
    
    def __next__(self):
        row = next(self.rows)
        delta = row["DELTA"] / self.replay_speed
        target_time = (delta / 1000) + time.perf_counter()

        while time.perf_counter() < target_time:
            pass

        return row