#!/usr/bin/env python3
"""Render a one-page newspaper front page for 24 November 2026.

Every picture element is drawn with Pillow shapes. No photo, no
downloaded picture, no face. The four stories below were checked
against the Reuters world-news summary for Tuesday 24 November
2026; anything not confirmed there is left out, not guessed.
"""

import os
from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
EDGE = 46
PAPER = (247, 243, 232)
INK = (17, 17, 17)
SOFT = (72, 72, 66)
RULE = (30, 30, 30)
RED = (139, 26, 26)
NAVY = (31, 58, 86)
SEA = (38, 74, 104)
SAND = (232, 222, 196)
PALE = (214, 226, 232)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def fit_words(text, font, width):
    """Split text into lines that fit `width`, measured with `font`."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if font.getlength(trial) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(draw, x, y, width, text, font, colour=INK, gap=6):
    """Draw wrapped text, return the y just below the last line."""
    rows = fit_words(text, font, width)
    step = font.size + gap
    for row in rows:
        draw.text((x, y), row, font=font, fill=colour)
        y += step
    return y


def block_height(text, font, width, gap=6):
    rows = fit_words(text, font, width)
    return len(rows) * (font.size + gap) - gap


def centred(draw, y, text, font, colour=INK):
    wide = font.getlength(text)
    draw.text(((PAGE - wide) / 2, y), text, font=font, fill=colour)
    return y + font.size + 4


def rule(draw, y, weight=2):
    draw.line([(EDGE, y), (PAGE - EDGE, y)], fill=RULE, width=weight)
    return y + weight


# --- stories, as reported on 24 November 2026 -------------------------

LEAD = {
    "kicker": "UKRAINE  •  GULF OF FINLAND",
    "head": "Zelenskiy confirms Ukraine hit Russian ship in Gulf of Finland",
    "body": (
        "President Volodymyr Zelenskiy confirmed on Tuesday that Ukraine "
        "was behind a drone strike on a Russian cargo ship in the Gulf of "
        "Finland. Norway, a strong supporter of Kyiv, urged caution in "
        "such operations."
    ),
    "source": "Source: Reuters — World News Summary, 24 November 2026",
}

SECOND = {
    "kicker": "GAZA",
    "head": "Israeli strike kills Hamas security chief in Gaza",
    "body": (
        "An Israeli airstrike in Gaza killed Naeem Abu Nahel, the director "
        "of Hamas' internal security apparatus, and six others, including "
        "two police officers, medics and police said on Tuesday."
    ),
    "source": "Source: Reuters, 24 November 2026",
}

THIRD = {
    "kicker": "UKRAINE  •  ZAPORIZHZHIA",
    "head": "Russian attack kills two in Zaporizhzhia",
    "body": (
        "An overnight Russian attack on the city of Zaporizhzhia killed two "
        "people and wounded 40 others, including four children, regional "
        "governor Mykhailo Semikin said on Tuesday. The attack struck an "
        "apartment building."
    ),
    "source": "Source: Reuters, 24 November 2026",
}

FOURTH = {
    "kicker": "YEMEN  •  ADEN",
    "head": "Houthis 60 km from Aden, Yemeni forces say city will hold",
    "body": (
        "Yemen's Houthis have pushed to within 60 km of Aden, the temporary "
        "capital of the internationally recognised government, Yemen's "
        "military said on Tuesday. The military said the Houthis will not "
        "capture the city."
    ),
    "source": "Source: Reuters, 24 November 2026",
}


# --- small drawn pictures ----------------------------------------------

def sea_picture(draw, x, y, w, h):
    """Sky, a dark sea band, a cargo ship silhouette, three dots above."""
    draw.rectangle([x, y, x + w, y + h], fill=PALE, outline=INK, width=2)
    sea_top = y + int(h * 0.35)
    draw.rectangle([x, sea_top, x + w, y + h], fill=SEA)
    for i in range(5):
        wx = x + 30 + i * 170
        draw.arc([wx, sea_top + 18, wx + 90, sea_top + 46], 180, 360, fill=(240, 240, 235), width=3)
    hull_y = sea_top + 8
    draw.rectangle([x + 300, hull_y, x + 640, hull_y + 34], fill=INK)
    draw.rectangle([x + 340, hull_y - 34, x + 420, hull_y], fill=INK)
    draw.rectangle([x + 460, hull_y - 22, x + 560, hull_y], fill=(120, 30, 30))
    for cx in (330, 480, 620):
        draw.ellipse([x + cx, y + 22, x + cx + 9, y + 31], fill=INK)


def town_picture(draw, x, y, w, h):
    """A street of plain blocks, no people, no faces."""
    draw.rectangle([x, y, x + w, y + h], fill=SAND, outline=INK, width=2)
    base = y + h - 8
    blocks = [(18, 58, 62), (96, 92, 44), (156, 74, 58), (230, 100, 40),
              (286, 66, 56), (356, 88, 46)]
    for bx, bh, bw in blocks:
        draw.rectangle([x + bx, base - bh, x + bx + bw, base], fill=NAVY, outline=INK, width=1)
        for wy in range(base - bh + 8, base - 6, 16):
            for wx in range(bx + 7, bx + bw - 6, 14):
                draw.rectangle([x + wx, wy, x + wx + 6, wy + 8], fill=(247, 243, 232))


def map_picture(draw, x, y, w, h):
    """A plain coastline sketch, all points scaled to its own width."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 236, 224), outline=INK, width=2)
    draw.rectangle([x, y, x + int(w * 0.62), y + h], fill=SAND)
    frac = [(0.16, 0.12), (0.30, 0.28), (0.40, 0.55),
            (0.52, 0.58), (0.58, 0.85), (0.62, 0.92)]
    pts = [(x + int(fx * w), y + int(fy * h)) for fx, fy in frac]
    draw.line(pts, fill=NAVY, width=4)
    ax, ay = x + int(0.46 * w), y + int(0.52 * h)
    draw.ellipse([ax, ay, ax + 14, ay + 14], fill=RED, outline=INK, width=2)
    draw.text((ax + 20, ay - 2), "ADEN", font=load(SANS_B, 18), fill=INK)
    draw.line([(x + 14, y + 22), (ax, ay + 7)], fill=RED, width=2)
    draw.text((x + 14, y + 28), "60 km", font=load(SANS_B, 16), fill=RED)
    draw.text((x + int(0.72 * w), y + 12), "SEA", font=load(SANS, 16), fill=NAVY)


