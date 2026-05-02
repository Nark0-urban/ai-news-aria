# -*- coding: utf-8 -*-
"""Render AI News Aria cardnews PNG files from cards.json.

The renderer uses the fixed visual template in assets/templates and only paints
text into reserved areas. It does not call image generation APIs.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT_ROOT / "assets" / "templates" / "ai_news_aria_layout_visual_v1.png"

NAVY = (11, 38, 84, 255)
MUTED = (70, 84, 110, 255)
BLUE = (0, 133, 204, 255)
WHITE = (255, 255, 255, 255)


def clean_day(value: str) -> str:
    text = str(value or "")
    return text[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", text) else text


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
                "title": "전날 AI 뉴스 핵심 요약",
                "summary": "하루 동안 나온 중요한 AI 소식만 골라 읽기 쉽게 정리했어요.",
                "bullets": [
                    "제품 업데이트와 모델 변경",
                    "정책·규제와 산업 흐름",
                    "개발자가 바로 확인할 포인트",
                ],
                "aria_line": "중요한 것만 빠르게 볼까요?",
                "caption": "AI 뉴스 큐레이터 아리아",
                "importance": "Brief",
                "source_date": day,
                "sources": [],
            },
            {
                "type": "news",
                "title": "AI 제품 업데이트 체크",
                "summary": "새 모델, 가격 정책, 개발자 도구 변화처럼 실제 업무에 영향을 줄 수 있는 소식을 우선 확인합니다.",
                "bullets": [
                    "무엇이 바뀌었는지",
                    "누구에게 영향이 있는지",
                    "오늘 바로 확인할 설정",
                ],
                "aria_line": "기능보다 업무 영향부터 보면 이해가 쉬워요.",
                "caption": "제품·개발자 업데이트",
                "importance": "Important",
                "source_date": day,
                "sources": [{"name": "Example", "url": "https://example.com"}],
            },
        ],
    }


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        PROJECT_ROOT / "assets" / "fonts" / "Pretendard-Medium.otf",
        PROJECT_ROOT / "assets" / "fonts" / "Pretendard-Regular.otf",
        PROJECT_ROOT / "assets" / "fonts" / "S-CoreDream-4Regular.otf",
        Path("C:/Windows/Fonts/Pretendard-Medium.otf"),
        Path("C:/Windows/Fonts/Pretendard-Regular.otf"),
        Path("C:/Windows/Fonts/malgun.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font_obj)
    return box[2] - box[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_obj: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    result: list[str] = []
    for raw_paragraph in str(text or "").splitlines() or [""]:
        paragraph = raw_paragraph.strip()
        if not paragraph:
            result.append("")
            continue

        current = ""
        for char in paragraph:
            candidate = current + char
            if text_width(draw, candidate, font_obj) <= max_width:
                current = candidate
            else:
                break_at = current.rfind(" ")
                if break_at > 0:
                    result.append(current[:break_at].rstrip())
                    current = (current[break_at + 1 :] + char).lstrip()
                else:
                    if current:
                        result.append(current.rstrip())
                    current = char.lstrip()
        if current:
            result.append(current.rstrip())
    return result


def ellipsize(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> str:
    text = str(text or "")
    if text_width(draw, text, font_obj) <= max_width:
        return text
    suffix = "..."
    while text and text_width(draw, text + suffix, font_obj) > max_width:
        text = text[:-1]
    return text + suffix if text else suffix


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_lines: int,
    start: int,
    minimum: int,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(start, minimum - 1, -2):
        f = font(size)
        lines = wrap_text(draw, text, f, max_width)
        if len(lines) <= max_lines:
            return f, lines, size
    f = font(minimum)
    lines = wrap_text(draw, text, f, max_width)[:max_lines]
    if lines:
        lines[-1] = ellipsize(draw, lines[-1], f, max_width)
    return f, lines, minimum


def draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    font_obj: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    line_height: int,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += line_height
    return y


def draw_clamped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: tuple[int, int, int, int],
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
    line_gap: int = 8,
) -> int:
    font_obj, lines, size = fit_font(draw, text, max_width, max_lines, start_size, min_size)
    return draw_lines(draw, xy, lines, font_obj, fill, size + line_gap)


def source_names(card: dict[str, Any]) -> str:
    sources = card.get("sources") or []
    names = []
    for source in sources:
        if isinstance(source, dict) and source.get("name"):
            names.append(str(source["name"]))
    return ", ".join(names[:3])


def draw_card(card: dict[str, Any], index: int, total: int, config: dict[str, Any], output_path: Path) -> None:
    width = int(config["cardnews"]["image_width"])
    height = int(config["cardnews"]["image_height"])

    if TEMPLATE_PATH.exists():
        canvas = Image.open(TEMPLATE_PATH).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (width, height), (245, 249, 253, 255))

    draw = ImageDraw.Draw(canvas)

    title = str(card.get("title") or "AI 뉴스 아리아")
    summary = str(card.get("summary") or "요약 내용이 아직 없습니다.")
    aria_line = str(card.get("aria_line") or "중요한 것만 쉽게 정리해드릴게요.")
    caption = str(card.get("caption") or "AI 뉴스 큐레이터 아리아")
    importance = str(card.get("importance") or "News")
    topic = str(card.get("topic") or card.get("type") or "AI News")
    source_date = clean_day(str(card.get("source_date") or card.get("date") or date.today().isoformat()))
    created_date = clean_day(str(card.get("created_date") or card.get("date") or date.today().isoformat()))

    # Top title box.
    draw.text((84, 62), f"CARD {index:02d} / {total:02d}", font=font(25), fill=BLUE)
    draw_clamped(draw, (84, 102), title, NAVY, 650, 1, 40, 28)
    draw_clamped(draw, (862, 82), created_date, WHITE, 150, 1, 24, 18)

    # Main content panel.
    draw.text((78, 232), importance, font=font(26), fill=BLUE)
    draw_clamped(draw, (78, 286), summary, MUTED, 860, 5, 34, 24)

    bullets = [str(item) for item in (card.get("bullets") or []) if str(item).strip()]
    if bullets:
        draw.text((78, 600), "핵심 포인트", font=font(31), fill=NAVY)
        y = 658
        bullet_font = font(28)
        for bullet in bullets[:3]:
            lines = wrap_text(draw, bullet, bullet_font, 790)
            lines = lines[:2]
            draw.ellipse((86, y + 10, 100, y + 24), fill=BLUE)
            y = draw_lines(draw, (118, y), lines, bullet_font, NAVY, 39) + 18
            if y > 850:
                break

    sources = source_names(card)
    if sources:
        source_text = "출처: " + sources
        draw_clamped(draw, (78, 920), source_text, MUTED, 700, 2, 21, 17)

    meta = f"{topic} | 뉴스 기준 {source_date}"
    draw_clamped(draw, (78, 970), meta, MUTED, 700, 1, 20, 16)

    # Speech bubble area in the template.
    draw_clamped(draw, (78, 1112), aria_line, NAVY, 610, 3, 34, 23)

    # Small signature inside the lower speech area.
    draw_clamped(draw, (78, 1272), caption, MUTED, 540, 1, 22, 17)

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
        save_json(default_cards_path, data)
    elif default_cards_path.exists() and not args.sample:
        data = load_json(default_cards_path)
    else:
        data = sample_cards(args.date)
        save_json(default_cards_path, data)

    root_day = clean_day(str(data.get("date") or args.date))
    cards = data.get("cards") or []
    for idx, card in enumerate(cards, start=1):
        if isinstance(card, dict):
            card.setdefault("date", root_day)
            card.setdefault("source_date", root_day)
        draw_card(card, idx, len(cards), config, output_dir / f"card_{idx:02d}.png")

    print(f"Done: {output_dir}")


if __name__ == "__main__":
    main()
