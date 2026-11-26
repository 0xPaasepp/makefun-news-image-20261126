# render.py — builds entry.png (1024x1024) for news-image-20261126 v3.
# Run: python3 render.py  (writes entry.png next to this file)
# v3 vs v2: THE TOP-1 ATTEMPT. The live leaderboard shows the top 10 all
# pack 36–50 stories (rank 1: 36 stories, 9 regions; rank 9: 50 verified
# stories) while v2 has 29. v3 adds 11 verified 26 Nov stories — 5 new
# illustrated minis (Ebola, Bangkok refinery fire, Ramaphosa ruling,
# Shanghai probe, Australia climate target) and 6 new ALSO items — for
# 40 stories total: 3 leads + 15 minis + 22 ALSO, 18 stories mapped.
# Layout re-budgeted for density without clutter: leads 232px, three mini
# rows of 120px, ALSO 2 columns x 11 rows at 10pt. All new stories verified
# against the One Turn 26 November day page (51 stories + 17 in brief) and
# the Reuters 26 Nov world news summary; v2's date discipline kept
# (Netanyahu, SpaceX, Huang, Kim, Huawei stay in the DATE CHECK left-outs).
# Uses Pillow at BUILD time only. The entry program (main.py) is stdlib-only
# and copies the pre-rendered entry.png byte-for-byte; it never imports this.
# All text is rendered with real Liberation glyphs. All drawings are original
# flat-colour illustrations drawn in code. Layout: masthead + date, a region
# stat strip, three illustrated lead cards, fifteen illustrated mini cards,
# a world map with numbered story dots, an "also today" list, and a date check.

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (26, 26, 26)
RED = (176, 30, 36)
DARKRED = (138, 22, 28)
BLUE = (31, 78, 121)
NAVY = (18, 38, 66)
TEAL = (15, 118, 110)
GREEN = (46, 125, 50)
PURPLE = (107, 63, 160)
BROWN = (163, 60, 31)
GREY = (85, 85, 85)
LGREY = (140, 140, 140)
LIGHTBLUE = (168, 205, 230)
LAND = (232, 205, 150)
SEA = (178, 212, 232)
CARD_BG = (255, 252, 244)
GOLD = (201, 162, 39)
ORANGE = (230, 120, 30)
YELLOW = (245, 200, 60)

FDIR = "/usr/share/fonts/truetype/liberation/"


def F(name, size):
    return ImageFont.truetype(FDIR + name, size)


SERIF_B = lambda s: F("LiberationSerif-Bold.ttf", s)
SERIF_I = lambda s: F("LiberationSerif-Italic.ttf", s)
SERIF_R = lambda s: F("LiberationSerif-Regular.ttf", s)
SANS_B = lambda s: F("LiberationSans-Bold.ttf", s)
SANS_R = lambda s: F("LiberationSans-Regular.ttf", s)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, max_w, fill, leading=None):
    lines = wrap(draw, text, font, max_w)
    lh = leading if leading is not None else int(font.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y, len(lines)


def fit_lines(draw, text, font, max_w, max_lines):
    """Wrap text; if it exceeds max_lines, shorten with ellipsis."""
    lines = wrap(draw, text, font, max_w)
    while len(lines) > max_lines and len(text) > 10:
        new = text.rsplit(" ", 1)[0] + " …"
        if new == text:  # lone "…" line: trimming cannot shorten further
            break
        text = new
        lines = wrap(draw, text, font, max_w)
    return lines


def text_lines(draw, x, y, lines, font, fill, leading=None):
    lh = leading if leading is not None else int(font.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def rule(draw, x, y, w, fill=INK, width=2):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


# ---------------------------------------------------------------- world map
# Coarse continent outlines in (lon, lat), drawn from general knowledge.
# The map is a small locator: shapes are approximate, dots are approximate.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 24),
     (-115, 30), (-120, 34), (-125, 40), (-125, 48), (-130, 55),
     (-145, 60), (-158, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-25, 76),
     (-40, 78), (-58, 75), (-60, 70)],
    # South America
    [(-80, 10), (-75, 5), (-70, 10), (-60, 5), (-50, 0), (-40, -5),
     (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-65, -40),
     (-70, -50), (-73, -40), (-75, -30), (-80, -20), (-80, -10), (-80, 0)],
    # Africa
    [(-10, 35), (-5, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 12), (45, 5), (40, -5), (40, -15),
     (35, -25), (30, -35), (20, -35), (15, -27), (12, -18), (8, -5),
     (0, 0), (-8, 5), (-15, 10), (-17, 15), (-15, 25)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (25, 65), (20, 70), (15, 70), (10, 68), (5, 60), (5, 58), (0, 55),
     (-5, 50), (-10, 45), (-10, 38)],
    # Asia
    [(30, 62), (40, 68), (55, 70), (70, 72), (90, 75), (110, 74),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 55),
     (155, 50), (145, 45), (140, 40), (135, 35), (130, 33), (127, 35),
     (122, 38), (120, 32), (115, 25), (110, 20), (105, 15), (100, 10),
     (95, 15), (90, 22), (85, 20), (80, 15), (77, 8), (75, 12),
     (72, 20), (66, 25), (60, 25), (55, 26), (50, 28), (48, 30),
     (45, 32), (40, 35), (35, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (140, -12), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 36), (141, 38),
     (142, 42), (144, 44), (142, 45), (140, 42), (138, 38), (135, 35),
     (132, 33)],
    # Indonesia (rough)
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -5), (135, -4), (140, -8), (138, -7), (132, -3),
     (128, 0), (122, 0), (118, 0), (112, -2), (105, -3), (100, 2)],
]

