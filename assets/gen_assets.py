"""Generate polished PNG banner + project cards (rasterized so text never clips on GitHub)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2  # supersample factor for crispness
NAVY = (5, 8, 16)
NAVY2 = (10, 17, 32)
GREEN = (57, 255, 176)
CYAN = (55, 208, 255)
VIOLET = (155, 107, 255)
PINK = (255, 92, 138)
MUTED = (143, 163, 191)
WHITE = (233, 240, 247)

FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FBLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FMONO = "/System/Library/Fonts/Menlo.ttc"


def f(path, size, idx=0):
    return ImageFont.truetype(path, size * S, index=idx)


def vgrad(w, h, top, bottom):
    base = Image.new("RGB", (w, h), top)
    top_i = Image.new("RGB", (w, h), bottom)
    mask = Image.new("L", (w, h))
    md = mask.load()
    for y in range(h):
        v = int(255 * (y / max(1, h - 1)))
        for x in range(w):
            md[x, y] = v
    base.paste(top_i, (0, 0), mask)
    return base


def glow(size, center, radius, color, alpha):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color + (alpha,))
    return layer.filter(ImageFilter.GaussianBlur(radius // 2))


def grid(img, step, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = img.size
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=color + (alpha,), width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=color + (alpha,), width=1)
    img.alpha_composite(layer)


def grad_text(img, text, font, xy, c1, c2):
    """Draw text filled with a horizontal gradient."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255)
    bbox = mask.getbbox()
    if not bbox:
        return
    grad = Image.new("RGB", img.size, c1)
    gi = Image.new("RGB", img.size, c2)
    gm = Image.new("L", img.size, 0)
    gml = gm.load()
    x0, x1 = bbox[0], bbox[2]
    span = max(1, x1 - x0)
    for x in range(x0, x1):
        v = int(255 * (x - x0) / span)
        for y in range(img.size[1]):
            gml[x, y] = v
    grad.paste(gi, (0, 0), gm)
    img.paste(grad.convert("RGBA"), (0, 0), mask)


def rounded(draw, box, r, **kw):
    draw.rounded_rectangle(box, radius=r, **kw)


def make_banner():
    W, H = 1200 * S, 300 * S
    img = vgrad(W, H, NAVY, (4, 20, 12)).convert("RGBA")
    img.alpha_composite(glow((W, H), (int(W * 0.12), int(H * 0.15)), 260 * S, GREEN, 70))
    img.alpha_composite(glow((W, H), (int(W * 0.9), int(H * 0.9)), 240 * S, CYAN, 55))
    grid(img, 34 * S, CYAN, 16)
    d = ImageDraw.Draw(img)
    rounded(d, [1, 1, W - 2, H - 2], 20 * S, outline=GREEN + (90,), width=2 * S)
    # accent bar
    rounded(d, [0, 40 * S, 8 * S, 260 * S], 4 * S, fill=GREEN)
    # terminal chip
    rounded(d, [60 * S, 52 * S, 250 * S, 84 * S], 8 * S, fill=(14, 26, 18), outline=GREEN + (120,))
    for i, c in enumerate((PINK, (245, 196, 81), GREEN)):
        d.ellipse([76 * S + i * 16 * S, 62 * S, 84 * S + i * 16 * S, 70 * S], fill=c)
    d.text((128 * S, 60 * S), "~/whoami", font=f(FMONO, 13), fill=MUTED)
    # name (gradient)
    grad_text(img, "Sindhura Kona", f(FBLACK, 60), (58 * S, 96 * S), WHITE, CYAN)
    # role
    d.text((62 * S, 196 * S), "Security Researcher", font=f(FMONO, 17), fill=GREEN)
    d.text((300 * S, 196 * S), "Offensive Security", font=f(FMONO, 17), fill=CYAN)
    d.text((540 * S, 196 * S), "Tooling", font=f(FMONO, 17), fill=VIOLET)
    d.text((62 * S, 232 * S), "Breaking it before the bad guys do — free & open-source security tooling.",
           font=f(FB, 14), fill=MUTED)
    # shield emblem right
    ox, oy = 1030 * S, 66 * S
    pts = [(ox + 70 * S, oy), (ox + 140 * S, oy + 26 * S), (ox + 140 * S, oy + 92 * S),
           (ox + 70 * S, oy + 168 * S), (ox, oy + 92 * S), (ox, oy + 26 * S)]
    d.polygon(pts, fill=(11, 21, 38), outline=GREEN + (150,))
    d.line([(ox + 44 * S, oy + 86 * S), (ox + 64 * S, oy + 108 * S), (ox + 100 * S, oy + 58 * S)],
           fill=GREEN, width=7 * S, joint="curve")
    img = img.resize((1200, 300), Image.LANCZOS)
    img.convert("RGB").save("assets/banner.png")
    print("banner.png")


def make_card(fname, icon_bg, accent, title, tagline, lines, chips):
    W, H = 560 * S, 200 * S
    img = vgrad(W, H, NAVY2, (6, 17, 9) if accent == GREEN else (12, 9, 22)).convert("RGBA")
    grid(img, 26 * S, accent, 14)
    d = ImageDraw.Draw(img)
    rounded(d, [1, 1, W - 2, H - 2], 16 * S, outline=accent + (110,), width=2 * S)
    rounded(d, [0, 0, 6 * S, H], 3 * S, fill=accent)
    # icon tile
    rounded(d, [30 * S, 28 * S, 82 * S, 80 * S], 13 * S, fill=icon_bg, outline=accent + (140,))
    d.text((44 * S, 40 * S), title[0], font=f(FBLACK, 24), fill=accent)
    # title + tagline
    d.text((98 * S, 30 * S), title, font=f(FBLACK, 22), fill=WHITE)
    d.text((98 * S, 66 * S), tagline, font=f(FMONO, 12), fill=MUTED)
    y = 104 * S
    for ln in lines:
        d.text((30 * S, y), ln, font=f(FB, 13), fill=(205, 216, 234))
        y += 21 * S
    # chips
    x = 30 * S
    for label, cc, tc in chips:
        w = int(d.textlength(label, font=f(FMONO, 12))) + 24 * S
        rounded(d, [x, 168 * S, x + w, 190 * S], 11 * S, fill=cc)
        d.text((x + 12 * S, 172 * S), label, font=f(FMONO, 12), fill=tc)
        x += w + 10 * S
    img = img.resize((560, 200), Image.LANCZOS)
    img.convert("RGB").save(fname)
    print(fname)


make_banner()
make_card("assets/card-toolkit.png", (14, 26, 18), GREEN, "pentesting-toolkit",
          "offensive-security · curated · open-source",
          ["A domain-structured pentesting resource hub —",
           "tool references, a phased engagement playbook,",
           "and copy-paste cheatsheets. Free & open source."],
          [("91 tool pages", GREEN, (4, 18, 10)), ("20 domains", CYAN, (4, 18, 10)),
           ("6 phases", VIOLET, WHITE)])
make_card("assets/card-signal.png", (18, 14, 30), VIOLET, "signal-hijacked-research",
          "original research · QR phishing · mobile",
          ['"The Signal Switch" — the measurable moment a',
           "user shifts from skepticism to compliance under",
           "a QR-based phishing attack over messaging."],
          [("DEF CON 34", VIOLET, WHITE), ("carrier-gateway detect", CYAN, (4, 18, 10))])
