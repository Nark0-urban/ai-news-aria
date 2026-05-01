# -*- coding: utf-8 -*-
"""Render AI News Aria cardnews PNG files from cards.json.

This renderer uses existing character assets plus text/layout templates.
It does not call any paid image generation API.
"""

from __future__ import annotations

import argparse
import json
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
                "topic": "Daily Brief",
                "source_date": day,
                "bullets": ["제품 업데이트", "연구/논문", "정책과 커뮤니티 반응"],
                "sources": [],
            },
            {
                "type": "news",
                "title": "제품 업데이트",
                "summary": "새 모델, 새 기능, 가격 정책 변화처럼 실사용에 영향을 주는 소식을 우선 확인합니다.",
                "aria_line": "업데이트는 기능보다 내 작업이 어떻게 달라지나를 보면 쉬워요.",
                "caption": "실무 영향 중심으로 보기",
                "importance": "중요",
                "topic": "Product Update",
                "source_date": day,
                "bullets": ["새 기능과 모델 변화", "가격/정책 영향", "실무 적용 포인트"],
                "sources": [{"name": "출처 예시", "url": "https://example.com"}],
            },
            {
                "type": "point",
                "title": "오늘 주목할 포인트",
                "summary": "반복해서 등장하는 키워드를 모아 내일 확인할 흐름을 정합니다.",
                "aria_line": "뉴스는 하루치만 보면 점이고, 며칠 묶어 보면 방향이 보여요.",
                "caption": "내일 다시 볼 키워드",
                "importance": "체크",
                "topic": "Watch Point",
                "source_date": day,
                "bullets": ["반복 키워드", "개발자 관점", "내일 확인할 흐름"],
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
    # Keep Aria as the side commentator and crop out most of the old text panels.
    crop_left = int(ref.width * 0.43)
    crop_top = int(ref.height * 0.10)
    ref = ref.crop((crop_left, crop_top, ref.width, ref.height))
    target_w = 520
    target_h = int(ref.height * (target_w / ref.width))
    ref = ref.resize((target_w, target_h), Image.Resampling.LANCZOS)
    x = width - target_w + 18
    y = height - target_h + 85

    fade = Image.new("RGBA", ref.size, (255, 255, 255, 0))
    ref = Image.blend(ref, fade, 0.02)
    canvas.alpha_composite(ref, (x, y))


def draw_badge(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font_obj: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int],
    text_fill: tuple[int, int, int],
) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=3)
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    x = box[0] + ((box[2] - box[0]) - (bbox[2] - bbox[0])) // 2
    y = box[1] + ((box[3] - box[1]) - (bbox[3] - bbox[1])) // 2 - 2
    draw.text((x, y), text, font=font_obj, fill=text_fill)