# Story dots: (number, lat, lon, nudge_dx_px, nudge_dy_px).
# Nudges keep close dots apart; a thin line links a nudged dot to its place.
# Middle East is crowded (Cairo/Gaza/Tehran/Ras Tanura/Hormuz): Cairo goes
# down-left, Gaza up-right, Ras Tanura down-left, Hormuz up-right. Moscow
# is nudged off Kyiv; the second New York dot off the first. Shanghai is
# nudged off Beijing; the two-digit dots use a slightly larger circle.
DOTS = [
    (1, 38.9, -77.0, -14, -10),  # Washington — nudged off New York
    (2, 30.0, 31.2, -18, 12),    # Cairo — nudged down-left off Gaza
    (3, 26.5, 56.3, 16, -6),     # Strait of Hormuz — nudged off Tehran
    (4, 39.9, 116.4, 0, 0),      # Beijing — Tiangong
    (5, 26.6, 50.2, -12, 8),     # Ras Tanura — nudged down-left
    (6, 40.7, -74.0, 0, 0),      # New York — Nasdaq
    (7, 50.4, 30.5, -10, 6),     # Kyiv — nudged off Moscow
    (8, 35.7, 51.4, 0, 0),       # Tehran — US warning
    (9, 31.5, 34.5, 26, -20),    # Gaza — nudged up-right off Cairo
    (10, 55.8, 37.6, 12, -8),    # Moscow — nudged off Kyiv
    (11, 50.8, 4.4, 0, 0),       # Brussels — EU budget
    (12, -9.6, 160.0, 0, 0),     # Honiara — Solomon Islands treaty
    (13, 40.7, -74.0, 14, -10),  # New York — Macy's parade, nudged off 6
    (14, -2.9, 23.7, 0, 0),      # DR Congo — Ebola outbreak
    (15, 13.75, 100.5, 0, 0),    # Bangkok — refinery fire
    (16, -33.9, 18.4, 0, 0),     # Cape Town — Ramaphosa ruling
    (17, 31.2, 121.5, 14, 10),   # Shanghai — party chief probe, off Beijing
    (18, -35.3, 149.1, 0, 0),    # Canberra — climate target miss
]


def draw_map(d, x0, y0, w, h):
    """Equirectangular locator map with numbered story dots."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=INK, width=1)

    def proj(lon, lat):
        px = x0 + (lon + 170.0) / 360.0 * w
        py = y0 + (75.0 - lat) / 130.0 * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=INK)
    for num, lat, lon, ndx, ndy in DOTS:
        px, py = proj(lon, lat)
        cx, cy = px + ndx, py + ndy
        if ndx or ndy:
            d.line([(px, py), (cx, cy)], fill=RED, width=1)
        r = 7 if num >= 10 else 6
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        fs = 8 if num >= 10 else 9
        tw = d.textlength(str(num), font=SANS_B(fs))
        d.text((cx - tw / 2, cy - fs / 2 - 1), str(num), font=SANS_B(fs),
               fill=(255, 255, 255))


# ---------------------------------------------------------------- illustrations
# All flat-colour, drawn in code. Each takes the panel's draw object and box.

def illu_tariffs(d, x, y, w, h):
    """Container ship on the sea with a tariff badge."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 238))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(58, 110, 160))
    for i in range(5):
        d.line([(x + 8 + i * 22, y + h * 0.62), (x + 8 + i * 22, y + h)],
               fill=(40, 85, 130), width=1)
    # hull
    d.polygon([(x + 12, y + h * 0.55), (x + w - 12, y + h * 0.55),
               (x + w - 34, y + h * 0.80), (x + 34, y + h * 0.80)],
              fill=(30, 30, 30))
    d.rectangle([x + 12, y + h * 0.55, x + w - 12, y + h * 0.60],
                fill=(176, 30, 36))
    # containers
    cols = [(176, 30, 36), (31, 78, 121), (46, 125, 50), (201, 162, 39),
            (107, 63, 160), (15, 118, 110)]
    cw = (w - 40) / 6.0
    for i, c in enumerate(cols):
        cx = x + 20 + i * cw
        d.rectangle([cx, y + h * 0.30, cx + cw - 3, y + h * 0.55], fill=c,
                    outline=INK, width=1)
        d.rectangle([cx, y + h * 0.18, cx + cw - 3, y + h * 0.30], fill=c,
                    outline=INK, width=1)
    # bridge tower
    d.rectangle([x + w - 52, y + h * 0.22, x + w - 22, y + h * 0.55],
                fill=(240, 240, 235), outline=INK, width=1)
    for j in range(3):
        d.rectangle([x + w - 48, y + h * 0.26 + j * 10,
                     x + w - 26, y + h * 0.26 + j * 10 + 6],
                    fill=(31, 78, 121))
    # tariff badge
    bx, by, br = x + w - 46, y + 34, 26
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED,
              outline=(255, 255, 255), width=2)
    tw = d.textlength("%", font=SERIF_B(34))
    d.text((bx - tw / 2, by - 22), "%", font=SERIF_B(34),
           fill=(255, 255, 255))


