"""Unlocked Stages: featured repos as game cartridges."""
import re
from ..kit import BASE_CSS, MONO, chrome, esc, fit, t, wrap
from ..pixel import ptext


def pretty(name):
    s = re.sub(r"[-_]+", " ", name).strip()
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    return " ".join(w.capitalize() if w.isupper() and len(w) > 3 and not any(ch.isdigit() for ch in w) else w for w in s.split())


def ago(d):
    return "today" if d <= 0 else f"{d}d ago" if d < 60 else f"{d // 30}mo ago"


def cartridge(project: dict, index: int, theme: dict) -> str:
    """Render a standalone cartridge so the README can link the whole tile."""
    title = project["title"] or pretty(project["name"])
    desc = project["desc"] or "Public GitHub project"
    color = esc(project["color"])
    lines = wrap(desc, 32, 2)
    titles = wrap(title, 27, 2)
    body = [
        f'<path d="M10 .5H228l17 17V119a9 9 0 0 1-9 9H10a9 9 0 0 1-9-9V10a9 9 0 0 1 9-9.5Z" fill="{theme["card"]}" stroke="{theme["line"]}"/>',
        f'<rect x="12" y="25" width="221" height="79" rx="5" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".45"/>',
        f'<rect x="12" y="25" width="221" height="5" rx="2" fill="{color}"/>',
        t(227, 17, f"STAGE {index:02d}", size=9, anchor="end"),
        f'<path d="M221 36h7v7m0-7-7 7" fill="none" stroke="{theme["dim"]}" stroke-width="1.3"/>',
        *(t(22, 47 + j * 14, line, size=12, weight=700) for j, line in enumerate(titles)),
        *(t(22, 48 + len(titles) * 14 + j * 14, line, "dim", 11) for j, line in enumerate(lines)),
        f'<circle cx="17" cy="117" r="3.5" fill="{color}"/>',
        t(26, 121, fit(project["lang"] or "Source", 20), size=10),
        t(229, 121, ago(project["days"]), "dim", 10, "end"),
    ]
    body.extend(f'<rect x="{17 + slot * 7}" y="10" width="3" height="8" rx="1" fill="{theme["line2"]}"/>'
                for slot in range(5))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="246" height="129" viewBox="0 0 246 129" role="img">
<title>{esc(title)} · Open repository</title>
<desc>{esc(desc)}</desc>
<style>{BASE_CSS % dict(theme, mono=MONO)}</style>
<g class="rise">{''.join(body)}</g>
</svg>
"""


def render(st, th, cfg):
    count = len(st["projects"])
    body = ptext("UNLOCKED STAGES", 24, 50, 2.65, "fg")
    if not count:
        body += t(24, 88, "No featured public projects", "dim", 14)
    return chrome(th, 104 if not count else 83, "unlocked_stages.rom",
                  f"{count} {'cartridge' if count == 1 else 'cartridges'}", body,
                  label="Unlocked Stages")
