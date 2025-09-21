from datetime import datetime, timezone
from mirrorhour.core import is_mirror_time, next_mirror_time

def test_is_mirror_time_basic():
    dt = datetime(2025, 1, 1, 11, 11, tzinfo=timezone.utc)
    assert is_mirror_time(dt)

def test_next_mirror_time_rounds_up():
    dt = datetime(2025, 1, 1, 11, 10, tzinfo=timezone.utc)
    nxt = next_mirror_time(dt)
    assert nxt.hour == 11 and nxt.minute == 11
