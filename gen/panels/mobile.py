"""Compact SVG layouts for the narrow GitHub README column."""
from math import ceil, sqrt

from ..kit import chrome, fit, t, wrap
from ..pixel import COIN, RUNNER, SPRITES, ptext, sprite_paths
from . import level, skills
from .stages import pretty


def panel(th, title, label, items, body, height, css=""):
    return chrome(th, height, title, "arcade edition", "".join(items + body), css, label)


def heading(title):
    return [ptext(title, 22, 56, 3.35, "fg")]


def boot(st, th, cfg):
    body = [f'<rect x="14" y="51" width="392" height="252" rx="10" class="screen" stroke="{th["line"]}"/>',
            ptext(cfg["logo"], 210, 73, min(6, 370 / max(1, 6 * len(cfg["logo"]))), "green glow", "middle")]
    for i, line in enumerate(wrap(cfg["tagline"], 32, 2)):
        body.append(t(210, 139 + i * 21, line, "fg", 17, "middle"))
    for i, msg in enumerate([f"SYNC  {st['contribs']} contributions", f"LOAD  {st['own_repos']} public projects"]):
        body.append(f'<g class="rise" style="animation-delay:{.15+i*.22:.2f}s">{t(37,205+i*23,msg,"dim",16)}</g>')
    body.append(f'<g class="blink">{ptext("PRESS START", 210, 254, 3, "amber", "middle")}</g>')
    return panel(th, "boot.sys", cfg["tagline"] + ". Press start to play.", [], body, 319)


def roster(st, th, cfg):
    body = []
    for i, sk in enumerate(st["skills"]):
        y = 98 + 81 * i
        tone = "amber" if sk["training"] else "green"
        icon = (sprite_paths(SPRITES[sk["key"]], 29, y + 14, 3.3, skills.ICON_COLORS[sk["key"]])
                if sk["key"] in SPRITES else ptext("ML", 51, y + 23, 3, "mag", "middle"))
        status = "IN TRAINING" if sk["training"] else f'{sk["repos"]} repos with evidence'
        body.extend([f'<g class="rise" style="animation-delay:{i*.05:.2f}s"><rect x="15" y="{y}" width="390" height="70" rx="8" class="card" stroke="{th["line"]}"/>',
                     icon, t(94,y+28,fit(sk["name"],23),"fg",21,weight=700),
                     t(94,y+54,status,tone,16), ptext(f'{sk["level"]:02d}',385,y+25,3,tone,"end"), '</g>'])
    if not body:
        body.append(t(22,117,"No skills configured","dim",17))
    return panel(th,"player_select.exe","Player Select. Levels count public repository evidence.",heading("PLAYER SELECT"),
                 body, max(151,105+81*len(st["skills"])))


def stages(st, th, cfg):
    body = []
    for i, project in enumerate(st["projects"]):
        y = 100 + i * 128
        title = fit(project["title"] or pretty(project["name"]), 30)
        body.append(f'<g class="rise" style="animation-delay:{i*.10:.2f}s"><rect x="14" y="{y}" width="392" height="116" rx="9" class="card" stroke="{th["line"]}"/>')
        body.append(t(30,y+26,f'STAGE {i+1:02d}',"green",15,weight=700))
        body.append(t(30,y+54,title,"fg",19,weight=700))
        for j,line in enumerate(wrap(project["desc"] or "Public GitHub repository",34,2)):
            body.append(t(30,y+80+j*19,line,"dim",16))
        body.append("</g>")
    if not body:
        body.append(t(22,117,"No public stages available","dim",17))
    return panel(th,"stages.rom","Featured projects. Source links appear below the panel.",heading("UNLOCKED STAGES"),
                 body, max(151,102+128*len(st["projects"])))


def scores(st, th, cfg):
    data = [("CONTRIBUTIONS", "contribs"), ("CURRENT STREAK", "streak"), ("BEST STREAK", "best_streak"),
            ("PUBLIC REPOS", "repos"), ("STARS EARNED", "stars"), ("FOLLOWERS", "followers")]
    body = []
    for i,(label,key) in enumerate(data):
        y = 99 + i * 55
        body.append(f'<g class="rise" style="animation-delay:{i*.10:.2f}s"><rect x="16" y="{y}" width="388" height="47" rx="7" class="card"/>')
        body.append(t(29,y+29,label,"fg",17,weight=700))
        body.append(t(387,y+31,f'{st[key]:,}',"amber" if i == 0 else "green",22,"end",700))
        body.append("</g>")
    return panel(th,"high_scores.dat","GitHub counts: "+", ".join(f"{label}: {st[key]}" for label,key in data),
                 heading("HIGH SCORES"),body,446)


def world(st, th, cfg):
    _, count, totals, days, current = level.weeks(st)
    scale = 7
    x0 = (420 - count*scale) / 2
    ground = 212
    heights = [ceil(63*sqrt(val/max(totals))) if val else 0 for val in totals] if any(totals) else [0]*count
    body = ['<rect x="15" y="94" width="390" height="144" rx="8" class="screen"/>',
            t(23,264,f'{st["contribs"]} contributions · {sum(days)} active days',"fg",16),
            t(23,289,"Taller platforms mean busier weeks","dim",16)]
    for i,h in enumerate(heights):
        x=x0+i*scale
        body.append(f'<rect x="{x:g}" y="{ground-h}" width="6" height="{h+9}" class="{"green" if h else "faint"}"/>')
    x = x0 + current * scale
    ground -= heights[current]
    body.extend([f'<path d="M{x:g} {ground}v-45h13l-13 8" fill="none" stroke="{th["mag"]}" stroke-width="2"/>',
                 f'<g class="rise">{sprite_paths(RUNNER[0], x-14, ground-14, 1.2, {"a":".mag","f":"#f2c9a0","k":"#16201b","g":".amber","b":".fg"})}</g>'])
    return panel(th,"level_map.lvl",f'Contribution year {st["year"]}. Click to play.',heading(f'WORLD {st["year"]}'),body,313)


def contact(st, th, cfg):
    body = [f'<g class="rise">{sprite_paths(COIN,357,52,3.6,{"c":".amber","d":".amber2"})}</g>']
    for i, link in enumerate(cfg["links"]):
        y=100+i*58
        body.append(f'<rect x="16" y="{y}" width="388" height="50" rx="8" class="card"/>')
        body.append(t(28,y+31,link["label"],"green",16,weight=700))
        body.append(t(390,y+31,fit(link["text"],27),"fg",14,"end"))
    return panel(th,"continue.sh","Continue? Contact links are listed under the panel.",heading("CONTINUE?"),
                 body,118+len(cfg["links"])*58)


RENDER = {"boot": boot, "skills": roster, "scores": scores,
          "level": world, "stages": stages, "contact": contact}
