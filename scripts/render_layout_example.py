from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE_TEMPLATE = ROOT / "assets" / "templates" / "ai_news_aria_layout_v1.png"
VISUAL_TEMPLATE = ROOT / "assets" / "templates" / "ai_news_aria_layout_visual_v1.png"
OUT_PATH = ROOT / "output" / "layout_examples" / "2026-05-01" / "ai_news_aria_layout_visual_example_01.png"

NAVY = (17, 39, 70, 255)
BLUE = (18, 89, 150, 255)
CYAN = (28, 183, 220, 255)
TEXT = (25, 35, 52, 255)
MUTED = (93, 110, 132, 255)
LINE = (176, 204, 226, 230)
PANEL = (248, 252, 255, 235)


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
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        box = draw.textbbox((x, y), line or "가", font=font)
        y += (box[3] - box[1]) + line_gap
    return y


def draw_blank_visual_box(draw: ImageDraw.ImageDraw) -> None:
    draw.rounded_rectangle((612, 322, 914, 522), radius=22, fill=(244, 250, 255, 245), outline=LINE, width=2)
    draw.rounded_rectangle((632, 342, 894, 502), radius=18, fill=(255, 255, 255, 210), outline=(210, 231, 244, 190), width=1)
    for x in range(660, 875, 34):
        draw.line((x, 360, x, 485), fill=(225, 238, 247, 130), width=1)
    for y in range(370, 490, 28):
        draw.line((648, y, 880, y), fill=(225, 238, 247, 130), width=1)
    draw.rounded_rectangle((652, 454, 742, 476), radius=11, fill=(226, 247, 252, 210), outline=(160, 220, 235, 180))
    draw.rounded_rectangle((760, 454, 850, 476), radius=11, fill=(238, 244, 255, 220), outline=(188, 207, 235, 180))


def build_visual_template() -> None:
    image = Image.open(BASE_TEMPLATE).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (70, 286, 948, 982),
        radius=24,
        fill=(255, 255, 255, 115),
        outline=(210, 230, 244, 190),
        width=2,
    )
    draw_blank_visual_box(draw)
    image.alpha_composite(overlay)
    VISUAL_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(VISUAL_TEMPLATE, quality=95)


