"""The Day's World -- Tuesday 24 November 2026, as a newspaper front page.

One day of real world news, drawn as a single 1024x1024 front page.
Pure Python 3 standard library: the page is painted pixel by pixel
into an RGB buffer and encoded as a PNG with zlib. No network calls,
no font files, no randomness -- run it twice and the bytes match.

The letterforms are a small mixed-case bitmap face made for this page,
seven pixels wide and nine tall, with serifs on the stems so it reads
like newspaper type. Lowercase letters sit on a five-row x-height with
their own ascenders and descenders. The zero is a plain oval.
"""

import os
import struct
import sys
import zlib
from pathlib import Path

PAGE_W = 1024
PAGE_H = 1024

PAPER_RGB = (252, 250, 244)
INK_RGB = (16, 16, 16)
GREY_RGB = (74, 74, 74)
RED_RGB = (178, 24, 24)
BLUE_RGB = (20, 60, 110)
TEAL_RGB = (12, 104, 96)
GREEN_RGB = (20, 112, 54)
AMBER_RGB = (166, 98, 0)
SKY_RGB = (196, 222, 235)
GRASS_RGB = (120, 178, 96)
SAND_RGB = (232, 214, 176)
RULE_RGB = (16, 16, 16)
PALE_RGB = (200, 192, 172)

