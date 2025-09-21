from __future__ import annotations
from datetime import datetime, time, timedelta, date
from typing import Iterable, List, Optional

try:
    # Python 3.9+: zoneinfo is stdlib; tzdata (optional dep) provides DB on some OSes
    from zoneinfo import ZoneInfo  # type: ignore
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


def _ensure_tz(dt: Optional[datetime] = None, tz: Optional[str] = None) -> datetime:
    """Return an aware datetime using provided tz name or dt.tzinfo; fallback to local naive dt."""
    if dt is None:
        dt = datetime.now()
    if tz:
        if ZoneInfo is None:
            raise RuntimeError("zoneinfo not available; install Python 3.9+ and optional 'tzdata'.")
        return dt.astimezone(ZoneInfo(tz)) if dt.tzinfo else dt.replace(tzinfo=ZoneInfo(tz))
    return dt if dt.tzinfo else dt


def is_mirror_time(dt: Optional[datetime] = None, *, tz: Optional[str] = None, use_24h: bool = True) -> bool:
    """
    Return True if the time is a mirror hour: HH:HH (e.g., 11:11, 22:22).
    - use_24h=True checks 00:00..23:23 (where minutes equal hour).
    - use_24h=False checks 12h clock (01..12 mirrored to minutes 01..12); 12:12 counts.
    """
    dt = _ensure_tz(dt, tz)
    h = dt.hour
    m = dt.minute
    if use_24h:
        return h == m
    # 12h mode: mirror times from 01:01 to 12:12
    h12 = ((h - 1) % 12) + 1
    return h12 == m and 1 <= m <= 12


def all_mirror_times(day: Optional[date] = None, *, use_24h: bool = True) -> List[time]:
    """
    List all mirror times in a day as `datetime.time` objects (naive).
    - 24h: 00:00, 01:01, ..., 23:23  (24 items)
    - 12h: 01:01..12:12               (12 items)
    """
    items: List[time] = []
    if use_24h:
        for h in range(24):
            items.append(time(hour=h, minute=h))
    else:
        for h in range(1, 13):
            items.append(time(hour=h % 12, minute=h if h < 60 else 0))
    return items


def next_mirror_time(dt: Optional[datetime] = None, *, tz: Optional[str] = None, use_24h: bool = True) -> datetime:
    """
    Return the next mirror time >= dt in the given timezone (aware datetime).
    If dt is exactly a mirror time (seconds=0), returns dt itself.
    """
    dt = _ensure_tz(dt, tz)
    # normalize seconds/microseconds for comparison
    base = dt.replace(second=0, microsecond=0)
    candidates: List[datetime] = []

    if use_24h:
        for h in range(base.hour, 24):
            t = base.replace(hour=h, minute=h)
            if t >= base:
                candidates.append(t)
        if not candidates:
            # next day 00:00
            candidates.append((base + timedelta(days=1)).replace(hour=0, minute=0))
    else:
        # Build next occurrences today in 12h mirror set
        h12_now = ((base.hour - 1) % 12) + 1
        for k in range(0, 24):  # span up to next day
            t_candidate = base + timedelta(minutes=1 * k)
            if is_mirror_time(t_candidate, use_24h=False):
                candidates.append(t_candidate.replace(second=0, microsecond=0))
                break
        if not candidates:
            # fallback to next day 01:01 local
            next_day = (base + timedelta(days=1)).replace(hour=1, minute=1, second=0, microsecond=0)
            candidates.append(next_day)

    return min(candidates)
