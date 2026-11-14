"""High Score table: live GitHub numbers as an arcade scoreboard."""
from ..kit import W, chrome, t, header
from ..pixel import ptext

RANKS = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH"]


def render(st, th, cfg):
    rows = [
        (f"CONTRIBUTIONS {st['year']}", st["contribs"], "commits, PRs, issues and reviews"),
        ("CURRENT STREAK", st["streak"], "active days through today or yesterday"),
        (f"LONGEST STREAK {st['year']}", st["best_streak"], "best run of active days"),
        ("PUBLIC REPOS", st["repos"], f"{st['own_repos']} owned, excluding this profile and forks"),
        ("STARS EARNED", st["stars"], "across public project repositories"),
        ("FOLLOWERS", st["followers"], "GitHub followers"),
    ]
    y0, rh = 128, 44
    body = [header(ptext("HIGH SCORES", 28, 62, 3, "fg"), f"world {st['year']} · GitHub activity")]
    body.append(t(44, y0 - 14, "RANK", "faint", 10))
    body.append(t(120, y0 - 14, "STAT", "faint", 10))
    body.append(t(W - 220, y0 - 14, "SCORE", "faint", 10))
    body.append(t(W - 44, y0 - 14, "PLAYER", "faint", 10, "end"))
    for i, (label, val, note) in enumerate(rows):
        y = y0 + i * rh
        top = i == 0
        rank_cls = "amber" if top else ("fg" if i < 3 else "dim")
        score_cls = "amber glow" if top else "green"
        o = [f'<g class="slide" style="animation-delay:{0.2 + i * 0.14:.2f}s">']
        if top:
            o.append(f'<rect x="28" y="{y - 2}" width="{W - 56}" height="{rh - 6}" rx="8" fill="{th["amber"]}" fill-opacity=".07" stroke="{th["amber"]}" stroke-opacity=".3"/>')
        elif i % 2 == 0:
            o.append(f'<rect x="28" y="{y - 2}" width="{W - 56}" height="{rh - 6}" rx="8" class="card"/>')
        o.append(ptext(RANKS[i], 44, y + 12, 2, rank_cls))
        o.append(t(120, y + 18, label, "fg", 13, weight=600))
        o.append(t(120, y + 32, note, "dim", 10.5))
        o.append(f'<line x1="{120 + len(label) * 8 + 14:.0f}" y1="{y + 15}" x2="{W - 232}" y2="{y + 15}" stroke="{th["faint"]}" stroke-dasharray="2 5"/>')
        o.append(ptext(f"{val:06d}", W - 220, y + 8, 3, score_cls))
        o.append(ptext(cfg["initials"], W - 44, y + 12, 2, "dim", "end"))
        if label == "CURRENT STREAK" and val > 0 and val == st["best_streak"]:
            o.append(ptext("BEST STREAK", W - 336, y + 13, 1.4, "mag", "end"))
        o.append("</g>")
        body.append("".join(o))
    h = y0 + len(rows) * rh + 18
    css = "@keyframes slide{from{opacity:0;transform:translateX(-14px)}}.slide{animation:slide .6s cubic-bezier(.2,.7,.2,1) backwards}"
    summary = "; ".join(f"{r[0].title()}: {r[1]}" for r in rows)
    return chrome(th, h, "high_scores.dat", f"updated {st['today']}", "\n".join(body), css, f"GitHub stats — {summary}")
