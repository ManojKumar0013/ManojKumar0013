"""Unlocked Stages: featured repos as game cartridges."""
import re
from ..kit import W, chrome, t, header, fit, wrap, esc
from ..pixel import ptext

CW, CH, GAP, X0, Y0 = 254, 186, 14, 24, 104


def pretty(name):
    s = re.sub(r"[-_]+", " ", name).strip()
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    return " ".join(w.capitalize() if w.isupper() and len(w) > 3 and not any(ch.isdigit() for ch in w) else w for w in s.split())


def ago(d):
    return "today" if d <= 0 else f"{d}d ago" if d < 60 else f"{d // 30}mo ago"


def cart(i, p, th):
    x = X0 + (i % 3) * (CW + GAP)
    y = Y0 + (i // 3) * (CH + GAP)
    k = 16
    shell = (f"M{x + 10} {y}H{x + CW - k}L{x + CW} {y + k}V{y + CH - 10}a10 10 0 0 1 -10 10"
             f"H{x + 10}a10 10 0 0 1 -10 -10V{y + 10}a10 10 0 0 1 10 -10z")
    desc = p["desc"] or f"{p['lang'] or 'Code'} build · {p['kb']:,} KB · {p['n_langs']} language{'s' if p['n_langs'] != 1 else ''}"
    lines = wrap(desc, 31, 2)
    lx, ly, lw, lh = x + 14, y + 26, CW - 28, 112
    o = [f'<g class="rise" style="animation-delay:{0.15 + i * 0.12:.2f}s">',
         f'<path d="{shell}" class="card" stroke="{th["line"]}"/>',
         "".join(f'<rect x="{x + 22 + g * 8}" y="{y + 9}" width="4" height="9" rx="1" fill="{th["line2"]}"/>' for g in range(5)),
         t(x + CW - 24, y + 17, f"STAGE {i + 1:02d}", "dim", 9.5, "end"),
         f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="6" fill="{p["color"]}" fill-opacity=".1" stroke="{p["color"]}" stroke-opacity=".45"/>',
         f'<rect x="{lx}" y="{ly}" width="{lw}" height="6" rx="3" fill="{p["color"]}"/>',
         ]
    title = wrap(pretty(p["name"]), 26, 2)
    for j, ln in enumerate(title):
        o.append(t(lx + 12, ly + 30 + j * 17, ln, "fg", 13.5, weight=700))
    for j, ln in enumerate(lines):
        o.append(t(lx + 12, ly + 40 + len(title) * 17 + 6 + j * 16, ln, "dim", 11))
    by = y + 158
    o.append(f'<circle cx="{x + 20}" cy="{by - 4}" r="4.5" fill="{p["color"]}"/>')
    o.append(t(x + 31, by, fit(p["lang"] or "—", 12), "fg", 11))
    o.append(f'<path d="{star(x + 140, by - 4, 5.5)}" class="amber"/>' + t(x + 150, by, str(p["stars"]), "fg", 11))
    o.append(t(x + CW - 16, by, ago(p["days"]), "dim", 11, "end"))
    o.append("".join(f'<rect x="{x + 26 + g * 22}" y="{y + CH - 5}" width="12" height="3" rx="1" fill="{th["line2"]}"/>' for g in range(10)))
    o.append("</g>")
    return "".join(o)


def star(cx, cy, r):
    from math import cos, sin, pi
    pts = []
    for k in range(10):
        a = -pi / 2 + k * pi / 5
        rr = r if k % 2 == 0 else r * .45
        pts.append(f"{cx + rr * cos(a):.2f} {cy + rr * sin(a):.2f}")
    return "M" + "L".join(pts) + "z"


def render(st, th, cfg):
    ps = st["projects"]
    rows = max(1, (len(ps) + 2) // 3)
    h = Y0 + rows * CH + (rows - 1) * GAP + 26
    body = [header(ptext("UNLOCKED STAGES", 28, 62, 3, "fg"), f"{len(ps)} of {st['own_repos']} repos · stars first, then latest")]
    body += [cart(i, p, th) for i, p in enumerate(ps)]
    if not ps:
        body.append(t(W / 2, Y0 + 90, "no public stages yet — first one unlocks soon", "dim", 13, "middle"))
    return chrome(th, h, "unlocked_stages.rom", f"{len(ps)} cartridges loaded", "\n".join(body), "",
                  "Projects: " + ", ".join(p["name"] for p in ps))
