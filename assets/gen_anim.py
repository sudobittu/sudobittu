"""Generate an animated GIF hero banner — crisp rasterized text + motion (scan line, pulse, cursor)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY = (5, 8, 16)
GREEN = (57, 255, 176)
CYAN = (55, 208, 255)
VIOLET = (155, 107, 255)
PINK = (255, 92, 138)
MUTED = (143, 163, 191)
WHITE = (233, 240, 247)
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FBLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FMONO = "/System/Library/Fonts/Menlo.ttc"
W, H = 1000, 250


def font(p, s):
    return ImageFont.truetype(p, s)


def vgrad(w, h, top, bottom):
    base = Image.new("RGB", (w, h), top); ti = Image.new("RGB", (w, h), bottom)
    m = Image.new("L", (w, h)); md = m.load()
    for y in range(h):
        v = int(255 * y / max(1, h - 1))
        for x in range(w):
            md[x, y] = v
    base.paste(ti, (0, 0), m); return base


def glow(size, c, r, col, a):
    l = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(l).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col + (a,))
    return l.filter(ImageFilter.GaussianBlur(r // 2))


def grid(img, step, col, a):
    l = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    for x in range(0, img.size[0], step):
        d.line([(x, 0), (x, img.size[1])], fill=col + (a,))
    for y in range(0, img.size[1], step):
        d.line([(0, y), (img.size[0], y)], fill=col + (a,))
    img.alpha_composite(l)


def grad_text(img, text, fnt, xy, c1, c2):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=fnt, fill=255)
    bb = mask.getbbox()
    if not bb:
        return
    grad = Image.new("RGB", img.size, c1); gi = Image.new("RGB", img.size, c2)
    gm = Image.new("L", img.size, 0); gml = gm.load()
    x0, x1 = bb[0], bb[2]; span = max(1, x1 - x0)
    for x in range(x0, x1):
        v = int(255 * (x - x0) / span)
        for y in range(img.size[1]):
            gml[x, y] = v
    grad.paste(gi, (0, 0), gm)
    img.paste(grad.convert("RGBA"), (0, 0), mask)


def build_base():
    img = vgrad(W, H, NAVY, (4, 20, 12)).convert("RGBA")
    img.alpha_composite(glow((W, H), (120, 40), 220, GREEN, 70))
    img.alpha_composite(glow((W, H), (900, 220), 200, CYAN, 55))
    grid(img, 30, CYAN, 16)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1, 1, W - 2, H - 2], 18, outline=GREEN + (90,), width=2)
    d.rounded_rectangle([0, 34, 7, 216], 3, fill=GREEN)
    d.rounded_rectangle([50, 44, 220, 72], 7, fill=(14, 26, 18), outline=GREEN + (120,))
    for i, c in enumerate((PINK, (245, 196, 81), GREEN)):
        d.ellipse([64 + i * 14, 52, 72 + i * 14, 60], fill=c)
    d.text((108, 51), "~/whoami", font=font(FMONO, 12), fill=MUTED)
    grad_text(img, "Sindhura Kona", font(FBLACK, 50), (50, 82), WHITE, CYAN)
    d.text((52, 158), "Security Researcher", font=font(FMONO, 15), fill=GREEN)
    d.text((280, 158), "Offensive Security", font=font(FMONO, 15), fill=CYAN)
    d.text((500, 158), "Tooling", font=font(FMONO, 15), fill=VIOLET)
    # shield
    ox, oy = 860, 56
    pts = [(ox + 58, oy), (ox + 116, oy + 22), (ox + 116, oy + 76), (ox + 58, oy + 140), (ox, oy + 76), (ox, oy + 22)]
    d.polygon(pts, fill=(11, 21, 38), outline=GREEN + (150,))
    d.line([(ox + 36, oy + 72), (ox + 53, oy + 90), (ox + 84, oy + 48)], fill=GREEN, width=6, joint="curve")
    return img


def scanline(x, alpha=70):
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.rectangle([x - 30, 0, x + 30, H], fill=CYAN + (max(0, alpha // 3),))
    d.line([(x, 0), (x, H)], fill=CYAN + (alpha,), width=2)
    return l.filter(ImageFilter.GaussianBlur(4))


def main():
    base = build_base()
    frames = []
    N = 28
    typed = "building free & open-source security tooling"
    for i in range(N):
        fr = base.copy()
        # sweeping scan line
        x = int(W * (i / (N - 1)))
        fr.alpha_composite(scanline(x))
        # typing tagline + blinking cursor
        d = ImageDraw.Draw(fr)
        n = min(len(typed), int(len(typed) * (i / (N * 0.7))))
        sub = typed[:n]
        d.text((52, 192), sub, font=font(FB, 13), fill=MUTED)
        if i % 4 < 2:
            cx = 52 + int(d.textlength(sub, font=font(FB, 13)))
            d.rectangle([cx + 2, 192, cx + 9, 208], fill=GREEN)
        frames.append(fr.convert("P", palette=Image.ADAPTIVE, colors=128))
    frames[0].save("assets/banner.gif", save_all=True, append_images=frames[1:],
                   duration=90, loop=0, optimize=True, disposal=2)
    print("banner.gif frames:", len(frames))


main()
