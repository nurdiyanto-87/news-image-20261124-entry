#!/usr/bin/env python3
"""news-image-20261124 entry: draws a one-page newspaper front page summing up
the world news of Tuesday 24 November 2026. Pure stdlib (zlib, struct, os,
math). The program draws every pixel itself and writes /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png). Deterministic: no randomness, no clock,
no network."""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
WHITE = (255, 255, 255)
INK = (18, 22, 30)
NAVY = (15, 42, 74)
GOLD = (217, 164, 65)
GRAY = (96, 96, 96)
SUB = (64, 64, 64)
RED = (178, 34, 34)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '#' = on.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "•": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(-(thick // 2), thick // 2 + 1):
                for b in range(-(thick // 2), thick // 2 + 1):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int(math.sqrt(max(r * r - dy * dy, 0)))
                self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        else:
            steps = max(24, int(2 * math.pi * r))
            for i in range(steps):
                a = 2 * math.pi * i / steps
                self.set(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)

    def poly(self, pts, c, fill=True):
        if fill:
            ys = [p[1] for p in pts]
            for y in range(min(ys), max(ys) + 1):
                xs = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= y < y1) or (y1 <= y < y0):
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
                xs.sort()
                for j in range(0, len(xs) - 1, 2):
                    self.rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, c)
        else:
            n = len(pts)
            for i in range(n):
                self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                          pts[(i + 1) % n][1], c)

    def star(self, cx, cy, r_out, r_in, points, c):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / points - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)


# ---------------------------------------------------------------- pictograms
# Each draws a small scene inside (x, y, w, h).