# Each glyph is nine rows of seven characters, "#" for ink, "." for paper.
GLYPHS = {
"A": (".###...", "#...#..", "#.....#", "#.....#", "#######", "#.....#",
      "#.....#", "#.....#", "#.....#"),
"B": ("######.", "#.....#", "#.....#", "######.", "#.....#", "#.....#",
      "#.....#", "#.....#", "######."),
"C": (".#####.", "#.....#", "#......", "#......", "#......", "#......",
      "#......", "#.....#", ".#####."),
"D": ("#####..", "#....#.", "#.....#", "#.....#", "#.....#", "#.....#",
      "#.....#", "#....#.", "#####.."),
"E": ("#######", "#......", "#......", "#......", "#####..", "#......",
      "#......", "#......", "#######"),
"F": ("#######", "#......", "#......", "#......", "#####..", "#......",
      "#......", "#......", "#......"),
"G": (".#####.", "#.....#", "#......", "#......", "#..####", "#.....#",
      "#.....#", "#.....#", ".#####."),
"H": ("#.....#", "#.....#", "#.....#", "#.....#", "#######", "#.....#",
      "#.....#", "#.....#", "#.....#"),
"I": (".#####.", "...#...", "...#...", "...#...", "...#...", "...#...",
      "...#...", "...#...", ".#####."),
"J": ("....###", "......#", "......#", "......#", "......#", "......#",
      "#.....#", "#.....#", ".#####."),
"K": ("#.....#", "#....#.", "#...#..", "#..#...", "###....", "#..#...",
      "#...#..", "#....#.", "#.....#"),
"L": ("#......", "#......", "#......", "#......", "#......", "#......",
      "#......", "#......", "#######"),
"M": ("#.....#", "##...##", "#.#.#.#", "#.#.#.#", "#..#..#", "#.....#",
      "#.....#", "#.....#", "#.....#"),
"N": ("#.....#", "##....#", "#.#...#", "#..#..#", "#...#.#", "#....##",
      "#.....#", "#.....#", "#.....#"),
"O": (".#####.", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
      "#.....#", "#.....#", ".#####."),
"P": ("######.", "#.....#", "#.....#", "#.....#", "######.", "#......",
      "#......", "#......", "#......"),
"Q": (".#####.", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
      "#.....#", "#..#..#", ".##.##."),
"R": ("######.", "#.....#", "#.....#", "#.....#", "######.", "#..#...",
      "#...#..", "#....#.", "#.....#"),
"S": (".#####.", "#.....#", "#......", "#......", ".#####.", "......#",
      "......#", "#.....#", ".#####."),
"T": ("#######", "...#...", "...#...", "...#...", "...#...", "...#...",
      "...#...", "...#...", "...#..."),
"U": ("#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
      "#.....#", "#.....#", ".#####."),
"V": ("#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
      ".#...#.", "..#.#..", "...#..."),
"W": ("#.....#", "#.....#", "#.....#", "#.....#", "#..#..#", "#.#.#.#",
      "#.#.#.#", "##...##", "#.....#"),
"X": ("#.....#", ".#...#.", "..#.#..", "...#...", "...#...", "..#.#..",
      ".#...#.", "#.....#", "#.....#"),
"Y": ("#.....#", "#.....#", ".#...#.", "..#.#..", "...#...", "...#...",
      "...#...", "...#...", "...#..."),
"Z": ("#######", "......#", ".....#.", "....#..", "...#...", "..#....",
      ".#.....", "#......", "#######"),
"a": (".......", ".......", ".......", ".####..", ".....#.", ".#####.",
      "#....#.", "#....#.", ".####.."),
"b": ("#......", "#......", "#......", "####...", "#...#..", "#...#..",
      "#...#..", "#...#..", "####..."),
"c": (".......", ".......", ".......", ".####..", "#....#.", "#......",
      "#......", "#....#.", ".####.."),
"d": (".....#.", ".....#.", ".....#.", ".####..", "#....#.", "#....#.",
      "#....#.", "#....#.", ".####.."),
"e": (".......", ".......", ".......", ".####..", "#....#.", "######.",
      "#......", "#....#.", ".####.."),
"f": ("..###..", ".#.....", ".#.....", "#####..", ".#.....", ".#.....",
      ".#.....", ".#.....", ".#....."),
"g": (".......", ".......", ".......", ".####..", "#....#.", "#....#.",
      ".####..", "....#..", ".###..."),
"h": ("#......", "#......", "#......", "####...", "#...#..", "#...#..",
      "#...#..", "#...#..", "#...#.."),
"i": (".......", ".##....", ".......", ".#.....", ".#.....", ".#.....",
      ".#.....", ".#.....", "###...."),
"j": (".......", "....#..", ".......", "....#..", "....#..", "....#..",
      "....#..", "#...#..", ".###..."),
"k": ("#......", "#......", "#......", "#...#..", "#..#...", "###....",
      "#..#...", "#...#..", "#....#."),
"l": (".##....", ".#.....", ".#.....", ".#.....", ".#.....", ".#.....",
      ".#.....", ".#.....", "###...."),
"m": (".......", ".......", ".......", "##.##..", "#.#.#..", "#.#.#..",
      "#.#.#..", "#.#.#..", "#.#.#.."),
"n": (".......", ".......", ".......", "####...", "#...#..", "#...#..",
      "#...#..", "#...#..", "#...#.."),
"o": (".......", ".......", ".......", ".####..", "#....#.", "#....#.",
      "#....#.", "#....#.", ".####.."),
"p": (".......", ".......", ".......", "####...", "#...#..", "#...#..",
      "####...", "#......", "#......"),
"q": (".......", ".......", ".......", ".####..", "#....#.", "#....#.",
      "#....#.", ".####..", ".....#."),
"r": (".......", ".......", ".......", "#.###..", "##..#..", "#......",
      "#......", "#......", "#......"),
"s": (".......", ".......", ".......", ".####..", "#....#.", "#......",
      ".####..", ".....#.", ".####.."),
"t": (".#.....", ".#.....", ".#.....", "#####..", ".#.....", ".#.....",
      ".#.....", ".#.....", ".##...."),
"u": (".......", ".......", ".......", "#...#..", "#...#..", "#...#..",
      "#...#..", "#...#..", ".####.."),
"v": (".......", ".......", ".......", "#...#..", "#...#..", "#...#..",
      "#...#..", ".#.#...", "..#...."),
"w": (".......", ".......", ".......", "#...#..", "#...#..", "#.#.#..",
      "#.#.#..", "#.#.#..", ".#.#..."),
"x": (".......", ".......", ".......", "#...#..", ".#.#...", "..#....",
      "..#....", ".#.#...", "#...#.."),
"y": (".......", ".......", ".......", "#...#..", "#...#..", "#...#..",
      ".####..", "....#..", ".###..."),
"z": (".......", ".......", ".......", "######.", "....#..", "...#...",
      "..#....", ".#.....", "######."),
}

