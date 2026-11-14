"""Render and verify the GitHub profile README and its local artwork."""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

from .kit import THEMES
from .panels import boot, level, scores, skills, stages
from .stats import CONFIG, fetch

ROOT = Path(__file__).resolve().parents[1]
PANELS = {"boot": boot, "stages": stages, "skills": skills, "level": level, "scores": scores}


def update_block(readme, name, body):
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) > readme.index(end):
        raise ValueError(f"README requires one correctly ordered {name} block")
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return f"{before}{start}\n\n{body}\n\n{end}{after}"


def project_table(projects):
    lines = ["| Project | What it does | Stack | Links |", "| --- | --- | --- | --- |"]
    for project in projects:
        links = f'[Source]({project["url"]})'
        if demo := project.get("demo"):
            links += f' · [Live demo]({demo})'
        lines.append(f'| **{project["title"]}** | {project["summary"]} | {project["stack"]} | {links} |')
    return "\n".join(lines)


def render_profile(stats, readme):
    rendered = {
        Path(f"assets/{theme}/{name}.svg"): panel.render(stats, palette, CONFIG)
        for theme, palette in THEMES.items() for name, panel in PANELS.items()
    }
    readme = update_block(readme, "STAGES", project_table(stats["projects"]))
    readme = update_block(readme, "ACTIVITY", (
        f"**{stats['contribs']:,} contributions in {stats['year']}** · "
        f"**{stats['streak']:,}-day current streak** · "
        f"**{stats['best_streak']:,}-day best streak this year**\n\n"
        f"Snapshot from GitHub on {stats['today']} (UTC)."
    ))
    return {**rendered, Path("README.md"): readme}


def validate(files):
    readme = files[Path("README.md")]
    for name in ("STAGES", "ACTIVITY"):
        pattern = rf"<!-- {name}:START -->\s*(\S.*?)<!-- {name}:END -->"
        if not re.search(pattern, readme, re.S):
            raise ValueError(f"Empty {name} block in README")
        update_block(readme, name, "")
    references = {Path(path) for path in re.findall(r'(?:srcset|src)="(assets/[^"]+)"', readme)}
    artwork = files.keys() - {Path("README.md")}
    if artwork != references:
        raise ValueError(f"README artwork differs from generated panels: {artwork ^ references}")
    for path in artwork:
        svg = ElementTree.fromstring(files[path])
        if svg.tag != "{http://www.w3.org/2000/svg}svg" or not svg.get("viewBox"):
            raise ValueError(f"Invalid SVG artwork: {path}")


def publish(files):
    # Stage the complete snapshot before replacing any published file.
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        staging = Path(tmp)
        for path, content in files.items():
            target = staging / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for path in files:
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            (staging / path).replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the existing snapshot offline")
    args = parser.parse_args()
    try:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        if args.check:
            files = {path: (ROOT / path).read_text(encoding="utf-8") for path in (
                Path(f"assets/{theme}/{name}.svg") for theme in THEMES for name in PANELS
            )}
            files[Path("README.md")] = readme
        else:
            files = render_profile(fetch(), readme)
        validate(files)
        if not args.check:
            publish(files)
        print(f"Validated README and {len(files) - 1} SVG panels.")
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, ElementTree.ParseError) as error:
        print(f"Profile {'validation' if args.check else 'refresh'} failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
