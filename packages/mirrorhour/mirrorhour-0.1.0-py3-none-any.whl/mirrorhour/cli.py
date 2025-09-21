from __future__ import annotations
import argparse
from datetime import datetime
from .core import is_mirror_time, next_mirror_time

def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror hour utilities.")
    parser.add_argument("--tz", type=str, default=None, help="IANA timezone, e.g., Europe/Madrid")
    parser.add_argument("--twelve", action="store_true", help="Use 12-hour mirror mode")
    args = parser.parse_args()

    now = datetime.now()
    mirror = is_mirror_time(now, tz=args.tz, use_24h=not args.twelve)
    nxt = next_mirror_time(now, tz=args.tz, use_24h=not args.twelve)

    print(f"Now: {now.isoformat()}")
    print(f"Is mirror time: {mirror}")
    print(f"Next mirror time: {nxt.isoformat()}")