def draw_shield(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    points = [(cx, cy - 48), (cx + 48, cy - 28), (cx + 38, cy + 34), (cx, cy + 62), (cx - 38, cy + 34), (cx - 48, cy - 28)]
    draw.polygon(points, fill=(17, 86, 142, 255))
    inner = [(cx, cy - 32), (cx + 28, cy - 18), (cx + 22, cy + 24), (cx, cy + 42), (cx - 22, cy + 24), (cx - 28, cy - 18)]
    draw.polygon(inner, fill=(236, 249, 255, 255))
    draw.line((cx - 18, cy + 2, cx - 3, cy + 18, cx + 22, cy - 16), fill=CYAN, width=8, joint="curve")


def draw_chip(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    draw.rounded_rectangle((cx - 38, cy - 38, cx + 38, cy + 38), radius=10, fill=(21, 51, 88, 255))
    draw.rounded_rectangle((cx - 20, cy - 20, cx + 20, cy + 20), radius=6, outline=(130, 224, 245, 255), width=4)
    for offset in (-26, -10, 10, 26):
        draw.line((cx - 54, cy + offset, cx - 40, cy + offset), fill=(130, 224, 245, 255), width=4)
        draw.line((cx + 40, cy + offset, cx + 54, cy + offset), fill=(130, 224, 245, 255), width=4)
        draw.line((cx + offset, cy - 54, cx + offset, cy - 40), fill=(130, 224, 245, 255), width=4)
        draw.line((cx + offset, cy + 40, cx + offset, cy + 54), fill=(130, 224, 245, 255), width=4)


def draw_visual_summary(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.FreeTypeFont]) -> None:
    box = (612, 322, 914, 522)
    draw.rounded_rectangle(box, radius=22, fill=(244, 250, 255, 245), outline=LINE, width=2)
    draw.rounded_rectangle((632, 342, 894, 502), radius=18, fill=(255, 255, 255, 225), outline=(210, 231, 244, 190), width=1)
    draw.text((652, 358), "관련 비주얼", font=fonts["caption"], fill=BLUE)

    # Keep the generated fallback visual readable at Kakao thumbnail size:
    # one dominant symbol, then compact topic chips instead of overlapping icons.
    draw_chip(draw, 762, 426)
    draw.arc((690, 352, 834, 496), 205, 335, fill=(196, 230, 243, 180), width=8)
    draw.arc((710, 372, 814, 476), 205, 335, fill=(224, 242, 249, 190), width=6)
    draw.line((654, 426, 702, 426), fill=(115, 197, 222, 210), width=4)
    draw.line((822, 426, 870, 426), fill=(115, 197, 222, 210), width=4)

    chips = [("보안", 654, 468, 720), ("차량", 734, 468, 802), ("칩", 816, 468, 880)]
    for label, x1, y1, x2 in chips:
        draw.rounded_rectangle((x1, y1, x2, y1 + 24), radius=12, fill=(226, 247, 252, 245))
        label_width = text_width(draw, label, fonts["micro"])
        draw.text((x1 + ((x2 - x1) - label_width) / 2, y1 + 2), label, font=fonts["micro"], fill=BLUE)


def draw_news_item(
    draw: ImageDraw.ImageDraw,
    num: int,
    title: str,
    body: str,
    y: int,
    fonts: dict[str, ImageFont.FreeTypeFont],
) -> int:
    draw.rounded_rectangle((82, y, 922, y + 132), radius=18, fill=PANEL, outline=LINE, width=2)
    draw.ellipse((106, y + 32, 154, y + 80), fill=(21, 93, 151, 255))
    draw.text((121, y + 38), str(num), font=fonts["body_bold"], fill=(255, 255, 255, 255))
    draw.text((176, y + 22), title, font=fonts["body_bold"], fill=NAVY)
    draw_wrapped(draw, body, (176, y + 64), fonts["body"], TEXT, 705, 5, max_lines=2)
    return y + 145


def render_example() -> None:
    build_visual_template()
    fonts = {
        "eyebrow": make_font(24),
        "title": make_font(50, True),
        "date": make_font(30, True),
        "section": make_font(32, True),
        "body": make_font(26),
        "body_bold": make_font(28, True),
        "small": make_font(21),
        "bubble": make_font(27, True),
        "caption": make_font(20, True),
        "micro": make_font(16, True),
    }

    image = Image.open(VISUAL_TEMPLATE).convert("RGBA")
    draw = ImageDraw.Draw(image)

    draw.text((72, 62), "AI NEWS ARIA", font=fonts["eyebrow"], fill=(74, 147, 190, 255))
    draw.text((72, 96), "전날 AI 뉴스 핵심 요약", font=fonts["title"], fill=NAVY)
    draw.text((835, 104), "2026.05.01", font=fonts["date"], fill=(230, 247, 255, 255))
    draw.text((846, 145), "작성 기준", font=fonts["small"], fill=(165, 213, 232, 255))

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
        'AI 서비스가 "성능 경쟁"을 넘어 보안, 차량, 칩 인프라로 확장되는 흐름이 뚜렷했습니다.',
        (82, 438),
        fonts["body"],
        TEXT,
        500,
        8,
        max_lines=3,
    )
    draw_visual_summary(draw, fonts)

    y = 555
    news_items = [
        (
            "OpenAI, 계정 보안 강화",
            "ChatGPT와 Codex 계정에 고위험 사용자를 위한 추가 보안 기능을 도입했습니다.",
        ),
        (
            "Gemini, 차량 안으로 확장",
            "Google built-in 차량에 Gemini가 적용되며 음성비서가 대화형 AI에 가까워졌습니다.",
        ),
        (
            "AI 칩 경쟁, 다변화 신호",
            "Google TPU와 Amazon Trainium처럼 자체 AI 칩을 외부 고객에게 제공하려는 움직임입니다.",
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
        '아리아 한줄 요약: 오늘은 "AI가 어디에 들어가고, 어떻게 안전하게 쓰이는가"가 핵심이에요.',
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
    render_example()
