# mirrorhour

Utilities to detect and work with **mirror hours** (when hour and minute are equal, e.g., `11:11`, `22:22`) in local time or any IANA timezone. Provides a tiny **Python API** and a **CLI**.

## Features
- `is_mirror_time(dt)` — check if a datetime is a mirror hour.
- `next_mirror_time(dt)` — compute the next mirror hour.
- `all_mirror_times()` — list all mirror hours in a day.
- Optional 12-hour mode (`01:01` … `12:12`).
- Timezone-aware via `zoneinfo` (stdlib) and optional `tzdata`.

## Installation

```bash
pip install mirrorhour[cli]
# If your OS lacks a timezone database (common on Windows):
pip install tzdata
```

## Quick Start (CLI)

```bash
# Installed script
mirrorhour --tz Europe/Madrid

# Run via Python module
python -m mirrorhour.cli --tz Europe/Madrid

# 12-hour mode
mirrorhour --tz Europe/Madrid --twelve
```

**Options**
- `--tz <ZONE>`: IANA timezone (e.g., `Europe/Madrid`).
- `--twelve`: Use 12-hour mirror mode (`01:01` to `12:12`).

## Quick Start (Python)

```python
from mirrorhour import is_mirror_time, next_mirror_time, all_mirror_times
from datetime import datetime

now = datetime.now()

if is_mirror_time(now):
    print("It's a mirror hour!")
else:
    print("Next mirror hour:", next_mirror_time(now))

print("All mirror hours (24h):", all_mirror_times())
```

## API

- `is_mirror_time(dt: datetime | None = None, *, tz: str | None = None, use_24h: bool = True) -> bool`  
  Returns `True` if `dt` is a mirror hour.  
  - `tz`: IANA timezone name (e.g., `Europe/Madrid`).  
  - `use_24h`: if `True`, checks `HH == MM` in 24-hour clock; if `False`, checks 12-hour mirror set (`01:01`–`12:12`).

- `next_mirror_time(dt: datetime | None = None, *, tz: str | None = None, use_24h: bool = True) -> datetime`  
  Returns the next mirror hour (timezone-aware if `tz` provided). If `dt` is exactly on a mirror minute, returns `dt`.

- `all_mirror_times(day: date | None = None, *, use_24h: bool = True) -> list[datetime.time]`  
  Returns all mirror times for a day (naive `time` objects).  
  - 24h: `00:00, 01:01, …, 23:23` (24 items).  
  - 12h: `01:01, …, 12:12` (12 items).

## Requirements
- Python ≥ 3.9
- `tzdata` (only if your OS lacks an IANA timezone database)

## Testing

```bash
# Recommended for development
python -m pip install -e .[cli]
pytest -q
```

## Troubleshooting
- **Timezone errors**: install `tzdata` and pass `--tz <ZONE>`.
- **CLI not found**: ensure the environment is active (`.venv`) and that `mirrorhour` is on PATH, or run `python -m mirrorhour.cli`.

## License & Credits
- License: MIT  
- Author: **XaviDev41** (<4152@xavi.com.es>)  
- Repository: https://github.com/XaviDev41/mirrorhour