def pic_gaza(cv, x, y, w, h):
    sky = (250, 232, 214)
    cv.rect(x, y, w, h, sky)
    base = y + h - 8
    # buildings
    heights = [34, 52, 28, 62, 44, 58, 30, 48]
    bw = w // len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw + 2
        cv.rect(bx, base - bh, bw - 4, bh, (58, 52, 48))
        # lit windows
        for wy in range(base - bh + 6, base - 6, 12):
            cv.rect(bx + 4, wy, 5, 6, (240, 200, 90))
    # explosion burst
    cx, cy = x + w // 2 + 30, y + 26
    cv.star(cx, cy, 30, 12, 8, (245, 140, 30))
    cv.star(cx, cy, 18, 8, 8, (255, 210, 60))
    cv.circle(cx, cy, 7, (255, 240, 180))
    # smoke
    for sx, sy, sr in ((x + w // 2 - 90, y + 18, 12), (x + w // 2 - 70, y + 10, 9),
                       (x + w // 2 + 110, y + 14, 11)):
        cv.circle(sx, sy, sr, (150, 140, 130))
    cv.rect(x, base, w, 8, (40, 36, 32))


def pic_korea(cv, x, y, w, h):
    cv.rect(x, y, w, h, (222, 236, 250))
    cx, cy = x + w // 2, y + h // 2 + 4
    # radar arcs
    for r in (18, 30, 42):
        cv.circle(x + 52, cy, r, (200, 40, 40), fill=False)
    cv.circle(x + 52, cy, 5, (200, 40, 40))
    # jet (nose right)
    jet = (200, 40, 40)
    pts = [(cx - 70, cy - 3), (cx - 10, cy - 5), (cx + 55, cy - 2),
           (cx + 80, cy), (cx + 55, cy + 2), (cx - 10, cy + 5), (cx - 70, cy + 3)]
    cv.poly(pts, (70, 76, 84))
    cv.poly([(cx - 35, cy - 4), (cx - 2, cy - 26), (cx + 12, cy - 4)], (70, 76, 84))
    cv.poly([(cx - 35, cy + 4), (cx - 2, cy + 26), (cx + 12, cy + 4)], (70, 76, 84))
    cv.poly([(cx - 62, cy - 3), (cx - 48, cy - 20), (cx - 38, cy - 3)], (70, 76, 84))
    # alert triangle
    tx, ty = x + w - 66, y + 12
    cv.poly([(tx, ty + 26), (tx + 15, ty), (tx + 30, ty + 26)], (245, 180, 20))
    cv.rect(tx + 13, ty + 8, 4, 10, (18, 22, 30))
    cv.rect(tx + 13, ty + 21, 4, 4, (18, 22, 30))


def pic_ships(cv, x, y, w, h):
    cv.rect(x, y, w, h, (216, 240, 238))
    base = y + h - 22
    # tanker hull
    cv.poly([(x + 60, base - 26), (x + 330, base - 26), (x + 372, base - 6),
             (x + 60, base - 6)], (40, 52, 66))
    cv.rect(x + 60, base - 26, 312, 6, (120, 40, 30))
    # containers
    cols = [(200, 70, 50), (60, 110, 150), (220, 160, 40), (90, 140, 90)]
    for i, col in enumerate(cols):
        cv.rect(x + 84 + i * 52, base - 52, 46, 24, col)
    # bridge tower
    cv.rect(x + 316, base - 58, 34, 32, (230, 230, 225))
    cv.rect(x + 320, base - 54, 26, 6, (40, 60, 90))
    # signal waves
    for r in (12, 22, 32):
        cv.circle(x + 410, y + 26, r, (14, 120, 120), fill=False)
    cv.circle(x + 410, y + 26, 5, (14, 120, 120))
    # sea
    cv.rect(x, base + 2, w, 4, (30, 110, 150))
    cv.rect(x + 20, base + 12, 90, 3, (30, 110, 150))
    cv.rect(x + 300, base + 12, 110, 3, (30, 110, 150))


def pic_train(cv, x, y, w, h):
    cv.rect(x, y, w, h, (252, 236, 216))
    base = y + h - 18
    # rails
    cv.rect(x + 20, base, w - 40, 4, (90, 90, 90))
    cv.rect(x + 20, base + 10, w - 40, 3, (90, 90, 90))
    for tx in range(x + 30, x + w - 30, 26):
        cv.rect(tx, base, 6, 13, (120, 120, 120))
    # train cars
    cv.rect(x + 40, base - 52, 120, 52, (200, 110, 20))
    cv.rect(x + 166, base - 52, 120, 52, (30, 90, 150))
    cv.rect(x + 292, base - 52, 120, 52, (200, 110, 20))
    for cx0 in (x + 40, x + 166, x + 292):
        for wx in range(cx0 + 10, cx0 + 108, 24):
            cv.rect(wx, base - 44, 16, 14, (220, 240, 250))
    # wheels
    for wx in (x + 62, x + 138, x + 188, x + 264, x + 314, x + 390):
        cv.circle(wx, base + 2, 7, (30, 30, 30))
    # flags on poles (India, Nepal)
    for fx, stripes in ((x + 428, [(255, 153, 51), (255, 255, 255), (19, 136, 8)]),
                        (x + 452, None)):
        cv.rect(fx, y + 8, 3, 46, (60, 60, 60))
        if stripes:
            for i, col in enumerate(stripes):
                cv.rect(fx + 3, y + 8 + i * 7, 22, 7, col)
        else:
            cv.poly([(fx + 3, y + 8), (fx + 25, y + 15), (fx + 3, y + 22)],
                    (220, 20, 60))
            cv.poly([(fx + 3, y + 22), (fx + 22, y + 28), (fx + 3, y + 34)],
                    (220, 20, 60))


def pic_chess(cv, x, y, w, h):
    cv.rect(x, y, w, h, (238, 228, 250))
    bx, by = x + 140, y + 2
    sq = 10
    for r in range(8):
        for c in range(8):
            col = (250, 246, 240) if (r + c) % 2 == 0 else (60, 40, 90)
            cv.rect(bx + c * sq, by + r * sq, sq, sq, col)
    # king piece (gold)
    kx = x + 330
    cv.rect(kx - 24, by + 58, 48, 13, (217, 164, 65))
    cv.poly([(kx - 15, by + 58), (kx + 15, by + 58), (kx + 8, by + 30),
             (kx - 8, by + 30)], (217, 164, 65))
    cv.circle(kx, by + 19, 14, (217, 164, 65))
    cv.rect(kx - 2, by + 1, 4, 13, (217, 164, 65))
    cv.rect(kx - 7, by + 5, 14, 4, (217, 164, 65))
    # small pawn on board
    cv.circle(bx + 4 * sq + 4, by + 5 * sq + 3, 4, (30, 30, 30))


def pic_quake(cv, x, y, w, h):
    cv.rect(x, y, w, h, (250, 238, 214))
    # seismograph zigzag (starts right of the magnitude label)
    pts = [(x + 96, y + 34)]
    amp = [0, -18, 26, -30, 34, -22, 14, -8, 4, 0]
    for i, a in enumerate(amp):
        pts.append((x + 96 + (i + 1) * 20, y + 34 + a))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                (150, 30, 20), thick=3)
    # island + waves
    ix = x + 330
    cv.poly([(ix - 60, y + h - 10), (ix - 30, y + h - 44), (ix + 10, y + h - 52),
             (ix + 46, y + h - 30), (ix + 66, y + h - 10)], (90, 120, 70))
    cv.poly([(ix - 30, y + h - 44), (ix - 18, y + h - 44), (ix - 24, y + h - 58)],
            (60, 90, 50))
    for wy in (y + h - 8, y + h - 2):
        cv.line(x + 20, wy, x + 300, wy, (30, 110, 160), thick=2)
    cv.text(x + 16, y + 8, "6.5", 3, (150, 30, 20))


# ---------------------------------------------------------------- stories
# All verified against Reuters / CNN / AP / WSJ reporting dated 24 Nov 2026.
STORIES = [
    dict(kicker="MIDDLE EAST", accent=RED, pic=pic_gaza,
         head=["STRIKE KILLS 3 IN GAZA"],
         sub=["Israeli airstrike hits Khan Younis;", "at least three killed, five hurt"]),
    dict(kicker="ASIA", accent=(30, 80, 160), pic=pic_korea,
         head=["RUSSIAN JET SPARKS ALERT"],
         sub=["Seoul warns Ulleung island after", "Russian plane enters its airspace"]),
    dict(kicker="IRAN - CYBERWAR", accent=(14, 120, 120), pic=pic_ships,
         head=["US PROBES IRAN", "IN SHIP HACKS"],
         sub=["Up to 50 tankers hit in cyberattacks;", "US suspects an Iran link, WSJ says"]),
    dict(kicker="SOUTH ASIA", accent=(200, 110, 20), pic=pic_train,
         head=["NEW TRAIN LINKS", "INDIA AND NEPAL"],
         sub=["Modi and Shah flag off Saryu-Kamala", "Express; eight pacts, big aid deal"]),
    dict(kicker="SPORT", accent=(110, 60, 160), pic=pic_chess,
         head=["CHESS CROWN DEFENCE OPENS"],
         sub=["Gukesh defends world title against", "Sindarov as championship opens"]),
    dict(kicker="PACIFIC", accent=(150, 100, 30), pic=pic_quake,
         head=["6.5 QUAKE HITS VANUATU"],
         sub=["Strong tremor shakes Pacific islands;", "no tsunami threat, officials say"]),
]


def build():
    cv = Canvas(W, H, PAPER)
    # thin frame
    cv.rect(0, 0, W, 6, INK)
    cv.rect(0, H - 6, W, 6, INK)
    cv.rect(0, 0, 6, H, INK)
    cv.rect(W - 6, 0, 6, H, INK)

    # ---- masthead
    cv.rect(0, 6, W, 166, NAVY)
    cv.text_center(24, "THE WORLD IN ONE DAY", 2, GOLD)
    cv.text_center(56, "24 NOVEMBER 2026", 8, WHITE)
    cv.text_center(132, "TUESDAY - SIX STORIES THAT DEFINED THE DAY", 2, GOLD)
    cv.rect(16, 164, W - 32, 3, GOLD)

    # ---- standfirst strip
    cv.text_center(186, "FROM GAZA TO GENEVA - WAR, DIPLOMACY, MARKETS AND SPORT",
                   2, INK)

    # ---- story grid: 2 columns x 3 rows
    px0, pw = 16, 480
    py0, ph, gap = 212, 228, 12
    for i, st in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = px0 + col * (pw + 16)
        y = py0 + row * (ph + gap)
        # card
        cv.rect(x, y, pw, ph, WHITE)
        for bx, by, bw, bh in ((x, y, pw, 2), (x, y + ph - 2, pw, 2),
                               (x, y, 2, ph), (x + pw - 2, y, 2, ph)):
            cv.rect(bx, by, bw, bh, INK)
        # kicker bar
        cv.rect(x + 2, y + 2, pw - 4, 26, st["accent"])
        cv.text(x + 14, y + 10, st["kicker"], 2, WHITE)
        # pictogram
        st["pic"](cv, x + 2, y + 28, pw - 4, 84)
        # headline
        hy = y + 122
        for line in st["head"]:
            cv.text_center(hy, line, 3, INK, x + 14, x + pw - 14)
            hy += 24
        # sub lines
        sy = hy + 6
        for line in st["sub"]:
            cv.text_center(sy, line, 2, SUB, x + 14, x + pw - 14)
            sy += 19

    # ---- footer: also in the news
    fy = 932
    cv.rect(0, fy, W, 76, NAVY)
    cv.text_center(fy + 12,
                   "ALSO: NVIDIA SHARES SOAR AS HUANG RETURNS - COP31 BLAME GAME AFTER COLLAPSE",
                   2, GOLD)
    cv.text_center(fy + 38,
                   "INDONESIA CONFIRMS 24 DEAD IN FACTORY FIRE - US STATES SUE SPACEX OVER GROK AI",
                   2, WHITE)
    cv.text_center(1010, "SOURCES: REUTERS, CNN, AP, WSJ - REPORTED 24 NOVEMBER 2026",
                   1, GRAY)
    return cv


# ---------------------------------------------------------------- PNG writer
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = (b"\x89PNG\r\n\x1a\n" +
           _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)) +
           _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
           _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    cv = build()
    path = os.path.join(out, "entry.png")
    size = write_png(path, cv)
    print(f"wrote {path} {cv.w}x{cv.h} {size} bytes")


if __name__ == "__main__":
    main()