GLYPHS.update({
"0": (".#####.", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
      "#.....#", "#.....#", ".#####."),
"1": ("...#...", "..##...", "...#...", "...#...", "...#...", "...#...",
      "...#...", "...#...", ".#####."),
"2": (".#####.", "#.....#", "......#", "......#", ".#####.", "#......",
      "#......", "#......", "#######"),
"3": (".#####.", "#.....#", "......#", "......#", ".#####.", "......#",
      "......#", "#.....#", ".#####."),
"4": ("#....#.", "#....#.", "#....#.", "#....#.", "#######", ".....#.",
      ".....#.", ".....#.", ".....#."),
"5": ("#######", "#......", "#......", "######.", "......#", "......#",
      "......#", "#.....#", ".#####."),
"6": (".#####.", "#.....#", "#......", "#......", "######.", "#.....#",
      "#.....#", "#.....#", ".#####."),
"7": ("#######", "......#", ".....#.", "....#..", "...#...", "...#...",
      "...#...", "...#...", "...#..."),
"8": (".#####.", "#.....#", "#.....#", ".#####.", "#.....#", "#.....#",
      "#.....#", "#.....#", ".#####."),
"9": (".#####.", "#.....#", "#.....#", "#.....#", ".######", "......#",
      "......#", "#.....#", ".#####."),
" ": (".......", ".......", ".......", ".......", ".......", ".......",
      ".......", ".......", "......."),
".": (".......", ".......", ".......", ".......", ".......", ".......",
      ".......", "..##...", "..##..."),
",": (".......", ".......", ".......", ".......", ".......", ".......",
      ".......", "..##...", "..#...."),
":": (".......", ".......", ".......", "..##...", "..##...", ".......",
      ".......", "..##...", "..##..."),
";": (".......", ".......", ".......", "..##...", "..##...", ".......",
      ".......", "..##...", "..#...."),
"-": (".......", ".......", ".......", ".......", ".......", ".#####.",
      ".......", ".......", "......."),
"–": (".......", ".......", ".......", ".......", ".......", "######.",
      ".......", ".......", "......."),
"—": (".......", ".......", ".......", ".......", ".......", "#######",
      ".......", ".......", "......."),
"(": ("...#...", "..#....", ".#.....", ".#.....", ".#.....", ".#.....",
      ".#.....", "..#....", "...#..."),
")": ("...#...", "....#..", ".....#.", ".....#.", ".....#.", ".....#.",
      ".....#.", "....#..", "...#..."),
"/": (".....#.", "....#..", "...#...", "...#...", "..#....", "..#....",
      ".#.....", ".#.....", "#......"),
"%": ("#.#....", "#.#....", "...#...", "..#....", "..#....", ".#.....",
      "....#.#", "....#.#", "......."),
"!": ("..#....", "..#....", "..#....", "..#....", "..#....", "..#....",
      ".......", "..##...", "..##..."),
"?": (".####..", "#....#.", ".....#.", "....#..", "...#...", "...#...",
      ".......", "...#...", "..##..."),
"$": ("...#...", ".####..", "#...#..", "#......", ".###...", "....#..",
      "#...#..", ".####..", "...#..."),
"'": ("...#...", "...#...", "..#....", ".......", ".......", ".......",
      ".......", ".......", "......."),
'"': (".#.#...", ".#.#...", ".#.#...", ".......", ".......", ".......",
      ".......", ".......", "......."),
"+": (".......", ".......", ".......", "...#...", ".#####.", "...#...",
      ".......", ".......", "......."),
"&": (".####..", "#....#.", "#....#.", ".###...", "#..#.#.", "#....#.",
      "#....#.", ".###.#.", "......."),
"=": (".......", ".......", ".......", ".#####.", ".......", ".#####.",
      ".......", ".......", "......."),
"•": (".......", ".......", ".......", ".......", "..##...", "..##...",
      ".......", ".......", "......."),
})

for _ch, _rows in GLYPHS.items():
    assert len(_rows) == 9, _ch
    for _row in _rows:
        assert len(_row) == 7, (_ch, _row)


