"""Gold arcade cards that also read cleanly in GitHub's light and dark themes."""
from ..kit import W, chrome, esc, fit, t, wrap
from ..pixel import ptext


PALETTES = {
    "light": {"bg": "#fff5cf", "bar": "#f3d779", "screen": "#fffae6", "line": "#bc8726",
              "fg": "#2e200b", "dim": "#5e4518", "amber": "#7c4908", "green": "#65400d",
              "mag": "#9e5315", "glow": 0},
    "dark": {"bg": "#251c0d", "bar": "#3d2b11", "screen": "#302412", "line": "#956b28",
             "fg": "#fff0c9", "dim": "#ead09a", "amber": "#ffcc64", "green": "#ffcf78",
             "mag": "#f9a759", "glow": 0},
}


def gold_palette(theme: dict) -> dict:
    mode = theme["mode"]
    return {**theme, **PALETTES[mode]}


def intro(st: dict, theme: dict, config: dict) -> str:
    theme = gold_palette(theme)
    mobile = theme.get("mobile")
    lines = wrap(config["intro"], 37 if mobile else 66, 8)
    body = [ptext("PLAYER PROFILE", 24, 58, 3, "amber")]
    body.extend(t(24, 108 + i * 23, line, "fg", 16 if mobile else 18) for i, line in enumerate(lines))
    return chrome(theme, 108 + len(lines) * 23, "profile.dat", "", '<g class="rise">' +
                  "".join(body) + "</g>", label=config["intro"])


def footer(st: dict, theme: dict, config: dict) -> str:
    theme = gold_palette(theme)
    mobile = theme.get("mobile")
    body = [ptext("WHAT I LEARNED", 24, 57, 3, "amber")]
    y = 107
    for i, lesson in enumerate(config["lessons"]):
        body.append(t(24, y, f"{i + 1:02d}", "amber", 16, weight=700))
        lines = wrap(lesson, 34 if mobile else 71, 7)
        body.extend(t(60, y + j * 21, line, "fg", 16 if mobile else 17)
                    for j, line in enumerate(lines))
        y += len(lines) * 21 + 11
    return chrome(theme, y + 7, "build_notes.txt", "", '<g class="rise">' +
                  "".join(body) + "</g>", label="What I learned building this. " + " ".join(config["lessons"]))


def project(project: dict, index: int, theme: dict) -> str:
    theme = gold_palette(theme)
    mobile = theme.get("mobile")
    width = 420 if mobile else W
    title = project["title"] or project["name"]
    description = project["desc"] or "Public GitHub project"
    lines = wrap(description, 36 if mobile else 68, 4)
    body = [t(24, 67, fit(title, 30 if mobile else 52), "fg", 20, weight=700)]
    body.extend(t(24, 94 + i * 21, line, "dim", 16) for i, line in enumerate(lines))
    return chrome(theme, 96 + len(lines) * 21, f"STAGE {index:02d}", "OPEN REPOSITORY",
                  '<g class="rise">' + "".join(body) + f'<path d="M{width - 37} 57h12v12m0-12-12 12" ' +
                  f'fill="none" stroke="{theme["amber"]}" stroke-width="2"/></g>',
                  label=f"{title}. {description}. Open repository.")


def button(label: str, theme: dict) -> str:
    theme = gold_palette(theme)
    width = max(90, 30 + len(label) * 10)
    arrow = f'<path d="M{width - 18} 14h6v6m0-6-6 6" fill="none" stroke="{theme["amber"]}" stroke-width="1.5"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="34" viewBox="0 0 {width} 34" role="img">
<title>{esc(label)}</title>
<style>.arrow{{animation:appear .45s ease-out}}@keyframes appear{{from{{opacity:.65}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<desc>Open {esc(label)}</desc>
<rect x=".5" y=".5" width="{width - 1}" height="33" rx="7" fill="{theme['bg']}" stroke="{theme['line']}"/>
<rect x="10" y="13" width="7" height="7" rx="1" fill="{theme['amber']}"/>
{t(23,22,label,"",13,weight=700,extra=f' fill="{theme["fg"]}" font-family="monospace"')}
<g class="arrow">{arrow}</g>
</svg>
"""