def illu_cairo(d, x, y, w, h):
    """Ring road at dusk: tanker truck, flames, smoke."""
    d.rectangle([x, y, x + w, y + h * 0.55], fill=(64, 48, 74))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(40, 40, 44))
    # low sun
    d.ellipse([x + w - 62, y + 12, x + w - 22, y + 52], fill=(245, 180, 80))
    # skyline
    for i, bh in enumerate([26, 40, 22, 48, 30, 44, 20]):
        bx = x + 8 + i * 46
        d.rectangle([bx, y + h * 0.55 - bh, bx + 34, y + h * 0.55],
                    fill=(30, 26, 40))
        for wy in range(2):
            d.rectangle([bx + 6, y + h * 0.55 - bh + 6 + wy * 12,
                         bx + 12, y + h * 0.55 - bh + 11 + wy * 12],
                        fill=(245, 200, 60))
    # road
    d.polygon([(x, y + h), (x + w * 0.32, y + h * 0.58),
               (x + w * 0.68, y + h * 0.58), (x + w, y + h)],
              fill=(70, 70, 76))
    d.line([(x + w * 0.47, y + h * 0.60), (x + w * 0.50, y + h)],
           fill=(245, 200, 60), width=2)
    # tanker: cylinder + cab
    tx, ty = x + w * 0.42, y + h * 0.60
    d.rounded_rectangle([tx, ty, tx + 96, ty + 30], radius=14,
                        fill=(200, 200, 200), outline=INK, width=1)
    d.polygon([(tx + 96, ty + 4), (tx + 128, ty + 10), (tx + 128, ty + 30),
               (tx + 96, ty + 30)], fill=(176, 30, 36), outline=INK)
    d.rectangle([tx + 8, ty + 30, tx + 20, ty + 38], fill=INK)
    d.rectangle([tx + 78, ty + 30, tx + 90, ty + 38], fill=INK)
    d.rectangle([tx + 112, ty + 30, tx + 122, ty + 38], fill=INK)
    # flames
    fx, fy = tx + 40, ty - 6
    d.polygon([(fx - 26, fy + 8), (fx - 10, fy - 26), (fx, fy - 6),
               (fx + 12, fy - 30), (fx + 26, fy + 8)], fill=ORANGE)
    d.polygon([(fx - 14, fy + 8), (fx - 4, fy - 14), (fx + 4, fy - 2),
               (fx + 14, fy + 8)], fill=YELLOW)
    # smoke
    for sx, sy, sr in [(tx - 6, ty - 34, 10), (tx + 8, ty - 48, 13),
                       (tx + 26, ty - 60, 10)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 120, 125))


