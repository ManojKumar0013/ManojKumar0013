"""Personal learning goals and a clearly labeled decorative curve."""
from ..kit import W, chrome, fit, t, wrap
from ..pixel import ptext


def render(st: dict, th: dict, cfg: dict) -> str:
    mobile = th.get("mobile", False)
    width = 420 if mobile else W
    goals = cfg["goals"]
    body = [ptext("NOW TRAINING", 26, 58, 3.5, "fg")]
    for i, goal in enumerate(goals):
        y = 118 + i * (59 if mobile else 42)
        body.append(t(28, y, f"{i + 1:02d}", "amber", 18, weight=700))
        for j, line in enumerate(wrap(goal, 29 if mobile else 36, 2)):
            body.append(t(65, y + j * 22, line, "fg", 18))
    x, y = (28, 289) if mobile else (510, 90)
    body.append(f'<rect x="{x}" y="{y}" width="{width - x - 28}" height="114" rx="9" class="screen" stroke="{th["line"]}"/>')
    body.append(f'<path d="M{x + 18} {y + 16}v55h{width - x - 64}" fill="none" stroke="{th["dim"]}"/>')
    body.append(f'<path class="loss" pathLength="100" d="M{x + 18} {y + 19}l26 12 27 7 26 16 25 -5 31 11 29 -5 32 6 24 -2" fill="none" stroke="{th["green"]}" stroke-width="3"/>')
    body.append(t(x + 15, y + 98, "Illustration · no model measurements", "dim", 13 if not mobile else 15))
    baseline = y + 152
    body.append(t(28, baseline, "LAST SHIPPED", "amber", 17, weight=700))
    shipped = st["shipped"]
    if shipped:
        name = cfg.get("featured", {}).get(shipped["repo"], {}).get("title", shipped["repo"])
        body.append(t(28, baseline + 28, fit(f"{name} · {shipped['date']}", 34 if mobile else 72), "fg", 18))
        body.append(t(28, baseline + 53, fit(shipped["title"], 34 if mobile else 72), "dim", 17))
    else:
        body.append(t(28, baseline + 30, "No public authored commit found", "dim", 16))
    css = "@keyframes draw-loss{from{stroke-dashoffset:100}}.loss{stroke-dasharray:100;animation:draw-loss 1.5s ease-out}"
    return chrome(th, baseline + 76, "training.log", "learning goals", "".join(body), css,
                  "Now Training. " + ". ".join(goals) +
                  (f". Latest public commit: {shipped['title']} on {shipped['date']}." if shipped else ". No public authored commit found."))
