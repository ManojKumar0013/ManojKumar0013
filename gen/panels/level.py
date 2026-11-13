"""Level Map: the contribution year as a pixel platformer with a runner and coins."""
import datetime as dt
from math import ceil, sqrt
from ..kit import W, chrome, t, header
from ..pixel import ptext, sprite_paths, RUNNER, COIN

G, U, CWID = 252, 11, 14
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def weeks(st):
    y = st["year"]
    jan1 = dt.date(y, 1, 1)
    start = jan1 - dt.timedelta(days=(jan1.weekday() + 1) % 7)
    n = (dt.date(y, 12, 31) - start).days // 7 + 1
    tot, active = [0] * n, [0] * n
    for d, c in st["calendar"]:
        i = (dt.date.fromisoformat(d) - start).days // 7
        if 0 <= i < n and c:
            tot[i] += c; active[i] += 1
    cw = (dt.date.fromisoformat(st["today"]) - start).days // 7
    return start, n, tot, active, min(max(cw, 0), n - 1)


def render(st, th, cfg):
    start, n, tot, active, cw = weeks(st)
    mx = max(tot) or 1
    lv = [ceil(5 * sqrt(v / mx)) if v else 0 for v in tot]
    x0 = (W - n * CWID) / 2
    top = [G - lv[c] * U for c in range(n)]
    cx = [x0 + c * CWID + CWID / 2 for c in range(n)]
    body = [header(ptext(f"WORLD {st['year']}", 28, 62, 3, "fg"),
                   f"{st['contribs']} coins · {sum(1 for _, c in st['calendar'] if c)} active days · best week {max(tot)}")]
    body.append(f'<rect x="24" y="100" width="{W - 48}" height="{G - 100 + 58}" rx="10" fill="{th["sky"]}" stroke="{th["line"]}"/>')
    for hx, hr in ((120, 70), (300, 44), (520, 86), (700, 52)):
        body.append(f'<path d="M{hx - hr} {G}a{hr} {hr * .7} 0 0 1 {hr * 2} 0z" fill="{th["line"]}" fill-opacity=".55"/>')
    for i, (cx0, cy0) in enumerate(((140, 128), (430, 116), (650, 136))):
        body.append(f'<g class="cloud" style="animation-delay:{-i * 7}s"><path d="M{cx0} {cy0}h28v-6h12v6h10v8h-58v-8z" fill="{th["line2"]}" fill-opacity=".7"/></g>')
    bricks = []
    for c in range(n):
        x = x0 + c * CWID
        for k in range(lv[c]):
            cls = "green" if k == lv[c] - 1 else "green2"
            bricks.append(f'<rect x="{x + .5:.1f}" y="{G - (k + 1) * U + 1}" width="{CWID - 1}" height="{U - 1}" rx="1.5" class="{cls}"/>')
    body.append(f'<g class="rise" style="animation-delay:.2s">{"".join(bricks)}</g>')
    gx1 = x0 + (cw + 1) * CWID
    body.append(f'<rect x="{x0}" y="{G}" width="{gx1 - x0}" height="12" fill="{th["line2"]}"/>')
    body.append(f'<rect x="{gx1}" y="{G}" width="{x0 + n * CWID - gx1}" height="12" fill="{th["line"]}"/>')
    seams = "".join(f"M{x0 + c * CWID:.1f} {G + (6 if c % 2 else 0)}v6" for c in range(n + 1))
    body.append(f'<path d="{seams}M{x0} {G + 6}h{n * CWID}" stroke="{th["bg"]}" stroke-opacity=".5" fill="none"/>')
    for c in range(cw + 6, n, 7):
        body.append(f'<rect x="{x0 + c * CWID + 1}" y="{G - 34}" width="12" height="12" rx="2" fill="none" stroke="{th["faint"]}" stroke-dasharray="2 2"/>'
                    + t(x0 + c * CWID + 7, G - 24.5, "?", "faint", 10, "middle"))
    if cw < n - 6:
        body.append(t((gx1 + x0 + n * CWID) / 2, G - 52, "unexplored", "faint", 10, "middle"))

    span = max(cw, 1)
    secs = max(8.0, span * 0.22)
    run_end = 86.0
    pct = lambda c: c / span * run_end
    css = [f"@keyframes cloud{{to{{transform:translateX(40px)}}}}.cloud{{animation:cloud 14s ease-in-out infinite alternate}}",
           "@keyframes bob{to{transform:translateY(-3px)}}.bob{animation:bob .9s ease-in-out infinite alternate}"]
    coins = []
    for c in range(cw + 1):
        if not tot[c]: continue
        p = pct(c)
        css.append(f"@keyframes k{c}{{0%,{max(p - .01, 0):.2f}%{{opacity:1}}{p:.2f}%,99.8%{{opacity:0}}100%{{opacity:1}}}}"
                   f".k{c}{{animation:k{c} {secs:.2f}s linear infinite 1.2s}}")
        coins.append(f'<g class="k{c}"><g class="bob" style="animation-delay:{-(c % 5) * .18:.2f}s">'
                     f'{sprite_paths(COIN, cx[c] - 6, top[c] - 22, 1.5, {"c": ".amber", "d": ".amber2"})}</g></g>')
    body.append(f'<g class="fade" style="animation-delay:.6s">{"".join(coins)}</g>')

    fx, fy = cx[cw], top[cw]
    body.append(f'<line x1="{fx}" y1="{fy}" x2="{fx}" y2="{fy - 62}" stroke="{th["dim"]}" stroke-width="2"/>'
                f'<path d="M{fx + 1} {fy - 62}l18 7l-18 7z" class="mag"/>' + t(fx, fy - 68, "TODAY", "mag", 9.5, "middle", 600))

    rw, rh = 18, 22
    frames = []
    for c in range(cw + 1):
        frames.append(f"{pct(c):.2f}%{{transform:translate({cx[c] - cx[0]:.1f}px,{top[c] - top[0]:.1f}px)}}")
        if c < cw and top[c + 1] != top[c]:
            frames.append(f"{(pct(c) + pct(c + 1)) / 2:.2f}%{{transform:translate({(cx[c] + cx[c + 1]) / 2 - cx[0]:.1f}px,{min(top[c], top[c + 1]) - 16 - top[0]:.1f}px)}}")
    frames.append(f"100%{{transform:translate({cx[cw] - cx[0] - 12:.1f}px,{top[cw] - top[0]:.1f}px)}}")
    css.append("@keyframes run{" + "".join(frames) + f"}}.run{{animation:run {secs:.2f}s linear infinite 1.2s}}")
    css.append("@keyframes leg{0%,49%{opacity:1}50%,100%{opacity:0}}.legA{animation:leg .32s steps(1,end) infinite}"
               ".legB{opacity:0;animation:leg .32s steps(1,end) infinite -.16s}")
    pal = {"a": ".mag", "f": "#f2c9a0", "k": "#16201b", "g": ".amber", "b": ".fg"}
    rx, ry = cx[0] - rw / 2, top[0] - rh
    body.append(f'<g class="run"><g class="legA">{sprite_paths(RUNNER[0], rx, ry, 2, pal)}</g>'
                f'<g class="legB">{sprite_paths(RUNNER[1], rx, ry, 2, pal)}</g></g>')

    for m in range(12):
        c = (dt.date(st["year"], m + 1, 1) - start).days // 7
        body.append(t(x0 + c * CWID + 2, G + 28, MONTHS[m], "dim", 9.5))
    ly = G + 82
    body.append(f'<rect x="28" y="{ly - 9}" width="10" height="10" rx="1.5" class="green"/>' + t(44, ly, "brick height = weekly contributions", "dim", 10.5))
    body.append(sprite_paths(COIN, 300, ly - 10, 1.4, {"c": ".amber", "d": ".amber2"}) + t(318, ly, "coin = active week", "dim", 10.5))
    body.append(f'<path d="M470 {ly - 10}l10 4l-10 4z" class="mag"/>' + t(486, ly, "flag = this week", "dim", 10.5))
    body.append(t(W - 28, ly, f"streak {st['streak']}d · longest {st['best_streak']}d", "fg", 10.5, "end"))
    h = ly + 22
    return chrome(th, h, "level_map.lvl", f"week {cw + 1} of {n}", "\n".join(body), "".join(css),
                  f"Contribution level map for {st['year']}: {st['contribs']} contributions")