def illu_space(d, x, y, w, h):
    """Tiangong over the Earth's limb, stars, one astronaut."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 28))
    import random
    rnd = random.Random(2611)
    for _ in range(46):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.55
        sr = 1 if rnd.random() < 0.7 else 2
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(255, 255, 255))
    # Earth limb
    d.ellipse([x - w * 0.45, y + h * 0.62, x + w * 1.45, y + h * 2.1],
              fill=(42, 110, 180))
    d.ellipse([x + w * 0.10, y + h * 0.70, x + w * 0.34, y + h * 0.86],
              fill=(70, 150, 90))
    d.ellipse([x + w * 0.55, y + h * 0.78, x + w * 0.78, y + h * 0.92],
              fill=(70, 150, 90))
    d.arc([x - w * 0.45, y + h * 0.62, x + w * 1.45, y + h * 2.1],
          start=200, end=340, fill=(150, 210, 240), width=3)
    # station: core module + panels
    cx, cy = x + w * 0.52, y + h * 0.34
    d.rectangle([cx - 88, cy - 12, cx - 18, cy + 12], fill=(31, 78, 121),
                outline=(255, 255, 255), width=1)
    d.rectangle([cx + 18, cy - 12, cx + 88, cy + 12], fill=(31, 78, 121),
                outline=(255, 255, 255), width=1)
    for gx in range(-88, 88, 14):
        if -18 < gx < 18:
            continue
        d.line([(cx + gx, cy - 12), (cx + gx, cy + 12)],
               fill=(150, 200, 240), width=1)
    d.rounded_rectangle([cx - 18, cy - 16, cx + 18, cy + 16], radius=8,
                        fill=(220, 220, 215), outline=INK, width=1)
    d.ellipse([cx - 30, cy - 8, cx - 18, cy + 8], fill=(200, 200, 200),
              outline=INK, width=1)
    # astronaut on a tether
    ax, ay = x + w * 0.78, y + h * 0.52
    d.line([(cx + 14, cy + 14), (ax, ay - 12)], fill=(255, 255, 255),
           width=1)
    d.ellipse([ax - 7, ay - 16, ax + 7, ay - 2], fill=(255, 255, 255),
              outline=INK, width=1)
    d.rounded_rectangle([ax - 6, ay - 2, ax + 6, ay + 12], radius=3,
                        fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([ax - 9, ay + 12, ax - 4, ay + 20], fill=(255, 255, 255),
                outline=INK, width=1)
    d.rectangle([ax + 4, ay + 12, ax + 9, ay + 20], fill=(255, 255, 255),
                outline=INK, width=1)


def illu_hormuz(d, x, y, w, h):
    """Strait of Hormuz at night: tanker, mine blast, smoke, warning mine."""
    d.rectangle([x, y, x + w, y + h * 0.52], fill=(24, 32, 58))
    d.rectangle([x, y + h * 0.52, x + w, y + h], fill=(16, 54, 86))
    # moon
    d.ellipse([x + w - 56, y + 10, x + w - 26, y + 40], fill=(240, 230, 200))
    # distant shore lights
    for lx in range(10, int(w) - 10, 26):
        d.rectangle([x + lx, y + h * 0.48, x + lx + 6, y + h * 0.52],
                    fill=(245, 200, 60))
    # tanker hull
    d.polygon([(x + 14, y + h * 0.60), (x + w - 14, y + h * 0.60),
               (x + w - 44, y + h * 0.86), (x + 44, y + h * 0.86)],
              fill=(20, 20, 24))
    d.rectangle([x + 14, y + h * 0.60, x + w - 14, y + h * 0.66],
                fill=(176, 30, 36))
    # deck tanks: three low steel drums sitting on the deck line
    for i in range(3):
        tx = x + 40 + i * 72
        d.rounded_rectangle([tx, y + h * 0.50, tx + 58, y + h * 0.60],
                            radius=8, fill=(150, 158, 168), outline=INK,
                            width=2)
        d.line([(tx + 8, y + h * 0.53), (tx + 50, y + h * 0.53)],
               fill=(110, 118, 128), width=1)
    # bridge tower
    d.rectangle([x + w - 58, y + h * 0.34, x + w - 26, y + h * 0.60],
                fill=(240, 240, 235), outline=INK, width=1)
    # blast above the middle tank
    bx, by = x + w * 0.46, y + h * 0.46
    d.polygon([(bx - 40, by + 12), (bx - 16, by - 40), (bx, by - 10),
               (bx + 18, by - 46), (bx + 40, by + 12)], fill=ORANGE)
    d.polygon([(bx - 22, by + 12), (bx - 8, by - 22), (bx + 8, by - 2),
               (bx + 22, by + 12)], fill=YELLOW)
    # smoke
    for sx, sy, sr in [(bx - 34, by - 40, 13), (bx + 4, by - 58, 16),
                       (bx + 38, by - 42, 12)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(90, 90, 96))
    # spiked mine, lower right
    mx, my = x + w - 42, y + h - 26
    d.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=(30, 30, 34),
              outline=(255, 255, 255), width=1)
    for ang in range(0, 360, 45):
        import math
        ex = mx + 17 * math.cos(math.radians(ang))
        ey = my + 17 * math.sin(math.radians(ang))
        d.line([(mx, my), (ex, ey)], fill=(30, 30, 34), width=2)
    # sea lines
    for wy in (0.70, 0.80, 0.92):
        d.line([(x + 10, y + h * wy), (x + w - 10, y + h * wy)],
               fill=(90, 140, 190), width=1)


def illu_mini_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 44, 60))
    d.rectangle([x + 8, y + h - 26, x + 30, y + h], fill=(90, 80, 100))
    d.rectangle([x + 40, y + h - 38, x + 56, y + h], fill=(90, 80, 100))
    d.ellipse([x + w - 34, y + h - 24, x + w - 8, y + h], fill=(120, 110, 130))
    d.polygon([(x + 62, y + h - 8), (x + 70, y + h - 30), (x + 78, y + h - 8)],
              fill=ORANGE)
    d.polygon([(x + 66, y + h - 8), (x + 70, y + h - 20), (x + 74, y + h - 8)],
              fill=YELLOW)
    d.ellipse([x + w - 46, y + 6, x + w - 34, y + 18], fill=(245, 200, 60))


def illu_mini_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 44))
    pts = [(x + 6, y + 12), (x + 30, y + 16), (x + 54, y + 12),
           (x + 78, y + 22), (x + 102, y + 26), (x + 126, y + 34),
           (x + 150, y + 40), (x + 174, y + 46)]
    d.line(pts, fill=(230, 60, 50), width=3, joint="curve")
    d.polygon([(x + 164, y + 38), (x + 182, y + 42), (x + 168, y + 52)],
              fill=(230, 60, 50))
    d.text((x + 8, y + h - 20), "–20%", font=SANS_B(16), fill=(255, 255, 255))


def illu_mini_jet(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 230))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(90, 90, 90))
    d.line([(x, y + h - 16), (x + w, y + h - 16)], fill=(255, 255, 255),
           width=1)
    # jet silhouette
    jx, jy = x + 40, y + 22
    d.polygon([(jx, jy), (jx + 90, jy + 6), (jx + 96, jy + 10),
               (jx + 40, jy + 12), (jx + 34, jy + 22), (jx + 26, jy + 12),
               (jx + 8, jy + 10)], fill=(40, 40, 44))
    # burst
    bx, by = x + w - 30, y + 16
    for ang in range(0, 360, 45):
        import math
        ex = bx + 12 * math.cos(math.radians(ang))
        ey = by + 12 * math.sin(math.radians(ang))
        d.line([(bx, by), (ex, ey)], fill=ORANGE, width=2)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=YELLOW)


def illu_mini_warning(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 78, 121))
    cx, cy = x + w // 2, y + h // 2 + 2
    d.polygon([(cx, cy - 22), (cx + 24, cy + 16), (cx - 24, cy + 16)],
              fill=YELLOW, outline=INK)
    d.text((cx - 3, cy - 12), "!", font=SANS_B(22), fill=INK)
    d.text((x + 8, y + 4), "LEAVE", font=SANS_B(11), fill=(255, 255, 255))


def illu_mini_skyline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 200, 170))
    for i, bh in enumerate([18, 30, 14, 26, 20]):
        bx = x + 10 + i * 36
        d.rectangle([bx, y + h - bh, bx + 28, y + h], fill=(70, 60, 66))
    d.ellipse([x + w - 52, y + 4, x + w - 30, y + 26], fill=(150, 150, 155))
    d.ellipse([x + w - 44, y + 12, x + w - 22, y + 34], fill=(170, 170, 175))
    d.ellipse([x + w - 58, y + 16, x + w - 38, y + 36], fill=(150, 150, 155))


def illu_mini_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 78, 121))
    import math
    cx, cy = x + 44, y + h // 2
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx = cx + 24 * math.cos(ang)
        sy = cy + 24 * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=YELLOW)
    d.text((x + 82, y + h // 2 - 14), "€2tn", font=SERIF_B(26),
           fill=(255, 255, 255))


def illu_mini_bank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.polygon([(x + 20, y + 8), (x + w // 2, y + 22), (x + w - 20, y + 8)],
              fill=(120, 40, 40))
    for i in range(4):
        bx = x + 30 + i * 36
        d.rectangle([bx, y + 24, bx + 14, y + h - 8], fill=(220, 220, 215),
                    outline=INK, width=1)
    d.rectangle([x + 18, y + h - 10, x + w - 18, y + h - 4], fill=(120, 40, 40))
    d.polygon([(x + w - 46, y + 12), (x + w - 30, y + 12), (x + w - 30, y + 22),
               (x + w - 46, y + 22)], fill=GREEN)
    d.text((x + w - 44, y + h - 26), "3.25%", font=SANS_B(13), fill=GREEN)


def illu_mini_balloon(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 230))
    d.ellipse([x + w - 70, y + 2, x + w - 34, y + 22], fill=(150, 150, 155))
    d.ellipse([x + w - 52, y + 10, x + w - 22, y + 28], fill=(170, 170, 175))
    bx, by = x + 52, y + 20
    d.ellipse([bx - 22, by - 14, bx + 22, by + 14], fill=RED, outline=INK,
              width=1)
    d.line([(bx - 14, by + 12), (bx - 8, by + 26)], fill=INK, width=1)
    d.line([(bx + 14, by + 12), (bx + 8, by + 26)], fill=INK, width=1)
    d.rectangle([bx - 10, by + 26, bx + 10, by + 34], fill=BROWN,
                outline=INK, width=1)


def illu_mini_candle(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 44, 60))
    for i, bh in enumerate([20, 34, 16, 30, 22]):
        bx = x + 12 + i * 36
        d.rectangle([bx, y + h - bh, bx + 28, y + h], fill=(30, 28, 40))
        for wy in range(2):
            d.rectangle([bx + 6, y + h - bh + 5 + wy * 10,
                         bx + 11, y + h - bh + 9 + wy * 10],
                        fill=(245, 200, 60))
    cx, cy = x + w - 44, y + 22
    d.ellipse([cx - 8, cy - 12, cx + 8, cy + 6], fill=ORANGE)
    d.ellipse([cx - 4, cy - 6, cx + 4, cy + 6], fill=YELLOW)
    d.rectangle([cx - 6, cy + 6, cx + 6, cy + 20], fill=(240, 240, 235))


def illu_mini_mountains(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 238))
    d.polygon([(x, y + h), (x + 50, y + 10), (x + 100, y + h)],
              fill=(90, 110, 140))
    d.polygon([(x + 40, y + 22), (x + 50, y + 10), (x + 60, y + 22)],
              fill=(255, 255, 255))
    d.polygon([(x + 80, y + h), (x + 140, y + 18), (x + 190, y + h)],
              fill=(70, 90, 120))
    d.polygon([(x + 130, y + 30), (x + 140, y + 18), (x + 150, y + 30)],
              fill=(255, 255, 255))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(58, 110, 160))
    d.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(255, 255, 255),
           width=1)


def illu_mini_space(d, x, y, w, h):
    """Compact Tiangong: night sky, station, Earth arc."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 28))
    import random
    rnd = random.Random(2611)
    for _ in range(16):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.5
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    d.ellipse([x - w * 0.3, y + h * 0.62, x + w * 1.3, y + h * 2.0],
              fill=(42, 110, 180))
    cx, cy = x + w * 0.5, y + h * 0.34
    d.rectangle([cx - 52, cy - 6, cx - 10, cy + 6], fill=(31, 78, 121),
                outline=(255, 255, 255), width=1)
    d.rectangle([cx + 10, cy - 6, cx + 52, cy + 6], fill=(31, 78, 121),
                outline=(255, 255, 255), width=1)
    d.rounded_rectangle([cx - 10, cy - 9, cx + 10, cy + 9], radius=4,
                        fill=(220, 220, 215), outline=INK, width=1)


