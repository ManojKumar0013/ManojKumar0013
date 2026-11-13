"""Shared panel chrome, palettes and text helpers."""
from __future__ import annotations
from html import escape

W = 840
MONO = "'JetBrains Mono','SF Mono','Cascadia Code','Fira Code',Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"

THEMES = {
    "dark": {
        "bg": "#07090b", "screen": "#0a0e11", "card": "#0d1215", "bar": "#0c1013",
        "line": "#1a2328", "line2": "#243037", "fg": "#e3ece7", "dim": "#8a9892", "faint": "#3a474d",
        "green": "#6ff7b0", "green2": "#1f7a52", "amber": "#ffb547", "amber2": "#7a5a22",
        "mag": "#ff5ca8", "sky": "#0f1a1d", "glow": 0.18,
    },
    "light": {
        "bg": "#f7f5ef", "screen": "#fbfaf6", "card": "#ffffff", "bar": "#efebe2",
        "line": "#ddd7ca", "line2": "#cfc8b8", "fg": "#18211c", "dim": "#626c66", "faint": "#c9c2b2",
        "green": "#0a8a55", "green2": "#9fd8bd", "amber": "#b56a00", "amber2": "#ecd2a6",
        "mag": "#c2185b", "sky": "#eef3ee", "glow": 0.0,
    },
}

LANG_COLORS = {
    "C": "#555555", "Python": "#3572A5", "Java": "#b07219", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Kotlin": "#A97BFF", "CSS": "#663399", "HTML": "#e34c26", "C++": "#f34b7d", "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B", "Go": "#00ADD8", "Rust": "#dea584", "Dart": "#00B4AB",
}


def esc(s) -> str:
    return escape(str(s), quote=True)


def fit(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: max(1, n - 1)].rstrip(" -_·,.") + "…"


def wrap(s: str, n: int, lines: int) -> list[str]:
    words, out, cur = " ".join(str(s).split()).split(" "), [], ""
    for w in words:
        if len(w) > n: w = fit(w, n)
        if not cur: cur = w
        elif len(cur) + 1 + len(w) <= n: cur += " " + w
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    if len(out) > lines:
        last = out[lines - 1].rstrip("…")
        out = out[:lines]
        out[-1] = (last if len(last) <= n - 1 else last[: n - 2].rstrip()) + "…"
    return out or [""]


def t(x, y, s, cls="fg", size=12, anchor="start", weight=None, extra="") -> str:
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x:g}" y="{y:g}" class="m {cls}" font-size="{size}"{a}{w}{extra}>{esc(s)}</text>'


BASE_CSS = """
.m{font-family:%(mono)s}
.fg{fill:%(fg)s}.dim{fill:%(dim)s}.faint{fill:%(faint)s}.green{fill:%(green)s}.green2{fill:%(green2)s}
.amber{fill:%(amber)s}.amber2{fill:%(amber2)s}.mag{fill:%(mag)s}.bgc{fill:%(bg)s}.card{fill:%(card)s}.screen{fill:%(screen)s}
.glow{filter:url(#glow)}
.fb{transform-box:fill-box;transform-origin:center}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
.rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) backwards}
@keyframes fade{from{opacity:0}}
.fade{animation:fade .8s ease-out backwards}
@keyframes blink{0%%,55%%{opacity:1}56%%,100%%{opacity:.3}}
.blink{animation:blink 1.4s ease-in-out infinite}
@keyframes type{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.type{transform-box:fill-box;transform-origin:right center;transform:scaleX(0);animation:type .55s steps(24,end) backwards}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def chrome(th: dict, h: int, title: str, right: str, body: str, css: str = "", label: str = "") -> str:
    p = dict(th, mono=MONO)
    glow = (f'<filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
            f'<feComponentTransfer in="b" result="b2"><feFuncA type="linear" slope="{0.9 if th["glow"] else 0}"/></feComponentTransfer>'
            f'<feMerge><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label or title)}">
<title>{esc(label or title)}</title>
<defs>{glow}
<radialGradient id="halo" cx="50%" cy="0%" r="90%"><stop offset="0" stop-color="{th['green']}" stop-opacity="{th['glow'] * 0.55:.3f}"/><stop offset="1" stop-color="{th['green']}" stop-opacity="0"/></radialGradient>
</defs>
<style>{BASE_CSS % p}{css}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{th['bg']}" stroke="{th['line']}"/>
<rect x="1" y="34" width="{W - 2}" height="{h - 35}" rx="13" fill="url(#halo)"/>
<path d="M1 34V14.5A13.5 13.5 0 0 1 14.5 1h811A13.5 13.5 0 0 1 839 14.5V34z" fill="{th['bar']}"/>
<line x1="1" y1="34.5" x2="{W - 1}" y2="34.5" stroke="{th['line']}"/>
<rect x="18" y="13" width="8" height="8" class="green"/><rect x="30" y="13" width="8" height="8" class="amber"/><rect x="42" y="13" width="8" height="8" class="mag"/>
{t(62, 21.5, title, "dim", 11.5)}
{t(W - 18, 21.5, right, "dim", 11.5, "end")}
{body}
</svg>'''


def header(title_svg: str, sub: str) -> str:
    return title_svg + t(W - 28, 82, sub, "dim", 11.5, "end")
