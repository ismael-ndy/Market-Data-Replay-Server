import time


class FXReplayIterator:
    def __init__(self, df, replay_speed=1.0):
        self.rows = df.iter_rows(named=True)
        self.start_time = time.perf_counter()
        self.replay_speed = replay_speed

    def __iter__(self):
        return self
    
    def __next__(self):
        row = next(self.rows)
        delta = row["DELTA"] / self.replay_speed
        target_time = (delta / 1000) + time.perf_counter()

        while time.perf_counter() < target_time:
            pass

        return row