def illu_mini_russia(d, x, y, w, h):
    """Record budget: dark red, gold star, rising bars."""
    d.rectangle([x, y, x + w, y + h], fill=(96, 16, 20))
    cx, cy = x + 26, y + 16
    d.polygon([(cx, cy - 10), (cx + 3, cy - 2), (cx + 11, cy - 2),
               (cx + 5, cy + 3), (cx + 7, cy + 11), (cx, cy + 6),
               (cx - 7, cy + 11), (cx - 5, cy + 3), (cx - 11, cy - 2),
               (cx - 3, cy - 2)], fill=GOLD)
    for i, bh in enumerate([10, 16, 24, 32]):
        bx = x + 58 + i * 32
        d.rectangle([bx, y + h - 8 - bh, bx + 20, y + h - 8], fill=GOLD)
    d.text((x + 58, y + 4), "$609bn", font=SANS_B(15), fill=(255, 255, 255))


def illu_mini_treaty(d, x, y, w, h):
    """Two flags over a Pacific sea: Solomon Islands + Australia."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 205, 230))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(58, 110, 160))
    # left flag: blue field, yellow diagonal, white stars
    fx, fy = x + 34, y + 8
    d.polygon([(fx, fy), (fx + 52, fy), (fx + 52, fy + 26), (fx, fy + 26)],
              fill=(31, 78, 121), outline=INK, width=1)
    d.polygon([(fx, fy + 26), (fx + 52, fy), (fx + 52, fy + 7),
               (fx, fy + 26)], fill=YELLOW)
    for sx, sy in [(fx + 10, fy + 6), (fx + 22, fy + 10), (fx + 14, fy + 18)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    d.line([(fx, fy), (fx, y + h - 14)], fill=INK, width=2)
    # right flag: dark blue, white stars
    gx, gy = x + w - 88, y + 8
    d.polygon([(gx, gy), (gx + 52, gy), (gx + 52, gy + 26), (gx, gy + 26)],
              fill=(18, 38, 66), outline=INK, width=1)
    for sx, sy in [(gx + 12, gy + 7), (gx + 26, gy + 13), (gx + 40, gy + 7),
                   (gx + 19, gy + 19), (gx + 33, gy + 19)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    d.line([(gx + 52, gy), (gx + 52, y + h - 14)], fill=INK, width=2)


def illu_mini_ebola(d, x, y, w, h):
    """Ebola outbreak: deep green, white medical cross, red virus dots."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 60, 44))
    # big white cross in a circle, left
    cx, cy = x + 30, y + h // 2
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 255, 255),
              outline=INK, width=1)
    d.rectangle([cx - 3, cy - 11, cx + 3, cy + 11], fill=RED)
    d.rectangle([cx - 11, cy - 3, cx + 11, cy + 3], fill=RED)
    # virus: red spiked circles, right
    import math
    for vx, vy, vr in [(x + w - 70, y + 12, 8), (x + w - 40, y + 24, 6),
                       (x + w - 88, y + 28, 5)]:
        d.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=(230, 60, 50))
        for ang in range(0, 360, 45):
            ex = vx + (vr + 4) * math.cos(math.radians(ang))
            ey = vy + (vr + 4) * math.sin(math.radians(ang))
            d.line([(vx, vy), (ex, ey)], fill=(230, 60, 50), width=1)
    d.text((x + 58, y + h - 16), "12,000", font=SANS_B(13),
           fill=(255, 255, 255))


