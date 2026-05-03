# -*- coding: utf-8 -*-
"""Send the latest published cardnews page to Kakao from local config."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def find_latest_day(cardnews_root: Path) -> str:
    days = [
        path.name
        for path in cardnews_root.iterdir()
        if path.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", path.name)
    ]
    if not days:
        raise SystemExit(f"No dated cardnews folders found under {cardnews_root}")
    return sorted(days)[-1]


def wait_for_page(url: str, marker: str, wait_seconds: int, interval_seconds: int) -> None:
    deadline = time.time() + wait_seconds
    last_error = ""
    while time.time() <= deadline:
        try:
            with urlopen(url, timeout=20) as response:
                content = response.read().decode("utf-8", errors="replace")
            if marker in content:
                return
            last_error = f"Page loaded but marker was missing: {marker}"
        except URLError as exc:
            last_error = str(exc)
        time.sleep(interval_seconds)
    print(f"Warning: page was not confirmed before sending Kakao: {last_error}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="")
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--base-url", default="https://nark0-urban.github.io/ai-news-aria")
    parser.add_argument("--image-url", default="")
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--interval-seconds", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cardnews_root = PROJECT_ROOT / "docs" / "cardnews"
    day = args.date or find_latest_day(cardnews_root)
    page_url = f"{args.base_url.rstrip('/')}/cardnews/{day}/"
    image_url = args.image_url or f"{args.base_url.rstrip('/')}/assets/kakao_thumbnail_20260501_v2.png"

    if not args.dry_run:
        wait_for_page(page_url, "card_01.png", args.wait_seconds, args.interval_seconds)

    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "send_kakao.py"),
        "--config",
        args.config,
        "--title",
        "AI 뉴스 아리아",
        "--description",
        "오늘의 AI 카드뉴스가 업데이트됐습니다.",
        "--image-url",
        image_url,
        "--link-url",
        page_url,
        "--button-title",
        "카드뉴스 확인하기",
        "--fallback-text",
    ]
    if args.dry_run:
        command.append("--dry-run")

    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