def draw_card(card: dict[str, Any], index: int, total: int, config: dict[str, Any], output_path: Path) -> None:
    width = int(config["cardnews"]["image_width"])
    height = int(config["cardnews"]["image_height"])
    reference_path = PROJECT_ROOT / config["cardnews"]["character_reference"]

    canvas = Image.new("RGBA", (width, height), (232, 244, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for y in range(height):
        ratio = y / height
        r = int(248 * (1 - ratio) + 225 * ratio)
        g = int(252 * (1 - ratio) + 238 * ratio)
        b = int(255 * (1 - ratio) + 248 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Soft newsroom grid, kept quiet so it reads as a cardnews background.
    grid_color = (190, 215, 238, 90)
    for x in range(0, width, 90):
        draw.line([(x, 150), (x, height)], fill=grid_color, width=1)
    for y in range(170, height, 90):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    paste_character(canvas, reference_path, width, height)
    draw = ImageDraw.Draw(canvas)

    navy = (12, 38, 82)
    deep = (9, 26, 54)
    blue = (0, 166, 230)
    gold = (247, 183, 38)
    gray = (74, 88, 112)
    white = (255, 255, 255)
    panel_border = (26, 66, 118)

    meta_font = font(28, bold=True)
    date_font = font(24, bold=True)
    card_no_font = font(74, bold=True)
    title_font = font(52, bold=True)
    body_font = font(36)
    speech_font = font(36, bold=True)
    small_font = font(28)
    source_font = font(24)
    label_font = font(24, bold=True)
    bullet_font = font(31, bold=True)

    created_date = str(card.get("created_date") or card.get("date") or date.today().isoformat())
    source_date = str(card.get("source_date") or created_date)
    topic = str(card.get("topic") or card.get("type") or "AI News")
    title = str(card.get("title") or "AI 뉴스 아리아")
    summary = str(card.get("summary") or "요약 내용이 아직 없습니다.")
    aria_line = str(card.get("aria_line") or "핵심만 차분하게 정리해볼게요.")
    caption = str(card.get("caption") or "AI 뉴스 큐레이터 아리아")
    importance = str(card.get("importance") or "뉴스")

    # Top headline bar.
    header = (28, 26, width - 28, 166)
    draw.rounded_rectangle(header, radius=24, fill=(20, 41, 78, 245), outline=(95, 163, 216), width=3)
    number_box = (52, 48, 142, 144)
    draw.rounded_rectangle(number_box, radius=18, fill=(255, 255, 255, 245), outline=gold, width=4)
    no_bbox = draw.textbbox((0, 0), str(index), font=card_no_font)
    draw.text(
        (number_box[0] + 45 - (no_bbox[2] - no_bbox[0]) // 2, number_box[1] + 42 - (no_bbox[3] - no_bbox[1]) // 2),
        str(index),
        font=card_no_font,
        fill=navy,
    )
    draw_wrapped(draw, (166, 50), title, title_font, white, 575, 62, 2)
    draw_badge(
        draw,
        (766, 52, 1032, 139),
        f"작성 {created_date}",
        date_font,
        (255, 255, 255, 245),
        (95, 163, 216),
        navy,
    )

    # Main information board.
    panel = (54, 202, 676, 902)
    draw.rounded_rectangle(panel, radius=26, fill=(255, 255, 255, 242), outline=panel_border, width=4)
    draw.text((86, 234), topic, font=label_font, fill=blue)
    draw_badge(draw, (438, 224, 632, 282), importance, meta_font, (255, 247, 224, 255), gold, navy)
    draw.text((86, 312), "핵심 요약", font=label_font, fill=navy)
    y_after_summary = draw_wrapped(draw, (86, 356), summary, body_font, gray, 536, 50, 4)

    bullets = card.get("bullets") or []
    if not bullets:
        bullets = [caption, "출처 확인", "내일 흐름 체크"]
    draw.text((86, max(545, y_after_summary + 34)), "오늘 볼 포인트", font=label_font, fill=navy)
    bullet_y = max(594, y_after_summary + 82)
    for bullet in [str(item) for item in bullets[:3]]:
        draw.rounded_rectangle((92, bullet_y + 4, 118, bullet_y + 30), radius=7, fill=blue)
        draw.text((132, bullet_y), bullet, font=bullet_font, fill=navy)
        bullet_y += 60

    # Source/date strip.
    strip = (74, 802, 652, 872)
    draw.rounded_rectangle(strip, radius=18, fill=(235, 244, 253, 255), outline=(187, 211, 232), width=2)
    draw.text((104, 822), f"뉴스 기준일  {source_date}", font=small_font, fill=navy)

    # Speech bubble from Aria.
    speech_box = (410, 888, 1018, 1156)
    draw.rounded_rectangle(speech_box, radius=32, fill=white, outline=navy, width=4)
    tail = [(735, 888), (814, 842), (796, 908)]
    draw.polygon(tail, fill=white, outline=navy)
    draw.line([tail[0], tail[1], tail[2]], fill=navy, width=4)
    draw_wrapped(draw, (456, 934), aria_line, speech_font, navy, 500, 52, 4)

    sources = card.get("sources") or []
    names = [str(source.get("name")) for source in sources if isinstance(source, dict) and source.get("name")]
    if names:
        draw_wrapped(draw, (70, 930), "출처: " + ", ".join(names), source_font, gray, 330, 34, 3)

    footer = (54, 1194, 1026, 1286)
    draw.rounded_rectangle(footer, radius=22, fill=(9, 32, 70, 235))
    draw.text((86, 1224), caption, font=small_font, fill=white)
    draw.text((836, 1224), f"{index:02d}/{total:02d}", font=small_font, fill=(151, 219, 255))

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