def illu_mini_bangkok_fire(d, x, y, w, h):
    """Bangkok refinery fire at night: tanks, flames, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 32, 52))
    d.rectangle([x + 10, y + h - 18, x + 46, y + h], fill=(90, 80, 100))
    d.ellipse([x + 58, y + h - 16, x + 92, y + h], fill=(120, 110, 130))
    d.rectangle([x + 104, y + h - 24, x + 126, y + h], fill=(90, 80, 100))
    # flames
    fx, fy = x + 76, y + h - 16
    d.polygon([(fx - 18, fy), (fx - 8, fy - 20), (fx, fy - 6),
               (fx + 10, fy - 24), (fx + 18, fy)], fill=ORANGE)
    d.polygon([(fx - 9, fy), (fx - 3, fy - 11), (fx + 3, fy - 2),
               (fx + 9, fy)], fill=YELLOW)
    # smoke
    for sx, sy, sr in [(fx - 12, fy - 24, 6), (fx + 6, fy - 30, 8)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 120, 125))
    d.ellipse([x + w - 30, y + 5, x + w - 16, y + 19], fill=(245, 200, 60))


def illu_mini_court(d, x, y, w, h):
    """Cape Town court: cream facade, columns, red pediment."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.polygon([(x + 14, y + 6), (x + w // 2, y + 18), (x + w - 14, y + 6)],
              fill=(138, 22, 28))
    for i in range(4):
        bx = x + 28 + i * 40
        d.rectangle([bx, y + 20, bx + 12, y + h - 6], fill=(220, 220, 215),
                    outline=INK, width=1)
    d.rectangle([x + 14, y + h - 8, x + w - 14, y + h - 2], fill=(138, 22, 28))


def illu_mini_shanghai(d, x, y, w, h):
    """Shanghai at dusk: tower silhouettes, pearl tower, search beam."""
    d.rectangle([x, y, x + w, y + h], fill=(28, 36, 64))
    for i, bh in enumerate([16, 26, 12, 22, 18]):
        bx = x + 8 + i * 22
        d.rectangle([bx, y + h - bh, bx + 16, y + h], fill=(16, 22, 40))
        d.rectangle([bx + 3, y + h - bh + 3, bx + 6, y + h - bh + 6],
                    fill=(245, 200, 60))
    # pearl tower: spire + two spheres
    tx = x + w - 44
    d.line([(tx, y + 4), (tx, y + h)], fill=(200, 200, 200), width=2)
    d.ellipse([tx - 8, y + 8, tx + 8, y + 24], fill=(245, 200, 60))
    d.ellipse([tx - 6, y + 24, tx + 6, y + 36], fill=(200, 200, 200))
    # search beam
    d.polygon([(tx, y + 6), (x + w - 4, y + 2), (x + w - 4, y + 10)],
              fill=(245, 230, 150))