class Sheet:
    """An RGB canvas with newspaper drawing tools."""

    def __init__(self):
        self.buf = bytearray(PAPER_RGB * (PAGE_W * PAGE_H))

    def px(self, x, y, col):
        if 0 <= x < PAGE_W and 0 <= y < PAGE_H:
            i = (y * PAGE_W + x) * 3
            self.buf[i:i + 3] = bytes(col)

    def rect(self, x, y, w, h, col):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, col)

    def hline(self, x, y, w, col, t=1):
        self.rect(x, y, w, t, col)

    def vline(self, x, y, h, col, t=1):
        self.rect(x, y, t, h, col)

    def line(self, x0, y0, x1, y1, col, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, col)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, col, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.px(xx, yy, col)
                elif not fill and abs(d - r * r) <= r * 2:
                    self.px(xx, yy, col)

    def poly(self, pts, col):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(xs[i], xs[i + 1] + 1):
                    self.px(x, y, col)

    def text(self, x, y, s, scale, col):
        cx = x
        for ch in s:
            rows = GLYPHS.get(ch)
            if rows is None:
                cx += 8 * scale
                continue
            for r, row in enumerate(rows):
                for c, bit in enumerate(row):
                    if bit == "#":
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, col)
            cx += 8 * scale
        return cx

    def twidth(self, s, scale):
        return len(s) * 8 * scale

    def centre(self, y, s, scale, col):
        self.text((PAGE_W - self.twidth(s, scale)) // 2, y, s, scale, col)

    def wrap(self, s, scale, width):
        """Greedy word wrap; returns a list of lines fitting width."""
        words = s.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.twidth(trial, scale) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, width, col, lh=None):
        lh = lh or (9 * scale + 4)
        for ln in self.wrap(s, scale, width):
            self.text(x, y, ln, scale, col)
            y += lh
        return y

    def dark_ink(self):
        dark = 0
        for i in range(0, len(self.buf), 3):
            if self.buf[i] < 128 and self.buf[i + 1] < 128 \
                    and self.buf[i + 2] < 128:
                dark += 1
        return dark / (PAGE_W * PAGE_H)


