"""python -m gen  ->  renders every panel (dark + light) into assets/ and refreshes README links."""
import json
import os
import re
import sys
import tempfile
from .kit import THEMES
from .stats import fetch, CONFIG
from .panels import boot, skills, scores, level, stages, contact

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
PANELS = {"boot": boot, "skills": skills, "scores": scores, "level": level, "stages": stages, "contact": contact}


def readme_links(st):
    path = os.path.join(ROOT, "README.md")
    if not os.path.exists(path): return
    links = " ·\n  ".join(f'<a href="{p["url"]}"><code>{i:02d} {p["name"]}</code></a>' for i, p in enumerate(st["projects"], 1))
    block = f'<!-- STAGES:START -->\n<p align="center">\n  {links}\n</p>\n<!-- STAGES:END -->'
    src = open(path, encoding="utf-8").read()
    new = re.sub(r"<!-- STAGES:START -->.*?<!-- STAGES:END -->", lambda _: block, src, flags=re.S)
    if new != src:
        open(path, "w", encoding="utf-8").write(new)


def main():
    cache = os.environ.get("STATS_CACHE")
    try:
        if cache and os.path.exists(cache):
            st = json.load(open(cache))
        else:
            st = fetch()
            if cache: json.dump(st, open(cache, "w"))
        if not st["calendar"]:
            raise RuntimeError("empty contribution calendar")
    except Exception as e:
        print(f"fetch failed ({e}); keeping the last good panels untouched", file=sys.stderr)
        sys.exit(1)
    print(f"stats: {st['contribs']} contributions, {st['repos']} repos, streak {st['streak']}/{st['best_streak']}")
    rendered = {}
    for theme, th in THEMES.items():
        for name, mod in PANELS.items():
            rendered[f"{theme}/{name}.svg"] = mod.render(st, th, CONFIG)
    for rel, svg in rendered.items():
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dst), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(svg)
        os.replace(tmp, dst)
        print(f"  {rel:<20} {len(svg) / 1024:6.1f} KB")
    readme_links(st)


if __name__ == "__main__":
    main()
