"""Compact profile text panels using the shared arcade palette."""
from ..kit import chrome, esc, t, wrap
from ..pixel import ptext


def intro(st: dict, theme: dict, config: dict) -> str:
    mobile = theme.get("mobile")
    lines = wrap(config["intro"], 44 if mobile else 88, 8)
    body = [ptext("PLAYER PROFILE", 24, 52, 2.4, "fg")]
    body.extend(t(24, 88 + i * 19, line, "fg", 14 if mobile else 15) for i, line in enumerate(lines))
    return chrome(theme, 90 + len(lines) * 19, "profile.dat", "", '<g class="rise">' +
                  "".join(body) + "</g>", label=config["intro"])


def footer(st: dict, theme: dict, config: dict) -> str:
    mobile = theme.get("mobile")
    body = [ptext("WHAT I LEARNED", 24, 52, 2.4, "fg")]
    y = 87
    for i, lesson in enumerate(config["lessons"]):
        body.append(t(24, y, f"{i + 1:02d}", "amber", 13, weight=700))
        lines = wrap(lesson, 42 if mobile else 94, 7)
        body.extend(t(60, y + j * 18, line, "fg", 13 if mobile else 14)
                    for j, line in enumerate(lines))
        y += len(lines) * 18 + 8
    return chrome(theme, y + 7, "build_notes.txt", "", '<g class="rise">' +
                  "".join(body) + "</g>", label="What I learned building this. " + " ".join(config["lessons"]))


def button(label: str, theme: dict) -> str:
    width = max(90, 30 + len(label) * 10)
    arrow = f'<path d="M{width - 18} 14h6v6m0-6-6 6" fill="none" stroke="{theme["amber"]}" stroke-width="1.5"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="32" viewBox="0 0 {width} 32" role="img">
<title>{esc(label)}</title>
<style>.arrow{{animation:appear .45s ease-out}}@keyframes appear{{from{{opacity:.65}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<desc>Open {esc(label)}</desc>
<rect x=".5" y=".5" width="{width - 1}" height="31" rx="7" fill="{theme['bg']}" stroke="{theme['line']}"/>
<rect x="10" y="13" width="7" height="7" rx="1" fill="{theme['amber']}"/>
{t(23,22,label,"",12,weight=700,extra=f' fill="{theme["fg"]}" font-family="monospace"')}
<g class="arrow">{arrow}</g>
</svg>
"""
