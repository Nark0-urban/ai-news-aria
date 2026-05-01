# -*- coding: utf-8 -*-
"""Render AI News Aria cardnews PNG files from cards.json.

This renderer uses existing character assets plus text/layout templates.
It does not call any paid image generation API.
"""

from __future__ import annotations

import argparse
import json
import textwrap
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sample_cards(day: str) -> dict[str, Any]:
    return {
        "date": day,
        "cards": [
            {
                "type": "cover",
                "title": "어제 AI 뉴스 핵심 요약",
                "summary": "중요한 변화만 빠르게 정리했어요.",
                "aria_line": "오늘은 흐름을 바꿀 만한 소식만 콕 집어줄게요!",
                "caption": "AI 뉴스 큐레이터 아리아",
                "importance": "브리핑",
                "sources": [],
            },
            {
                "type": "news",
                "title": "제품 업데이트",
                "summary": "새 모델, 새 기능, 가격 정책 변화처럼 실사용에 영향을 주는 소식을 우선 확인합니다.",
                "aria_line": "업데이트는 기능보다 내 작업이 어떻게 달라지나를 보면 쉬워요.",
                "caption": "실무 영향 중심으로 보기",
                "importance": "중요",
                "sources": [{"name": "출처 예시", "url": "https://example.com"}],
            },
            {
                "type": "point",
                "title": "오늘 주목할 포인트",
                "summary": "반복해서 등장하는 키워드를 모아 내일 확인할 흐름을 정합니다.",
                "aria_line": "뉴스는 하루치만 보면 점이고, 며칠 묶어 보면 방향이 보여요.",
                "caption": "내일 다시 볼 키워드",
                "importance": "체크",
                "sources": [],
            },
        ],
    }


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/NotoSansKR-Bold.otf" if bold else "C:/Windows/Fonts/NotoSansKR-Regular.otf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for token in paragraph.split():
            candidate = token if not current else f"{current} {token}"
            bbox = draw.textbbox((0, 0), candidate, font=font_obj)
            if bbox[2] - bbox[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = token
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font_obj: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    max_width: int,
    line_height: int,
    max_lines: int,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, font_obj, max_width)[:max_lines]:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += line_height
    return y


def paste_character(canvas: Image.Image, reference_path: Path, width: int, height: int) -> None:
    if not reference_path.exists():
        return
    ref = Image.open(reference_path).convert("RGBA")
    target_w = 560
    target_h = int(ref.height * (target_w / ref.width))
    ref = ref.resize((target_w, target_h), Image.Resampling.LANCZOS)
    x = width - target_w + 20
    y = height - target_h + 40

    fade = Image.new("RGBA", ref.size, (255, 255, 255, 0))
    ref = Image.blend(ref, fade, 0.08)
    canvas.alpha_composite(ref, (x, y))


def draw_card(card: dict[str, Any], index: int, total: int, config: dict[str, Any], output_path: Path) -> None:
    width = int(config["cardnews"]["image_width"])
    height = int(config["cardnews"]["image_height"])
    reference_path = PROJECT_ROOT / config["cardnews"]["character_reference"]

    canvas = Image.new("RGBA", (width, height), (232, 244, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for y in range(height):
        ratio = y / height
        r = int(246 * (1 - ratio) + 218 * ratio)
        g = int(251 * (1 - ratio) + 238 * ratio)
        b = 255
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    paste_character(canvas, reference_path, width, height)
    draw = ImageDraw.Draw(canvas)

    navy = (12, 38, 82)
    blue = (0, 166, 230)
    gold = (247, 183, 38)
    gray = (74, 88, 112)
    white = (255, 255, 255)
    panel_border = (26, 66, 118)

    panel = (64, 82, 784, 992)
    draw.rounded_rectangle(panel, radius=34, fill=(255, 255, 255, 238), outline=panel_border, width=5)

    meta_font = font(30, bold=True)
    title_font = font(72, bold=True)
    body_font = font(39)
    speech_font = font(38, bold=True)
    small_font = font(30)
    source_font = font(24)

    draw.text((92, 120), f"CARD {index:02d} / {total}", font=meta_font, fill=blue)
    draw.text((92, 164), str(card.get("importance") or "뉴스"), font=meta_font, fill=gold)

    title = str(card.get("title") or "AI 뉴스 아리아")
    summary = str(card.get("summary") or "요약 내용이 아직 없습니다.")
    aria_line = str(card.get("aria_line") or "핵심만 차분하게 정리해볼게요.")
    caption = str(card.get("caption") or "AI 뉴스 큐레이터 아리아")

    next_y = draw_wrapped(draw, (92, 235), title, title_font, navy, 620, 84, 3)
    draw_wrapped(draw, (96, max(next_y + 28, 410)), summary, body_font, gray, 610, 55, 4)

    speech_box = (92, 690, 734, 920)
    draw.rounded_rectangle(speech_box, radius=32, fill=white, outline=navy, width=4)
    draw_wrapped(draw, (126, 728), aria_line, speech_font, navy, 570, 52, 3)

    sources = card.get("sources") or []
    names = [str(source.get("name")) for source in sources if isinstance(source, dict) and source.get("name")]
    if names:
        draw_wrapped(draw, (92, 1012), "출처: " + ", ".join(names), source_font, gray, 900, 34, 2)

    footer = (64, 1086, 1016, 1236)
    draw.rounded_rectangle(footer, radius=28, fill=(9, 32, 70, 230))
    draw_wrapped(draw, (100, 1125), caption, small_font, white, 850, 42, 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"Rendered: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.json")
    parser.add_argument("--cards-json", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    config_path = PROJECT_ROOT / args.config
    if not config_path.exists():
        config_path = PROJECT_ROOT / "config/config.example.json"
    config = load_json(config_path)

    output_dir = PROJECT_ROOT / config["cardnews"]["output_dir"] / args.date
    default_cards_path = output_dir / "cards.json"

    if args.cards_json:
        data = load_json(PROJECT_ROOT / args.cards_json)
    elif default_cards_path.exists() and not args.sample:
        data = load_json(default_cards_path)
    else:
        data = sample_cards(args.date)
        save_json(default_cards_path, data)

    cards = data.get("cards") or []
    for idx, card in enumerate(cards, start=1):
        draw_card(card, idx, len(cards), config, output_dir / f"card_{idx:02d}.png")

    print(f"Done: {output_dir}")


if __name__ == "__main__":
    main()
