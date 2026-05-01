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


def clean_day(value: str) -> str:
    text = str(value)
    return text[:10] if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-" else text


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


def draw_soft_shadow(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int) -> None:
    x1, y1, x2, y2 = box
    for offset, alpha in [(14, 24), (8, 30), (4, 38)]:
        draw.rounded_rectangle(
            (x1 + offset, y1 + offset, x2 + offset, y2 + offset),
            radius=radius,
            fill=(24, 55, 94, alpha),
        )


def draw_card(card: dict[str, Any], index: int, total: int, config: dict[str, Any], output_path: Path) -> None:
    width = int(config["cardnews"]["image_width"])
    height = int(config["cardnews"]["image_height"])
    reference_path = PROJECT_ROOT / config["cardnews"]["character_reference"]

    canvas = Image.new("RGBA", (width, height), (244, 248, 252, 255))
    draw = ImageDraw.Draw(canvas)

    # Editorial, clean base background.
    for y in range(height):
        ratio = y / height
        r = int(247 * (1 - ratio) + 232 * ratio)
        g = int(250 * (1 - ratio) + 241 * ratio)
        b = int(253 * (1 - ratio) + 249 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    draw.rounded_rectangle((-70, 220, 470, 760), radius=80, fill=(214, 235, 250, 105))
    draw.rounded_rectangle((680, 138, 1200, 720), radius=90, fill=(208, 230, 247, 120))
    draw.rounded_rectangle((560, 760, 1170, 1430), radius=100, fill=(225, 237, 244, 165))

    grid_color = (182, 205, 225, 65)
    for x in range(60, width, 120):
        draw.line([(x, 170), (x, height - 70)], fill=grid_color, width=1)
    for y in range(190, height, 120):
        draw.line([(40, y), (width - 40, y)], fill=grid_color, width=1)

    # Right visual stage for Aria, so the template looks intentional even with fixed art.
    stage = (630, 156, 1032, 1094)
    draw_soft_shadow(draw, stage, 38)
    draw.rounded_rectangle(stage, radius=38, fill=(239, 247, 253, 232), outline=(185, 214, 236), width=2)

    paste_character(canvas, reference_path, width, height)
    draw = ImageDraw.Draw(canvas)

    navy = (12, 38, 82)
    deep = (9, 26, 54)
    blue = (0, 132, 204)
    cyan = (0, 178, 218)
    gold = (242, 181, 44)
    gray = (74, 88, 112)
    muted = (101, 116, 138)
    white = (255, 255, 255)
    panel_border = (180, 209, 232)

    meta_font = font(26, bold=True)
    date_font = font(24, bold=True)
    card_no_font = font(58, bold=True)
    title_font = font(50, bold=True)
    body_font = font(34)
    speech_font = font(34, bold=True)
    small_font = font(27)
    source_font = font(24)
    label_font = font(24, bold=True)
    bullet_font = font(29, bold=True)

    created_date = clean_day(str(card.get("created_date") or card.get("date") or date.today().isoformat()))
    source_date = clean_day(str(card.get("source_date") or created_date))
    topic = str(card.get("topic") or card.get("type") or "AI News")
    title = str(card.get("title") or "AI 뉴스 아리아")
    summary = str(card.get("summary") or "요약 내용이 아직 없습니다.")
    aria_line = str(card.get("aria_line") or "핵심만 차분하게 정리해볼게요.")
    caption = str(card.get("caption") or "AI 뉴스 큐레이터 아리아")
    importance = str(card.get("importance") or "뉴스")

    # Top editorial header.
    header = (42, 40, width - 42, 176)
    draw_soft_shadow(draw, header, 28)
    draw.rounded_rectangle(header, radius=28, fill=(14, 36, 74, 248))
    draw.rounded_rectangle((42, 40, 70, 176), radius=14, fill=cyan)
    number_box = (90, 68, 164, 148)
    draw.rounded_rectangle(number_box, radius=18, fill=(255, 255, 255, 255), outline=(111, 189, 237), width=3)
    no_bbox = draw.textbbox((0, 0), str(index), font=card_no_font)
    draw.text(
        (number_box[0] + 37 - (no_bbox[2] - no_bbox[0]) // 2, number_box[1] + 35 - (no_bbox[3] - no_bbox[1]) // 2),
        str(index),
        font=card_no_font,
        fill=navy,
    )
    draw.text((188, 66), "AI NEWS ARIA", font=label_font, fill=(142, 218, 255))
    draw_wrapped(draw, (188, 96), title, title_font, white, 540, 58, 1)
    draw_badge(
        draw,
        (770, 72, 1016, 143),
        f"작성 {created_date}",
        date_font,
        (255, 255, 255, 250),
        (146, 198, 233),
        navy,
    )

    # Main information board.
    panel = (66, 228, 620, 940)
    draw_soft_shadow(draw, panel, 30)
    draw.rounded_rectangle(panel, radius=30, fill=(255, 255, 255, 248), outline=panel_border, width=2)
    draw.rounded_rectangle((66, 228, 620, 300), radius=30, fill=(239, 248, 255, 255))
    draw.rectangle((66, 266, 620, 300), fill=(239, 248, 255, 255))
    draw.text((98, 250), topic, font=label_font, fill=blue)
    draw_badge(draw, (420, 244, 578, 288), importance, meta_font, (255, 248, 224, 255), gold, navy)
    draw.text((98, 334), "핵심 요약", font=label_font, fill=navy)
    y_after_summary = draw_wrapped(draw, (98, 382), summary, body_font, gray, 474, 48, 4)

    bullets = card.get("bullets") or []
    if not bullets:
        bullets = [caption, "출처 확인", "내일 흐름 체크"]
    draw.text((98, max(574, y_after_summary + 34)), "오늘 볼 포인트", font=label_font, fill=navy)
    bullet_y = max(624, y_after_summary + 82)
    for bullet in [str(item) for item in bullets[:3]]:
        row = (98, bullet_y - 8, 584, bullet_y + 42)
        draw.rounded_rectangle(row, radius=16, fill=(245, 249, 252, 255), outline=(220, 232, 240), width=1)
        draw.rounded_rectangle((118, bullet_y + 5, 138, bullet_y + 25), radius=6, fill=cyan)
        draw.text((154, bullet_y - 1), bullet, font=bullet_font, fill=navy)
        bullet_y += 62

    # Source/date strip.
    strip = (96, 824, 590, 886)
    draw.rounded_rectangle(strip, radius=18, fill=(235, 244, 253, 255), outline=(187, 211, 232), width=1)
    draw.text((126, 842), f"뉴스 기준일  {source_date}", font=small_font, fill=navy)

    # Speech bubble from Aria.
    speech_box = (404, 886, 1014, 1162)
    draw_soft_shadow(draw, speech_box, 34)
    draw.rounded_rectangle(speech_box, radius=32, fill=white, outline=navy, width=4)
    tail = [(735, 888), (814, 842), (796, 908)]
    draw.polygon(tail, fill=white, outline=navy)
    draw.line([tail[0], tail[1], tail[2]], fill=navy, width=4)
    draw.text((456, 922), "ARIA COMMENT", font=label_font, fill=blue)
    draw_wrapped(draw, (456, 972), aria_line, speech_font, navy, 500, 49, 3)

    sources = card.get("sources") or []
    names = [str(source.get("name")) for source in sources if isinstance(source, dict) and source.get("name")]
    if names:
        draw_wrapped(draw, (78, 972), "출처: " + ", ".join(names), source_font, muted, 310, 34, 3)

    footer = (66, 1202, 1014, 1284)
    draw.rounded_rectangle(footer, radius=24, fill=(9, 32, 70, 238))
    draw.text((100, 1228), caption, font=small_font, fill=white)
    draw.text((842, 1228), f"{index:02d}/{total:02d}", font=small_font, fill=(151, 219, 255))

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
