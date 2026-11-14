"""Achievement cabinet backed by public GitHub activity."""
from ..kit import W, chrome, t
from ..pixel import ptext


def render(st: dict, th: dict, cfg: dict) -> str:
    mobile = th.get("mobile", False)
    width, columns = (420, 1) if mobile else (W, 2)
    card_width = (width - 60) / columns
    badges = [("STREAK", f"{st['best_streak']} active days in a row", st["best_streak"] > 0),
              ("FIRST PULL REQUEST", "Public PR found" if st["first_pr"] else "Awaiting a public PR", bool(st["first_pr"])),
              ("REPOS SHIPPED", f"{st['own_repos']} public project repositories", st["own_repos"] > 0),
              ("LANGUAGES USED", f"{st['languages']} public project languages", st["languages"] > 0)]
    body = [ptext("ACHIEVEMENTS", 26, 57, 3.5, "fg")]
    for i, (title, detail, earned) in enumerate(badges):
        x, y = 24 + i % columns * (card_width + 12), 102 + i // columns * 81
        body.append(f'<g class="rise" style="animation-delay:{i * .12:.2f}s"><rect x="{x}" y="{y}" width="{card_width}" height="68" rx="9" class="card" stroke="{th["line"]}"/>')
        body.append(f'<path d="M{x+25} {y+16}l13 13-13 13-13-13z" class="{"amber" if earned else "dim"}"/>')
        body.extend([t(x+48,y+29,title,"green" if earned else "dim",17,weight=700),
                     t(x+48,y+52,detail,"fg",16), "</g>"])
    return chrome(th, 104 + (len(badges) // columns) * 81, "achievements.dat", "public evidence",
                  "".join(body), label="Achievements. " + ". ".join(detail for _, detail, _ in badges))
