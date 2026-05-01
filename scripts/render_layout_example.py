from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BG_PATH = ROOT / "assets" / "templates" / "ai_news_aria_layout_v1.png"
OUT_PATH = ROOT / "output" / "layout_examples" / "2026-05-01" / "ai_news_aria_layout_example_01.png"

NAVY = (17, 39, 70, 255)
BLUE = (18, 89, 150, 255)
TEXT = (25, 35, 52, 255)
MUTED = (93, 110, 132, 255)
LINE = (176, 204, 226, 230)


def pick_font(bold: bool = False) -> Path:
    repo_fonts = ROOT / "assets" / "fonts"
    candidates = [
        repo_fonts / ("Pretendard-Bold.otf" if bold else "Pretendard-Regular.otf"),
        repo_fonts / ("Pretendard-Bold.ttf" if bold else "Pretendard-Regular.ttf"),
        repo_fonts / ("Pretendard-SemiBold.otf" if bold else "Pretendard-Medium.otf"),
        repo_fonts / ("Pretendard-SemiBold.ttf" if bold else "Pretendard-Medium.ttf"),
        repo_fonts / "Pretendard-Medium.otf",
        repo_fonts / "Pretendard-Medium.ttf",
        repo_fonts / ("S-CoreDream-6Bold.otf" if bold else "S-CoreDream-4Regular.otf"),
        repo_fonts / ("SCDream6.otf" if bold else "SCDream4.otf"),
        repo_fonts / ("WantedSans-Bold.otf" if bold else "WantedSans-Regular.otf"),
        repo_fonts / ("SUIT-Bold.otf" if bold else "SUIT-Regular.otf"),
        Path("C:/Windows/Fonts/Pretendard-Bold.otf" if bold else "C:/Windows/Fonts/Pretendard-Regular.otf"),
        Path("C:/Windows/Fonts/S-CoreDream-6Bold.otf" if bold else "C:/Windows/Fonts/S-CoreDream-4Regular.otf"),
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/NotoSansKR-VF.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Korean font not found. Put a .ttf or .otf font in assets/fonts.")


def make_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(pick_font(bold)), size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue

        words = para.split(" ")
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if text_width(draw, candidate, font) <= max_width:
                line = candidate
                continue

            if line:
                lines.append(line)

            while text_width(draw, word, font) > max_width and len(word) > 1:
                cut = 1
                for i in range(1, len(word) + 1):
                    if text_width(draw, word[:i], font) <= max_width:
                        cut = i
                    else:
                        break
                lines.append(word[:cut])
                word = word[cut:]
            line = word

        if line:
            lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    max_width: int,
    line_gap: int = 8,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        box = draw.textbbox((x, y), line or "가", font=font)
        y += (box[3] - box[1]) + line_gap
    return y


def draw_news_item(
    draw: ImageDraw.ImageDraw,
    num: int,
    title: str,
    body: str,
    y: int,
    fonts: dict[str, ImageFont.FreeTypeFont],
) -> int:
    draw.rounded_rectangle((82, y, 922, y + 142), radius=18, fill=(248, 252, 255, 230), outline=LINE, width=2)
    draw.ellipse((106, y + 34, 158, y + 86), fill=(21, 93, 151, 255))
    draw.text((122, y + 42), str(num), font=fonts["body_bold"], fill=(255, 255, 255, 255))
    draw.text((178, y + 24), title, font=fonts["body_bold"], fill=NAVY)
    draw_wrapped(draw, body, (178, y + 69), fonts["body"], TEXT, 700, 6)
    return y + 166


def main() -> None:
    fonts = {
        "eyebrow": make_font(24),
        "title": make_font(50, True),
        "date": make_font(30, True),
        "section": make_font(34, True),
        "body": make_font(30),
        "body_bold": make_font(31, True),
        "small": make_font(22),
        "bubble": make_font(28, True),
    }

    image = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(image)

    draw.text((72, 62), "AI NEWS ARIA", font=fonts["eyebrow"], fill=(74, 147, 190, 255))
    draw.text((72, 96), "전날 AI 뉴스 핵심 요약", font=fonts["title"], fill=NAVY)
    draw.text((835, 104), "2026.05.01", font=fonts["date"], fill=(230, 247, 255, 255))
    draw.text((846, 145), "작성 기준", font=fonts["small"], fill=(165, 213, 232, 255))

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (70, 286, 948, 982),
        radius=24,
        fill=(255, 255, 255, 120),
        outline=(210, 230, 244, 190),
        width=2,
    )
    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (82, 318, 242, 362),
        radius=22,
        fill=(226, 247, 252, 245),
        outline=(120, 205, 226, 210),
        width=1,
    )
    draw.text((105, 325), "2026.04.30", font=fonts["small"], fill=BLUE)

    draw.text((82, 390), "오늘의 흐름", font=fonts["section"], fill=NAVY)
    draw_wrapped(
        draw,
        'AI 서비스가 "모델 성능 경쟁"을 넘어 보안, 차량, 결제, 칩 인프라까지 넓어지는 날이었습니다.',
        (82, 442),
        fonts["body"],
        TEXT,
        820,
        10,
    )

    y = 535
    news_items = [
        (
            "OpenAI, 계정 보안 강화",
            "ChatGPT와 Codex 계정에 고위험 사용자를 위한 Advanced Account Security를 도입했습니다.",
        ),
        (
            "Gemini, 차량 안으로 확장",
            "Google built-in 차량에 Gemini가 순차 적용되며 자동차 음성비서가 더 자연스러운 대화형으로 바뀝니다.",
        ),
        (
            "AI 칩 경쟁, 다변화 신호",
            "Google TPU와 Amazon Trainium처럼 자체 AI 칩을 외부 고객에게 제공하려는 움직임이 커지고 있습니다.",
        ),
    ]
    for index, (title, body) in enumerate(news_items, 1):
        y = draw_news_item(draw, index, title, body, y, fonts)

    draw.line((82, 1032, 920, 1032), fill=(190, 216, 232, 200), width=2)
    draw.text(
        (82, 1048),
        "출처 예시: OpenAI, TechCrunch, The Verge, Business Insider / 요약: AI 뉴스 아리아",
        font=fonts["small"],
        fill=MUTED,
    )

    draw_wrapped(
        draw,
        '아리아 한줄 요약: 오늘은 AI가 "더 똑똑해지는 것"보다, 어디에 들어가고 어떻게 안전하게 쓰이는지가 핵심이에요.',
        (87, 1163),
        fonts["bubble"],
        NAVY,
        670,
        12,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT_PATH, quality=95)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
