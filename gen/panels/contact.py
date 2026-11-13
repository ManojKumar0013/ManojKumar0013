"""Continue? screen: countdown, spinning coin and contact menu."""
from ..kit import W, chrome, t
from ..pixel import ptext, sprite_paths, COIN

H = 300


def render(st, th, cfg):
    body = [f'<rect x="24" y="54" width="{W - 48}" height="{H - 78}" rx="10" class="screen" stroke="{th["line"]}"/>']
    body.append(ptext("CONTINUE?", 56, 92, 5, "amber glow"))
    digits = []
    css = []
    for i, dg in enumerate("9876543210"):
        cls = "cd0" if i == 0 else "cd"
        digits.append(f'<g class="{cls}" style="animation-delay:{i - 10}s">{ptext(dg, 352, 85, 7, "green glow")}</g>')
    css.append("@keyframes cd{0%,9.99%{opacity:1}10%,100%{opacity:0}}.cd{opacity:0;animation:cd 10s steps(1,end) infinite}"
               ".cd0{animation:cd 10s steps(1,end) infinite}")
    body.append("".join(digits))
    body.append(t(56, 152, "the game isn't over — pick a channel to reach player 1", "dim", 12))

    cx, cy = 640, 82
    body.append(f'<g class="spin">{sprite_paths(COIN, cx - 20, cy, 5, {"c": ".amber", "d": ".amber2"})}</g>')
    body.append(f'<g class="blink">{ptext("INSERT COIN", cx, cy + 54, 2, "fg", "middle")}</g>')
    body.append(t(cx, cy + 86, "TO CONNECT", "dim", 11, "middle"))
    css.append("@keyframes spin{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.12)}}"
               ".spin{transform-box:fill-box;transform-origin:center;animation:spin 2.2s ease-in-out infinite}")

    my = 204
    for i, ln in enumerate(cfg["links"]):
        y = my + i * 34
        body.append(f'<g class="rise" style="animation-delay:{0.4 + i * 0.15:.2f}s">'
                    f'<rect x="44" y="{y - 20}" width="{W - 88}" height="28" rx="7" class="card" stroke="{th["line"]}"/>'
                    + ptext(ln["label"], 92, y - 11, 1.6, "green")
                    + t(200, y - 1.5, ln["text"], "fg", 12.5)
                    + t(W - 60, y - 1.5, "link below ↓", "faint", 10.5, "end") + "</g>")
    body.append(f'<path class="arrow green" d="M60 {my - 13}l8 6l-8 6z"/>')
    css.append(f"@keyframes arrow{{0%,45%{{transform:translateY(0)}}50%,95%{{transform:translateY(34px)}}100%{{transform:translateY(0)}}}}"
               f".arrow{{animation:arrow 4s steps(1,end) infinite}}")
    return chrome(th, H, "continue.sh", f"credits: {st['followers']} followers", "\n".join(body), "".join(css),
                  "Continue? Insert coin to connect: " + ", ".join(f"{l['label'].title()} {l['text']}" for l in cfg["links"]))