# --- page assembly -------------------------------------------------------

def story_block(draw, x, y, width, story, head_size, body_size):
    """Kicker + headline + body + source, stacked, returns bottom y."""
    y = block(draw, x, y, width, story["kicker"], load(SANS_B, 18), colour=RED, gap=4)
    y += 4
    y = block(draw, x, y, width, story["head"], load(SERIF_B, head_size), gap=4)
    y += 6
    y = block(draw, x, y, width, story["body"], load(SANS, body_size), gap=5)
    y += 6
    y = block(draw, x, y, width, story["source"], load(SANS, 15), colour=SOFT, gap=4)
    return y


def build():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    wide = PAGE - 2 * EDGE

    y = 22
    y = centred(draw, y, "THE WORLD LEDGER", load(SERIF_B, 48))
    y = centred(draw, y + 2, "TUESDAY,  24 NOVEMBER 2026  •  FOUR STORIES  •  SOURCES NAMED BELOW",
                load(SANS, 15), colour=SOFT)
    y = rule(draw, y + 6, 4)
    y += 8

    y = story_block(draw, EDGE, y, wide, LEAD, 32, 19)
    y += 8
    sea_picture(draw, EDGE, y, wide, 96)
    y += 96 + 8
    y = rule(draw, y, 2)
    y += 8

    col_w = (wide - 24) // 2
    left_top = y
    right_top = y
    left_bottom = story_block(draw, EDGE, left_top, col_w, SECOND, 24, 18)
    right_bottom = story_block(draw, EDGE + col_w + 24, right_top, col_w, THIRD, 24, 18)
    pic_y = max(left_bottom, right_bottom) + 8
    town_picture(draw, EDGE, pic_y, col_w, 78)
    # Right-hand panel: two plain bars for the two reported figures.
    rx = EDGE + col_w + 24
    draw.rectangle([rx, pic_y, rx + col_w, pic_y + 78], fill=SAND, outline=INK, width=2)
    draw.text((rx + 12, pic_y + 8), "KILLED  2", font=load(SANS_B, 16), fill=INK)
    draw.rectangle([rx + 12, pic_y + 28, rx + 28, pic_y + 40], fill=RED)
    draw.text((rx + 12, pic_y + 46), "WOUNDED  40", font=load(SANS_B, 16), fill=INK)
    draw.rectangle([rx + 12, pic_y + 64, rx + 220, pic_y + 74], fill=NAVY)
    y = pic_y + 78 + 8
    y = rule(draw, y, 2)
    y += 8

    y = block(draw, EDGE, y, wide, FOURTH["kicker"], load(SANS_B, 17), colour=RED, gap=4)
    y += 4
    head_end = block(draw, EDGE, y, wide, FOURTH["head"], load(SERIF_B, 26), gap=4)
    y = head_end + 6
    body_end = block(draw, EDGE, y, 560, FOURTH["body"], load(SANS, 18), gap=5)
    body_end += 6
    body_end = block(draw, EDGE, body_end, 560, FOURTH["source"], load(SANS, 14), colour=SOFT, gap=4)
    map_picture(draw, EDGE + 584, y - 6, wide - 584, 96)
    y = max(body_end, y + 96) + 8
    y = rule(draw, y, 2)
    y += 8
    centred(draw, y, "All four stories are dated 24 November 2026. Unconfirmed details are omitted.",
            load(SANS, 15), colour=SOFT)
    centred(draw, y + 20, "Drawn entirely with shapes — no photographs, no faces.  •  Page 1",
            load(SANS, 15), colour=SOFT)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    picture = build()
    path = os.path.join(out_dir, "entry.png")
    picture.save(path, format="PNG")
    with open(path, "rb") as handle:
        data = handle.read()
    check = Image.open(path)
    assert check.size == (1024, 1024), check.size
    assert len(data) > 0
    print(f"wrote {path} ({len(data)} bytes, {check.size[0]}x{check.size[1]})")


if __name__ == "__main__":
    main()
