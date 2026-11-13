"""Player Select: six skill cards with pixel icons and language-derived levels."""
from ..kit import W, chrome, t, header
from ..pixel import ptext, sprite_paths, SPRITES

CW, CH, GAP, X0, Y0 = 254, 166, 14, 24, 104
ICON_COLORS = {
    "python": {"B": "#3776ab", "Y": "#ffd43b", "k": "#0b0f12", "r": ".mag"},
    "java": {"C": "#e76f00", "h": "#5382a1", "H": "#e76f00", "s": ".dim", "P": "#5382a1"},
    "react": {"R": "#61dafb", "N": ".amber"},
    "kotlin": {"K": "#7f52ff", "O": "#e44857"},
    "javascript": {"J": "#f7df1e", "k": "#16201b"},
    "c": {"H": "#3c5a99", "w": "#ffffff"},
}


def card(i, sk, th):
    x = X0 + (i % 3) * (CW + GAP)
    y = Y0 + (i // 3) * (CH + GAP)
    tone = "amber" if sk["training"] else "green"
    status = "IN TRAINING" if sk["training"] else "INSTALLED"
    o = [f'<g class="rise" style="animation-delay:{0.15 + i * 0.12:.2f}s">',
         f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="10" class="card" stroke="{th["line"]}"/>',
         f'<rect x="{x + 14}" y="{y + 14}" width="64" height="64" rx="6" fill="{th["screen"]}" stroke="{th["line"]}"/>',
         sprite_paths(SPRITES[sk["key"]], x + 18, y + 18, 4, ICON_COLORS[sk["key"]]),
         t(x + 92, y + 30, "CLASS", "dim", 9.5),
         t(x + 92, y + 46, sk["role"], "fg", 12, weight=600),
         f'<rect x="{x + 92}" y="{y + 56}" width="{len(status) * 6.4 + 20:.0f}" height="18" rx="9" fill="none" stroke="{th[tone]}" stroke-opacity=".55"/>',
         f'<circle cx="{x + 101}" cy="{y + 65}" r="2.6" class="{tone}"/>',
         t(x + 108, y + 68.5, status, tone, 9.5, weight=600),
         t(x + CW - 16, y + 30, "LV", "dim", 9.5, "end"),
         ptext(f"{sk['level']:02d}", x + CW - 16, y + 38, 3, f"{tone} glow", "end"),
         ptext(sk["name"], x + 16, y + 90, 3, "fg"),
         t(x + 16, y + 130, f"pkg: {sk['key']} · " + (f"{sk['share'] * 100:.1f}% of code" if sk["share"] else "first repo loading…"), "dim", 11)]
    seg_w = (CW - 32 - 9 * 3) / 10
    for s in range(10):
        on = s < sk["level"]
        cls = f"{tone} seg" if on else "faint"
        delay = f' style="animation-delay:{0.9 + i * 0.12 + s * 0.06:.2f}s"' if on else ""
        o.append(f'<rect x="{x + 16 + s * (seg_w + 3):.1f}" y="{y + 142}" width="{seg_w:.1f}" height="9" rx="1.5" class="{cls}"{delay}/>')
    o.append("</g>")
    return "".join(o)


def selector(th, n):
    steps = []
    for i in range(n):
        x = (i % 3) * (CW + GAP)
        y = (i // 3) * (CH + GAP)
        a, b = i * 100 / n, (i + 1) * 100 / n - 0.01
        steps.append(f"{a:.2f}%,{b:.2f}%{{transform:translate({x}px,{y}px)}}")
    css = "@keyframes sel{" + "".join(steps) + "}.sel{animation:sel %ds steps(1,end) infinite 2.4s}" % (n * 2)
    x, y, w, h, k = X0 - 5, Y0 - 5, CW + 10, CH + 10, 14
    c = th["amber"]
    corners = (f"M{x} {y + k}V{y}H{x + k}M{x + w - k} {y}H{x + w}V{y + k}"
               f"M{x + w} {y + h - k}V{y + h}H{x + w - k}M{x + k} {y + h}H{x}V{y + h - k}")
    svg = (f'<g class="sel"><path d="{corners}" fill="none" stroke="{c}" stroke-width="2.5"/>'
           f'<rect x="{x + w - 34}" y="{y - 8}" width="28" height="15" rx="3" fill="{c}"/>'
           f'{ptext("P1", x + w - 20, y - 4, 1.2, "bgc", "middle")}</g>')
    return css, svg


def render(st, th, cfg):
    skills = st["skills"]
    rows = (len(skills) + 2) // 3
    h = Y0 + rows * CH + (rows - 1) * GAP + 26
    body = [header(ptext("PLAYER SELECT", 28, 62, 3, "fg"), "choose your fighter · levels from repo languages")]
    body += [card(i, sk, th) for i, sk in enumerate(skills)]
    css, sel = selector(th, len(skills))
    body.append(sel)
    css += "@keyframes seg{from{opacity:.15}}.seg{animation:seg .35s ease-out backwards}"
    summary = ", ".join(f"{s['name'].title()} level {s['level']}" for s in skills)
    return chrome(th, h, "player_select.exe", f"{len(skills)} fighters · {sum(not s['training'] for s in skills)} installed",
                  "\n".join(body), css, f"Skills: {summary}")
