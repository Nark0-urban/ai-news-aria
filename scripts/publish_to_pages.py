# -*- coding: utf-8 -*-
"""Copy rendered cardnews files into docs/ for GitHub Pages."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        raise SystemExit(f"Missing source folder: {source}")
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        if item.is_file() and item.suffix.lower() in {".png", ".json"}:
            shutil.copy2(item, target / item.name)


def write_index(docs_dir: Path, site_title: str, base_url: str) -> None:
    entries: list[str] = []
    for day_dir in sorted((docs_dir / "cardnews").glob("*"), reverse=True):
        if not day_dir.is_dir():
            continue
        cards = sorted(day_dir.glob("card_*.png"))
        if not cards:
            continue
        day = day_dir.name
        first = f"cardnews/{day}/{cards[0].name}"
        entries.append(
            f"""
            <article>
              <a href="cardnews/{day}/index.html">
                <img src="{first}" alt="{day} cardnews cover">
                <strong>{day}</strong>
              </a>
            </article>
            """
        )

    body = "\n".join(entries) or "<p>아직 발행된 카드뉴스가 없습니다.</p>"
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{site_title}</title>
  <style>
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #eef6ff; color: #102652; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 40px 20px; }}
    h1 {{ margin: 0 0 24px; font-size: 34px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }}
    article {{ background: white; border: 1px solid #c8d8ec; border-radius: 8px; overflow: hidden; }}
    a {{ color: inherit; text-decoration: none; }}
    img {{ display: block; width: 100%; height: auto; }}
    strong {{ display: block; padding: 14px 16px 18px; }}
  </style>
</head>
<body>
  <main>
    <h1>{site_title}</h1>
    <section class="grid">
      {body}
    </section>
  </main>
</body>
</html>
"""
    (docs_dir / "index.html").write_text(html, encoding="utf-8")


def write_day_page(day_dir: Path, day: str, site_title: str) -> None:
    cards = sorted(day_dir.glob("card_*.png"))
    image_tags = "\n".join(
        f'<img src="{card.name}" alt="{day} {card.stem}">' for card in cards
    )
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{day} - {site_title}</title>
  <style>
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #102652; color: white; }}
    main {{ max-width: 720px; margin: 0 auto; padding: 24px 14px 42px; }}
    a {{ color: #8ed8ff; }}
    h1 {{ font-size: 24px; }}
    img {{ display: block; width: 100%; height: auto; margin: 18px 0; border-radius: 8px; }}
  </style>
</head>
<body>
  <main>
    <p><a href="../../">전체 목록</a></p>
    <h1>{day} AI 뉴스 아리아</h1>
    {image_tags}
  </main>
</body>
</html>
"""
    (day_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--base-url", default="https://nark0-urban.github.io/ai-news-aria")
    parser.add_argument("--site-title", default="AI News Aria")
    args = parser.parse_args()

    config_path = PROJECT_ROOT / args.config
    if not config_path.exists():
        config_path = PROJECT_ROOT / "config/config.example.json"
    config = load_json(config_path)

    source_dir = PROJECT_ROOT / config["cardnews"]["output_dir"] / args.date
    docs_dir = PROJECT_ROOT / "docs"
    target_dir = docs_dir / "cardnews" / args.date

    copy_tree(source_dir, target_dir)
    write_day_page(target_dir, args.date, args.site_title)
    write_index(docs_dir, args.site_title, args.base_url)

    page_url = f"{args.base_url.rstrip('/')}/cardnews/{args.date}/"
    image_url = f"{args.base_url.rstrip('/')}/cardnews/{args.date}/card_01.png"
    print(f"Published folder: {target_dir}")
    print(f"Page URL: {page_url}")
    print(f"Image URL: {image_url}")


if __name__ == "__main__":
    main()