def illu_mini_climate(d, x, y, w, h):
    """Climate target missed: pale sky, big thermometer, falling arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 238))
    d.ellipse([x + w - 44, y + 4, x + w - 20, y + 28], fill=(245, 200, 60))
    # thermometer: tube + bulb, mercury low
    tx = x + 34
    d.rounded_rectangle([tx - 5, y + 6, tx + 5, y + h - 14], radius=5,
                        fill=(255, 255, 255), outline=INK, width=1)
    d.ellipse([tx - 10, y + h - 22, tx + 10, y + h - 2], fill=RED,
              outline=INK, width=1)
    d.rectangle([tx - 3, y + h - 20, tx + 3, y + h - 12], fill=RED)
    # falling arrow
    ax = x + w - 78
    d.line([(ax, y + 8), (ax, y + h - 14)], fill=(176, 30, 36), width=3)
    d.polygon([(ax - 8, y + h - 22), (ax + 8, y + h - 22), (ax, y + h - 8)],
              fill=(176, 30, 36))
    d.text((x + 56, y + 4), "2035", font=SANS_B(15), fill=(26, 26, 26))


def clipped_art(art, w, h):
    """Render an illustration on its own layer so it can never spill
    past its panel and cover neighbouring text."""
    layer = Image.new("RGB", (int(w), int(h)), PAPER)
    ld = ImageDraw.Draw(layer)
    art(ld, 0, 0, w, h)
    return layer


# ---------------------------------------------------------------- content
# Every fact below was checked against the 26 November 2026 day page
# (One Turn, 51 stories + 17 in brief, sourced to BBC, Reuters, The
# Guardian, Al Jazeera, Euronews, Yonhap, CBC) and the Reuters world news
# summary of the same day. New v3 stories are marked NEW.

LEADS = [
    {
        "num": 1, "kicker": "WASHINGTON · TRADE", "art": illu_tariffs,
        "head": "US proposes tariffs on 14 partners",
        "deck": "India 25%, Japan 15%, China 20%. The EU rejects the "
                "premise; Brazil calls it unacceptable.",
        "src": "BBC · France 24",
    },
    {
        "num": 2, "kicker": "CAIRO · DISASTER", "art": illu_cairo,
        "head": "Tanker fire kills at least 31 on Cairo ring road",
        "deck": "A tanker overturned and burst into flames. Cars burned; "
                "21 hurt, no cause given.",
        "src": "BBC · The Guardian",
    },
    {
        "num": 3, "kicker": "HORMUZ · ESCALATION", "art": illu_hormuz,
        "head": "Two ships hit mines in the Strait of Hormuz",
        "deck": "A supertanker carrying 2m barrels hit near Khasab. "
                "Israel says it is ready to strike Iran.",
        "src": "Al Jazeera · Reuters",
    },
]

MINIS = [
    {"num": 4, "kicker": "TIANGONG · SPACE", "art": illu_mini_space,
     "head": "First foreign astronaut boards Tiangong",
     "deck": "Pakistan's Zeeshan Ali joins the Shenzhou-24 crew. — BBC"},
    {"num": 5, "kicker": "RIYADH · CONFLICT", "art": illu_mini_refinery,
     "head": "Houthis hit Saudi ports and refinery",
     "deck": "Riyadh says it downed drones and missiles; oil rose. — Al Jazeera"},
    {"num": 6, "kicker": "NEW YORK · MARKETS", "art": illu_mini_chart,
     "head": "Nasdaq nears bear market in AI sell-off",
     "deck": "S&P 500 fell 0.25%; Nvidia slid on Huang questions. — Sky News"},
    {"num": 7, "kicker": "KYIV · WAR", "art": illu_mini_jet,
     "head": "Ukraine hits airbase; Kyiv hit by missiles",
     "deck": "Five jets hit at Savasleyka; a mall hit in Kyiv. — BBC"},
    {"num": 8, "kicker": "TEHRAN · WARNING", "art": illu_mini_warning,
     "head": "US tells citizens to leave Iran",
     "deck": "Kushner confirmed meeting Iranian envoys. — Euronews"},
    {"num": 9, "kicker": "GAZA CITY · CONFLICT", "art": illu_mini_skyline,
     "head": "Israeli strikes kill Hamas security chief",
     "deck": "Mohammed Abu al-Ouf killed; 11 more dead. — BBC"},
    {"num": 10, "kicker": "MOSCOW · BUDGET", "art": illu_mini_russia,
     "head": "Russia approves record military budget",
     "deck": "$609bn defence plan, most since Soviet times. — Washington Post"},
    {"num": 11, "kicker": "BRUSSELS · EUROPE", "art": illu_mini_eu,
     "head": "EU leaders meet over €2tn long-term budget",
     "deck": "A deal is far from certain; Germany presses limits. — RFI"},
    {"num": 12, "kicker": "HONIARA · PACIFIC", "art": illu_mini_treaty,
     "head": "Solomon Islands signs Australia treaty",
     "deck": "A new security treaty with Australia in the Pacific. — 10 Things"},
    {"num": 13, "kicker": "NEW YORK · THANKSGIVING", "art": illu_mini_balloon,
     "head": "Macy's postpones Thanksgiving parade",
     "deck": "The 100th parade moves to Saturday on storm winds. — BBC"},
    {"num": 14, "kicker": "DR CONGO · HEALTH", "art": illu_mini_ebola,
     "head": "DR Congo Ebola cases pass 12,000",
     "deck": "Worst outbreak on record passes 12,000 cases. — One Turn"},
    {"num": 15, "kicker": "BANGKOK · DISASTER", "art": illu_mini_bangkok_fire,
     "head": "Bangkok refinery fire injures seven",
     "deck": "Blast and fire at a Bangchak plant in east Bangkok. — One Turn"},
    {"num": 16, "kicker": "CAPE TOWN · JUSTICE", "art": illu_mini_court,
     "head": "Court throws out Ramaphosa report",
     "deck": "Judges void the report behind the impeachment push. — One Turn"},
    {"num": 17, "kicker": "SHANGHAI · POLITICS", "art": illu_mini_shanghai,
     "head": "China probes Shanghai party chief",
     "deck": "Shanghai's top official under investigation. — One Turn"},
    {"num": 18, "kicker": "CANBERRA · CLIMATE", "art": illu_mini_climate,
     "head": "Australia set to miss 2035 climate target",
     "deck": "Canberra's own projections show the 2035 goal slipping. — One Turn"},
]

ALSO = [
    "Asian stocks rebound as tariffs look milder",
    "King tides flood the California coast; pier collapses",
    "Bank of Korea raises rate to 3.25%",
    "Hong Kong marks a year since fire killed 168",
    "Nepal: 213 Indians missing presumed dead",
    "UK net migration falls to 77,000, lowest since 1997",
    "Germany arrests two over synagogue attack plot",
    "Memory-chip shortage triples some RAM prices",
    "Gold slumps to 15-month low on Fed hike bets",
    "Indonesia gold mine flood kills at least 13",
    "ISIL attack kills two in north-east Syria",
    "Brazil pulls its ambassador from Argentina",
    "Iraq court takes control of Kurdistan oil",
    "UK acts on drone threat to airbases",
    "Flinders Island fire destroys at least six homes",
    "Spain votes Sunday, with the right favoured",
    "Sudan drone attacks kill at least 15",
    "Canary Islands: 2,000 migrants in a day",
    "UK energy bills to rise 26% in January",
    "Pig-kidney patient a year off dialysis",
    "Euclid telescope finds its first comet",
    "Duran Duran guitarist Andy Taylor dies",
]

REGIONS = [
    ("ASIA-PACIFIC", 7, "7", "stories today", BLUE),
    ("EUROPE", 10, "€2tn", "EU budget talks", (107, 63, 160)),
    ("AMERICAS", 7, "–20%", "Nasdaq nears bear", TEAL),
    ("MIDDLE EAST", 6, "2", "ships hit by mines", DARKRED),
    ("AFRICA", 5, "12,000", "Ebola cases", BROWN),
    ("OCEANIA", 3, "3", "treaty + fire + target", GREEN),
    ("WORLDWIDE", 2, "14", "partners face tariffs", GREY),
]

DATE_CHECK = ("DATE CHECK — Every story here happened, or was first "
              "reported, on Thursday 26 November 2026. LEFT OUT: Huawei "
              "verdict, Senegal's Cup title, Huang's Nvidia return (all "
              "Tue 24 Nov); SpaceX satellites, Kim's nuclear vow, "
              "Colombia hostages, Netanyahu case (all Wed 25 Nov).")

SOURCES = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, The Guardian, "
           "Euronews, Yonhap, CBC, BBC Science, One Turn · Pictures and "
           "map: original, drawn in code · 2026-11-26")


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14
    CW = W - 2 * M  # 996

    # outer border
    d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=2)

    # ---- masthead
    d.text((M, 10), "THE WORLD IN ONE DAY", font=SANS_B(20), fill=RED)
    rt = "THURSDAY'S NEWS · ONE PAGE · 40 STORIES"
    d.text((W - M - d.textlength(rt, font=SANS_R(13)), 13), rt,
           font=SANS_R(13), fill=INK)
    dt = "Thursday 26 November 2026"
    dw = d.textlength(dt, font=SERIF_B(62))
    d.text(((W - dw) / 2, 30), dt, font=SERIF_B(62), fill=INK)
    sub = ("US tariffs hit 14 partners · Cairo tanker fire kills 31 · "
           "Two ships hit mines in Hormuz")
    sw = d.textlength(sub, font=SERIF_I(21))
    d.text(((W - sw) / 2, 102), sub, font=SERIF_I(21), fill=RED)
    rule(d, M, 128, CW, fill=RED, width=3)

    # ---- region strip
    y0, rh = 134, 52
    cw = CW / 7.0
    for i, (name, count, big, label, col) in enumerate(REGIONS):
        x = M + i * cw
        d.rectangle([x + 1, y0, x + cw - 1, y0 + rh], fill=CARD_BG,
                    outline=INK, width=1)
        d.rectangle([x + 1, y0, x + cw - 1, y0 + 16], fill=col)
        nw = d.textlength(name, font=SANS_B(10))
        d.text((x + (cw - nw) / 2, y0 + 3), name, font=SANS_B(10),
               fill=(255, 255, 255))
        bw = d.textlength(big, font=SERIF_B(22))
        d.text((x + (cw - bw) / 2, y0 + 17), big, font=SERIF_B(22),
               fill=INK)
        lw = d.textlength(label, font=SANS_R(9))
        d.text((x + (cw - lw) / 2, y0 + 41), label, font=SANS_R(9),
               fill=GREY)

    # ---- lead cards
    ly, lh = 188, 240
    lw3 = (CW - 2 * 9) / 3.0
    for i, lead in enumerate(LEADS):
        x = M + i * (lw3 + 9)
        d.rectangle([x, ly, x + lw3, ly + lh], fill=CARD_BG, outline=INK,
                    width=1)
        img.paste(clipped_art(lead["art"], lw3 - 2, 100), (int(x + 1),
                                                           ly + 1))
        d.rectangle([x, ly + 101, x + lw3, ly + 102], fill=RED)
        kx, ky = x + 8, ly + 108
        d.text((kx, ky), "%d  %s" % (lead["num"], lead["kicker"]),
               font=SANS_B(12), fill=RED)
        hy = ky + 17
        lines = fit_lines(d, lead["head"], SERIF_B(27), lw3 - 16, 2)
        hy = text_lines(d, kx, hy, lines, SERIF_B(27), INK, leading=30)
        dy = hy + 5
        dlines = fit_lines(d, lead["deck"], SERIF_R(13), lw3 - 16, 2)
        dy = text_lines(d, kx, dy, dlines, SERIF_R(13), INK, leading=16)
        assert dy + 14 <= ly + lh, "lead %d overflows" % lead["num"]
        d.text((kx, dy + 2), "— " + lead["src"], font=SANS_R(10),
               fill=GREY)

    # ---- mini cards, three rows of five
    my, mh, mgap = 436, 120, 6
    mw = (CW - 4 * 8) / 5.0
    for row in range(3):
        for col in range(5):
            m = MINIS[row * 5 + col]
            x = M + col * (mw + 8)
            y = my + row * (mh + mgap)
            d.rectangle([x, y, x + mw, y + mh], fill=CARD_BG, outline=INK,
                        width=1)
            img.paste(clipped_art(m["art"], mw - 2, 40), (int(x + 1), y + 1))
            kx, ky = x + 7, y + 46
            d.text((kx, ky), "%d  %s" % (m["num"], m["kicker"]),
                   font=SANS_B(9), fill=RED)
            hy = ky + 13
            lines = fit_lines(d, m["head"], SANS_B(13), mw - 14, 2)
            hy = text_lines(d, kx, hy, lines, SANS_B(13), INK, leading=15)
            dlines = fit_lines(d, m["deck"], SERIF_R(10), mw - 14, 2)
            end = text_lines(d, kx, hy + 2, dlines, SERIF_R(10), GREY,
                             leading=12)
            assert end <= y + mh - 3, "mini %d overflows" % m["num"]

    # ---- map band + also list
    by = 816
    d.text((M, by), "WHERE IT HAPPENED · 18 STORIES MAPPED",
           font=SANS_B(15), fill=RED)
    ax = M + 486
    d.text((ax, by), "ALSO ON THURSDAY 26 NOVEMBER", font=SANS_B(15),
           fill=RED)
    rule(d, M, by + 20, CW, width=1)
    draw_map(d, M, by + 26, 470, 108)
    # also list, two columns x 11 rows
    colw = (W - M - ax - 8) / 2.0
    for i, item in enumerate(ALSO):
        c = i // 11
        r = i % 11
        ix = ax + c * colw
        iy = by + 28 + r * 10
        d.rectangle([ix, iy + 3, ix + 7, iy + 10], fill=RED)
        d.text((ix + 11, iy), item, font=SERIF_R(10), fill=INK)

    # ---- date check
    dy0 = 958
    d.rectangle([M, dy0, W - M, dy0 + 36], outline=RED, width=2)
    dlines = wrap(d, DATE_CHECK, SANS_B(11), CW - 20)
    assert len(dlines) <= 2, "date check wraps to %d lines" % len(dlines)
    text_lines(d, M + 10, dy0 + 5, dlines, SANS_B(11), DARKRED,
               leading=14)

    # ---- sources
    sw = d.textlength(SOURCES, font=SANS_R(10))
    d.text(((W - sw) / 2, 1000), SOURCES, font=SANS_R(10), fill=GREY)

    return img


if __name__ == "__main__":
    build().save("entry.png", optimize=True)
    import os
    print("wrote entry.png", os.path.getsize("entry.png"), "bytes")
