"""Arcade-style language cards backed by repository counts."""
from ..kit import chrome, header, t
from ..pixel import SPRITES, ptext, sprite_paths

ICONS = {
    "c": ("c", {"H": "#3c5a99", "w": "#ffffff"}),
    "python": ("python", {"B": "#3776ab", "Y": "#ffd43b", "k": "#0b0f12", "r": ".mag"}),
    "java": ("java", {"C": "#e76f00", "h": "#5382a1", "H": "#e76f00", "s": ".dim", "P": "#5382a1"}),
    "typescript": ("typescript", {}),
    "kotlin": ("kotlin", {"K": "#7f52ff", "O": "#e44857"}),
    "javascript": ("javascript", {"J": "#f7df1e", "k": "#16201b"}),
}


def render(st, th, cfg):
    width, height, gap = 254, 102, 14
    body = [header(ptext("LANGUAGE SELECT", 28, 62, 3, "fg"), "public, non-fork project repositories")]
    for i, skill in enumerate(st["skills"]):
        x, y = 24 + i % 3 * (width + gap), 104 + i // 3 * (height + gap)
        count = skill["repos"]
        sprite, colors = ICONS[skill["key"]]
        if sprite == "typescript":
            icon = ptext("TS", x + 42, y + 42, 3, "green", "middle")
        else:
            icon = sprite_paths(SPRITES[sprite], x + 20, y + 26, 3.5, colors)
        label = f"{count} {'repository' if count == 1 else 'repositories'}"
        body.extend([
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" class="card" stroke="{th["line"]}"/>',
            icon,
            ptext(skill["name"], x + 86, y + 30, 2, "fg"),
            t(x + 86, y + 66, label, "dim", 13),
        ])
    rows = (len(st["skills"]) + 2) // 3
    summary = ", ".join(f"{s['name']}: {s['repos']}" for s in st["skills"])
    return chrome(th, 130 + rows * height + (rows - 1) * gap, "language_select.exe",
                  f"{len(st['skills'])} languages", "\n".join(body), label=f"Repository counts: {summary}")
