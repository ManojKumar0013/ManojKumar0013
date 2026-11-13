"""Opening screen: power-on line, typed boot log, MANOJ//OS title, PRESS START."""
from ..kit import W, chrome, t, esc
from ..pixel import ptext, text_width

H = 360


def render(st, th, cfg):
    sx, sy, sw, sh = 24, 54, W - 48, 282
    log = [
        ("POST", "memory check · 640K · ok"),
        ("MOUNT", f"/home/{st['login'].lower()} · {st['own_repos']} repos"),
        ("LOAD", f"skills.pkg · {len(st['skills'])} modules"),
        ("SYNC", f"github · {st['contribs']} contributions in {st['year']}"),
        ("READY", f"uptime {st['uptime_days']}d · player 1"),
    ]
    body = [f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" class="screen" stroke="{th["line"]}"/>']
    body.append(f'<rect x="{sx + 40}" y="{sy + sh / 2 - 1}" width="{sw - 80}" height="2" class="green pwr"/>')
    body.append('<g class="dimlog">')
    for i, (tag, msg) in enumerate(log):
        y = sy + 30 + i * 17
        d = 0.5 + i * 0.42
        line = f'<tspan class="green">[ OK ]</tspan> <tspan class="dim">{tag:<5}</tspan> {esc(msg)}'
        body.append(f'<text x="{sx + 22}" y="{y}" class="m fg" font-size="11.5" xml:space="preserve">{line}</text>')
        body.append(f'<rect x="{sx + 18}" y="{y - 12}" width="{sw / 2}" height="16" class="screen type" style="animation-delay:{d:.2f}s"/>')
    body.append("</g>")
    body.append(t(sx + sw - 22, sy + 30, "HI-SCORE", "dim", 11, "end"))
    body.append(t(sx + sw - 22, sy + 48, f"{st['contribs']:06d}", "amber", 15, "end", 700))
    body.append(t(sx + sw - 22, sy + 64, "contributions", "dim", 10, "end"))

    logo, scale = cfg["logo"], 8
    lw = text_width(logo, scale)
    lx, ly = (W - lw) / 2, sy + 118
    body.append(f'<g class="title fb">')
    body.append(ptext(logo, lx + scale * .5, ly + scale * .75, scale, "green2"))
    body.append(ptext(logo, lx, ly, scale, "green glow"))
    body.append("</g>")
    body.append(f'<g class="fade" style="animation-delay:3.4s">{t(W / 2, ly + 86, cfg["tagline"], "fg", 14, "middle")}</g>')
    ps = "PRESS START"
    body.append(f'<g class="fade" style="animation-delay:3.9s"><g class="blink" style="animation-delay:4.6s">'
                f'{ptext(ps, W / 2, ly + 108, 3, "amber", "middle")}</g></g>')
    body.append(t(sx + 22, sy + sh - 16, f"© {st['year']} {st['name'].upper()} · github.com/{st['login']}", "faint", 10.5))
    body.append(t(sx + sw - 22, sy + sh - 16, f"CREDIT 01 · v{st['year']}.{st['today'][5:7]}{st['today'][8:]}", "faint", 10.5, "end"))
    css = """
@keyframes pwr{0%{opacity:1;transform:scaleX(0)}45%{opacity:1;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1)}}
.pwr{opacity:0;transform-box:fill-box;transform-origin:center;animation:pwr .9s cubic-bezier(.3,.7,.2,1)}
@keyframes dimlog{0%,86%{opacity:1}100%{opacity:.5}}
.dimlog{opacity:.5;animation:dimlog 3.6s ease-out}
@keyframes title{from{opacity:0;transform:scale(.94)}}
.title{animation:title 1s cubic-bezier(.2,.8,.2,1) 2.7s backwards}
"""
    return chrome(th, H, "manoj_os — boot.sys", f"{st['login']} · arcade edition", "\n".join(body), css,
                  f"MANOJ//OS boot screen for {st['name']}: {cfg['tagline']}")
