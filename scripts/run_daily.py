from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vx_daily.pipeline import run_daily  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one AI WeChat draft.")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--min-score", type=int, default=None)
    parser.add_argument("--max-attempts", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = date.fromisoformat(args.date)
    article_dir = run_daily(ROOT, target_date, min_score=args.min_score, max_attempts=args.max_attempts)
    print(f"Draft generated: {article_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