def png_bytes(sheet):
    raw = bytearray()
    stride = PAGE_W * 3
    for y in range(PAGE_H):
        raw.append(0)
        raw += sheet.buf[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", PAGE_W, PAGE_H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- scenes

def draw_market(p, x, y, w, h):
    # A rising chart: the rebound after Friday's rout.
    p.rect(x, y, w, h, (255, 255, 255))
    p.rect(x, y + h - 30, w, 30, (238, 238, 238))
    p.line(x + 30, y + 92, x + 90, y + 86, GREEN_RGB, 3)
    p.line(x + 90, y + 86, x + 150, y + 90, GREEN_RGB, 3)
    p.line(x + 150, y + 90, x + 200, y + 46, GREEN_RGB, 3)
    p.line(x + 200, y + 46, x + 250, y + 38, GREEN_RGB, 3)
    p.line(x + 250, y + 38, x + 296, y + 14, GREEN_RGB, 3)
    p.poly([(x + 296, y + 14), (x + 284, y + 12), (x + 296, y + 26)], GREEN_RGB)
    p.rect(x + 70, y + h - 22, 10, 12, GREEN_RGB)
    p.rect(x + 86, y + h - 16, 10, 6, GREEN_RGB)
    p.rect(x + 102, y + h - 26, 10, 16, GREEN_RGB)


def draw_summit(p, x, y, w, h):
    # Two flags over an empty round table: no consensus.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 24, w, 24, SAND_RGB)
    p.rect(x + 20, y + h - 52, w - 40, 28, (220, 220, 220))
    p.circle(x + w // 2, y + h - 52, 16, (220, 220, 220))
    p.vline(x + 34, y + 8, h - 40, INK_RGB, 2)
    p.vline(x + w - 36, y + 8, h - 40, INK_RGB, 2)
    p.poly([(x + 36, y + 8), (x + 74, y + 16), (x + 36, y + 24)], RED_RGB)
    p.poly([(x + w - 36, y + 8), (x + w - 74, y + 16), (x + w - 36, y + 24)],
           BLUE_RGB)
    p.rect(x + w // 2 - 30, y + h - 46, 60, 6, INK_RGB)
    p.rect(x + w // 2 - 6, y + h - 58, 12, 12, INK_RGB)


def draw_strait(p, x, y, w, h):
    # Two tankers in a narrow strait, smoke on the horizon.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 32, w, 32, BLUE_RGB)
    p.poly([(x + 30, y + h - 54), (x + 150, y + h - 32), (x + 140, y + h - 18),
            (x + 44, y + h - 18)], (90, 90, 90))
    p.rect(x + 130, y + h - 68, 22, 14, (255, 255, 255))
    p.poly([(x + 190, y + h - 54), (x + 290, y + h - 32), (x + 280, y + h - 18),
            (x + 204, y + h - 18)], (120, 120, 120))
    p.circle(x + 250, y + h - 62, 7, (240, 120, 20))
    p.circle(x + 262, y + h - 70, 5, (240, 120, 20))
    p.circle(x + 136, y + h - 80, 6, (120, 120, 120))
    p.circle(x + 148, y + h - 88, 5, (120, 120, 120))
    p.line(x + 10, y + h - 12, x + 40, y + h - 20, (255, 255, 255), 2)
    p.line(x + 40, y + h - 20, x + 70, y + h - 12, (255, 255, 255), 2)
    p.line(x + 70, y + h - 12, x + 100, y + h - 20, (255, 255, 255), 2)
    p.line(x + 100, y + h - 20, x + 130, y + h - 12, (255, 255, 255), 2)
    p.line(x + 130, y + h - 12, x + 160, y + h - 20, (255, 255, 255), 2)
    p.line(x + 160, y + h - 20, x + 190, y + h - 12, (255, 255, 255), 2)


def draw_rocket(p, x, y, w, h):
    # A small planet and a rocket climbing away from it.
    p.rect(x, y, w, h, (24, 40, 90))
    p.circle(x + 52, y + 26, 16, (196, 150, 110))
    p.circle(x + 46, y + 20, 4, (150, 110, 80))
    p.circle(x + 58, y + 32, 3, (150, 110, 80))
    for sx, sy in ((140, 18), (168, 34), (120, 52), (176, 62)):
        p.circle(x + sx, y + sy, 2, (255, 255, 255))
    p.poly([(x + 96, y + 84), (x + 104, y + 40), (x + 112, y + 84)],
           (255, 255, 255))
    p.poly([(x + 104, y + 40), (x + 104, y + 28), (x + 112, y + 44),
            (x + 104, y + 44)], RED_RGB)
    p.poly([(x + 96, y + 84), (x + 88, y + 96), (x + 96, y + 92)], RED_RGB)
    p.poly([(x + 112, y + 84), (x + 120, y + 96), (x + 112, y + 92)], RED_RGB)
    p.poly([(x + 100, y + 84), (x + 108, y + 84), (x + 104, y + 100)],
           (240, 120, 20))


def draw_chip(p, x, y, w, h):
    # A square chip on a pale board, pins on all four sides.
    p.rect(x, y, w, h, (238, 238, 238))
    p.rect(x + 20, y + 10, w - 40, 12, (220, 220, 220))
    for px in range(40, w - 30, 18):
        p.line(x + px, y + 22, x + px, y + 34, BLUE_RGB, 2)
        p.line(x + px, y + h - 22, x + px, y + h - 34, BLUE_RGB, 2)
    for py in range(40, h - 30, 18):
        p.line(x + 20, y + py, x + 32, y + py, BLUE_RGB, 2)
        p.line(x + w - 20, y + py, x + w - 32, y + py, BLUE_RGB, 2)
    p.rect(x + 64, y + 22, 64, 64, INK_RGB)
    p.rect(x + 74, y + 32, 44, 44, TEAL_RGB)
    p.rect(x + 88, y + 46, 16, 16, (255, 255, 255))


def draw_ship(p, x, y, w, h):
    # A grey hull with smoke rising from the deck.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 30, w, 30, BLUE_RGB)
    p.poly([(x + 30, y + h - 52), (x + 150, y + h - 30), (x + 140, y + h - 16),
            (x + 44, y + h - 16)], (120, 120, 120))
    p.line(x + 60, y + h - 52, x + 60, y + h - 70, INK_RGB, 2)
    p.circle(x + 60, y + h - 76, 8, (90, 90, 90))
    p.circle(x + 72, y + h - 84, 6, (120, 120, 120))
    p.circle(x + 118, y + h - 58, 7, (240, 120, 20))
    p.circle(x + 130, y + h - 66, 5, (240, 120, 20))
    p.line(x + 10, y + h - 12, x + 40, y + h - 20, (255, 255, 255), 2)
    p.line(x + 40, y + h - 20, x + 70, y + h - 12, (255, 255, 255), 2)
    p.line(x + 70, y + h - 12, x + 100, y + h - 20, (255, 255, 255), 2)
    p.line(x + 100, y + h - 20, x + 130, y + h - 12, (255, 255, 255), 2)
    p.line(x + 130, y + h - 12, x + 160, y + h - 20, (255, 255, 255), 2)
    p.line(x + 160, y + h - 20, x + 182, y + h - 12, (255, 255, 255), 2)


def draw_tanker(p, x, y, w, h):
    # A tanker hull, low in the water, with a flame astern.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 32, w, 32, BLUE_RGB)
    p.rect(x + 14, y + h - 52, 150, 22, (90, 90, 90))
    p.rect(x + 130, y + h - 66, 22, 14, (255, 255, 255))
    p.circle(x + 52, y + h - 22, 5, INK_RGB)
    p.line(x + 48, y + h - 26, x + 56, y + h - 18, INK_RGB, 1)
    p.line(x + 48, y + h - 18, x + 56, y + h - 26, INK_RGB, 1)
    p.circle(x + 150, y + h - 58, 7, (240, 120, 20))
    p.circle(x + 162, y + h - 66, 5, (240, 120, 20))


def draw_factory(p, x, y, w, h):
    # A sawtooth roof, a chimney, and a spark on the line.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 20, w, 20, SAND_RGB)
    p.poly([(x + 16, y + h - 20), (x + 16, y + h - 52), (x + 40, y + h - 40),
            (x + 64, y + h - 52), (x + 88, y + h - 40), (x + 112, y + h - 52),
            (x + 136, y + h - 40), (x + 150, y + h - 52), (x + 150, y + h - 20)],
           (150, 150, 150))
    p.rect(x + 158, y + 12, 12, h - 32, (120, 120, 120))
    p.circle(x + 164, y + 8, 6, (90, 90, 90))
    p.poly([(x + 84, y + h - 52), (x + 96, y + h - 30), (x + 90, y + h - 36),
            (x + 98, y + h - 32), (x + 92, y + h - 20), (x + 76, y + h - 20)],
           (240, 120, 20))


def draw_capitol(p, x, y, w, h):
    # A domed hall with columns and a dark door.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 18, w, 18, SAND_RGB)
    p.circle(x + w // 2, y + h - 34, 22, (220, 220, 220))
    p.rect(x + w // 2 - 22, y + h - 34, 44, 16, (220, 220, 220))
    for cx in (30, 56, 132, 158):
        p.rect(x + cx, y + h - 44, 8, 26, (255, 255, 255))
    p.rect(x + 84, y + h - 44, 24, 26, INK_RGB)
    p.rect(x + 88, y + h - 40, 16, 4, (255, 255, 255))


def draw_city(p, x, y, w, h):
    # A low skyline under drifting cloud.
    p.rect(x, y, w, h, SKY_RGB)
    p.rect(x, y + h - 18, w, 18, SAND_RGB)
    for bx, bh in ((14, 40), (44, 56), (78, 34), (108, 50), (142, 38)):
        p.rect(x + bx, y + h - 18 - bh, 26, bh, (120, 120, 120))
    p.circle(x + 60, y + 14, 6, (90, 90, 90))
    p.circle(x + 74, y + 8, 8, (90, 90, 90))
    p.circle(x + 130, y + 16, 6, (90, 90, 90))


def draw_chess(p, x, y, w, h):
    # An eight-square board with two kings facing off.
    p.rect(x, y, w, h, SAND_RGB)
    for r in range(4):
        for c in range(8):
            if (r + c) % 2 == 0:
                p.rect(x + 16 + c * 20, y + 6 + r * 16, 20, 16, INK_RGB)
    p.circle(x + 56, y + 26, 10, (255, 255, 255))
    p.rect(x + 52, y + 12, 8, 6, (255, 255, 255))
    p.circle(x + 136, y + 54, 10, INK_RGB)
    p.rect(x + 132, y + 40, 8, 6, INK_RGB)
    p.circle(x + 96, y + 88, 7, (255, 255, 255))
    p.poly([(x + 92, y + 92), (x + 100, y + 92), (x + 96, y + 100)], INK_RGB)


def draw_goal(p, x, y, w, h):
    # A pitch, a goal, and a ball on the spot.
    p.rect(x, y, w, h, GRASS_RGB)
    p.line(x, y + h // 2, x + w, y + h // 2, (255, 255, 255), 2)
    p.rect(x + 30, y + 12, 6, 34, (255, 255, 255))
    p.rect(x + 130, y + 12, 6, 34, (255, 255, 255))
    p.rect(x + 30, y + 12, 106, 6, (255, 255, 255))
    for i in range(6):
        p.vline(x + 40 + i * 16, y + 18, 26, (255, 255, 255), 1)
    p.circle(x + w // 2, y + h - 18, 9, (255, 255, 255))
    p.poly([(x + w // 2 - 4, y + h - 22), (x + w // 2 + 4, y + h - 22),
            (x + w // 2, y + h - 14)], INK_RGB)


def draw_trophy(p, x, y, w, h):
    # A gold cup on a green pitch, ball at its foot.
    p.rect(x, y, w, h, GRASS_RGB)
    p.line(x, y + h // 2, x + w, y + h // 2, (255, 255, 255), 2)
    p.poly([(x + w // 2 - 22, y + 10), (x + w // 2 + 22, y + 10),
            (x + w // 2 + 16, y + 38), (x + w // 2 - 16, y + 38)],
           (240, 196, 64))
    p.line(x + w // 2, y + 38, x + w // 2, y + 50, (240, 196, 64), 3)
    p.line(x + w // 2 - 14, y + 52, x + w // 2 + 14, y + 52, (240, 196, 64), 3)
    p.circle(x + w - 24, y + h - 18, 7, (255, 255, 255))
    p.poly([(x + w - 28, y + h - 22), (x + w - 20, y + h - 22),
            (x + w - 24, y + h - 14)], INK_RGB)


def frame(p, x, y, w, h):
    p.hline(x, y, w, INK_RGB, 2)
    p.hline(x, y + h - 2, w, INK_RGB, 2)
    p.vline(x, y, h, INK_RGB, 2)
    p.vline(x + w - 2, y, h, INK_RGB, 2)


def tag_box(p, x, y, s, col):
    w = p.twidth(s, 1) + 14
    p.rect(x, y, w, 18, col)
    p.text(x + 7, y + 5, s, 1, (255, 255, 255))
    return w


# ---------------------------------------------------------------- content

HEROES = [
    (draw_market, RED_RGB, "CONFIRMED", "WALL STREET",
     "Wall St roars as Huang returns",
     "Nvidia up 31.5% as board reinstates its founder; Nasdaq jumps 6.5%.",
     "Source: Reuters / CNN, 23 Nov"),
    (draw_summit, RED_RGB, "CONFIRMED", "ANTALYA",
     "COP31 collapses with no deal",
     "Longest summit on record ends in Antalya; fossil fuels split the talks.",
     "Source: UN News, 22 Nov"),
    (draw_strait, AMBER_RGB, "DEVELOPING", "THE GULF",
     "Hormuz on edge as tankers hit",
     "Two tankers struck; Iran vows to counter a US blockade threat.",
     "Source: UKMTO / AP, 23 Nov"),
]

CARDS = [
    (draw_rocket, "BepiColombo at Mercury",
     "Eight-year trip ends in orbit. ESA/JAXA"),
    (draw_chip, "Zscaler buy $43.9bn",
     "CrowdStrike all-stock. 23 Nov"),
    (draw_ship, "Corvette burns",
     "Russian ship hit at Benghazi. Naval News"),
    (draw_tanker, "Sparta II ablaze",
     "Cargo ship hit by drones. AP"),
    (draw_factory, "Plant fire kills 24",
     "Candy plant blaze, Cikande. Reuters"),
    (draw_capitol, "India-China talks",
     "Border talks in Arunachal. TOI"),
    (draw_city, "Modi opens AI centre",
     "IIT Patna gets Rs 400cr park. TOI"),
    (draw_chess, "Gukesh defends",
     "World chess opens in Geneva. TOI"),
    (draw_goal, "Champions League",
     "Arsenal-Dortmund lead tonight. UEFA"),
    (draw_trophy, "Cowboys rout Titans",
     "Prescott throws four TDs. AP, 23 Nov"),
]

TIMELINE = [
    ("13:55", "Huang return breaks before open"),
    ("14:30", "Wall Street opens sharply higher"),
    ("16:45", "Champions League night kicks off"),
    ("21:00", "Nasdaq closes up 6.5%"),
    ("00:00", "Austria ministry site breached"),
    ("01:05", "UN warns on Black Sea shipping"),
]

ALSO = [
    "India and NZ draw first Test in Wellington — TOI",
    "England 37-12 New Zealand, record win — BBC",
    "Gaza soil and water poisoned, Oxfam warns — Oxfam",
    "Trump bid to Kim ignored, WSJ reports — WSJ",
    "Anthropic debuts at $83 a share — AITNT",
    "Tesla rolls out FSD v15 — AITNT",
    "Zhipu releases GLM-5.4 model — AITNT",
    "Sierra raises $1.75bn at $30bn value — AI-Newsdesk",
]

NUMBERS = [
    ("S&P 500", "+4.7%"),
    ("NASDAQ COMP.", "+6.5%"),
    ("DOW JONES", "+3.0%"),
    ("NVIDIA", "+31.5%"),
    ("BITCOIN", "$61,000"),
    ("GOLD, PER OZ", "$3,666"),
]


def build():
    p = Sheet()
    # Masthead: white nameplate on a black bar, then the date line.
    p.rect(24, 10, 976, 58, INK_RGB)
    p.centre(14, "The Day's World", 5, (255, 255, 255))
    p.hline(24, 68, 976, RULE_RGB, 3)
    p.text(24, 78, "Tuesday, 24 November 2026", 2, INK_RGB)
    right = "No. 328  •  Price: one day"
    p.text(PAGE_W - 24 - p.twidth(right, 2), 78, right, 2, INK_RGB)
    p.hline(24, 102, 976, RULE_RGB, 1)
    p.hline(24, 106, 976, RULE_RGB, 3)
    # Numbers strip.
    cw = 976 // 6
    for i, (label, num) in enumerate(NUMBERS):
        x = 24 + i * cw
        if i:
            p.vline(x, 114, 38, PALE_RGB, 1)
        p.text(x + 6, 116, label, 1, GREY_RGB)
        p.text(x + 6, 130, num, 2, INK_RGB)
    p.hline(24, 154, 976, RULE_RGB, 1)
    # Heroes.
    for i, (scene, col, tag, region, head, stand, src) in enumerate(HEROES):
        x = 24 + i * 328
        scene(p, x, 162, 320, 128)
        frame(p, x, 162, 320, 128)
        tw = tag_box(p, x, 296, tag, col)
        p.text(x + tw + 8, 301, region, 1, RED_RGB)
        y = 320
        for ln in p.wrap(head, 2, 320):
            p.text(x, y, ln, 2, INK_RGB)
            y += 22
        y += 2
        for ln in p.wrap(stand, 1, 320)[:3]:
            p.text(x, y, ln, 1, GREY_RGB)
            y += 13
        p.text(x, 408, src, 1, GREY_RGB)
        if i < 2:
            p.vline(x + 324, 162, 262, PALE_RGB, 1)
    p.hline(24, 428, 976, RULE_RGB, 3)
    # Scene cards.
    p.text(24, 438, "The rest of the day", 2, INK_RGB)
    p.hline(24, 458, 976, RULE_RGB, 1)
    for i, (scene, head, sub) in enumerate(CARDS):
        r, c = divmod(i, 5)
        x = 24 + c * 196
        y = 466 + r * 168
        scene(p, x, y, 192, 76)
        frame(p, x, y, 192, 76)
        if c:
            p.vline(x - 2, y, 160, PALE_RGB, 1)
        yy = y + 82
        for ln in p.wrap(head, 2, 184):
            p.text(x, yy, ln, 2, INK_RGB)
            yy += 22
        yy += 2
        for ln in p.wrap(sub, 1, 184)[:2]:
            p.text(x, yy, ln, 1, GREY_RGB)
            yy += 13
    p.hline(24, 802, 976, RULE_RGB, 3)
    # Timeline.
    p.text(24, 812, "The day in time — all times UTC", 2, INK_RGB)
    p.hline(24, 836, 976, RULE_RGB, 2)
    tw = 976 // 6
    for i, (t, what) in enumerate(TIMELINE):
        x = 24 + i * tw
        p.circle(x + 4, 836, 5, RED_RGB)
        p.text(x, 848, t, 2, RED_RGB)
        yy = 872
        for ln in p.wrap(what, 1, tw - 8)[:3]:
            p.text(x, yy, ln, 1, INK_RGB)
            yy += 12
    p.hline(24, 912, 976, RULE_RGB, 1)
    # Also today.
    p.text(24, 920, "Also today", 2, INK_RGB)
    for i, item in enumerate(ALSO):
        r, c = divmod(i, 2)
        x = 24 + c * 492
        y = 940 + r * 13
        p.text(x, y, "•  " + item, 1, INK_RGB)
    # Legend and footer.
    p.hline(24, 994, 976, RULE_RGB, 1)
    p.text(24, 1002, "CONFIRMED = verified  •  DEVELOPING = facts "
           "still coming in  •  PENDING = decision awaited",
           1, GREY_RGB)
    # Thin black frame around the whole front page.
    frame(p, 8, 8, 1008, 1008)
    return p


def main():
    page = build()
    data = png_bytes(page)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)
    print("wrote %s (%d bytes, dark ink %.1f%%)"
          % (target, len(data), page.dark_ink() * 100))


if __name__ == "__main__":
    main()
