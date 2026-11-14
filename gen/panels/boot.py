"""Opening screen for the profile."""
from ..kit import W, chrome, t
from ..pixel import ptext


def render(st, th, cfg):
    body = [
        f'<rect x="24" y="54" width="{W - 48}" height="182" rx="10" class="screen" stroke="{th["line"]}"/>',
        t(W / 2, 84, st["name"].upper(), "dim", 15, "middle", 700),
        ptext(cfg["logo"], W / 2, 105, 8, "green glow", "middle"),
        t(W / 2, 195, cfg["tagline"], "fg", 17, "middle"),
        '<path class="amber" d="M403 214h8v4h-8zm13 0h8v4h-8zm13 0h8v4h-8z"/>',
    ]
    return chrome(th, 260, "manoj_os / profile", f"@{st['login']} · arcade edition", "\n".join(body),
                  label=f"{st['name']} — {cfg['tagline']}")
