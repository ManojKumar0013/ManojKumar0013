"""Render the complete profile snapshot, or check the committed files offline."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

from .game import export_level
from .kit import THEMES, palette
from .panels import boot, contact, gold, level, mobile, scores, skills, stages
from .stats import CONFIG, fetch

ROOT = Path(__file__).resolve().parents[1]
PANELS = {"boot": boot, "skills": skills, "stages": stages, "level": level,
          "scores": scores, "contact": contact, "intro": gold.intro, "footer": gold.footer}
BUDGET = 150_000
PLAY = "Play the game"
LEVEL = Path("game/level.json")
README = Path("README.md")


def art_paths() -> list[Path]:
    return [Path(f"assets/{theme}/{name}{suffix}.svg")
            for theme in THEMES for suffix in ("", "-mobile") for name in PANELS]


def picture(name: str, alt: str, url: str = "") -> str:
    image = "\n".join([
        "<picture>",
        f'  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/dark/{name}-mobile.svg">',
        f'  <source media="(max-width: 600px)" srcset="assets/light/{name}-mobile.svg">',
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/dark/{name}.svg">',
        f'  <img src="assets/light/{name}.svg" width="840" alt="{escape(alt)}">',
        "</picture>",
    ])
    return f'<a href="{escape(url)}">\n{image}\n</a>' if url else image


def actions(config: dict) -> list[tuple[str, str]]:
    return [(PLAY, config["game"]["url"]), *[
        ("LinkedIn" if link["label"] == "LINKEDIN" else link["label"].title(), link["url"])
        for link in config["links"]
    ]]


def buttons(links: list[tuple[str, str]], start: int = 0) -> str:
    tags = []
    for i, (label, url) in enumerate(links, start):
        tags.append(
            f'<a href="{escape(url)}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/dark/action-{i}.svg">'
            f'<img src="assets/light/action-{i}.svg" alt="{escape(label)}"></picture></a>'
        )
    return '<p align="left">' + ' &nbsp; '.join(tags) + '</p>'


def profile_block(st: dict, config: dict) -> str:
    game_url = config["game"]["url"]
    links = actions(config)
    projects = [picture(f"project-{i}", f"{project['title'] or project['name']}. "
                        f"{project['desc'] or 'Public GitHub project'}. Open repository.", project["url"])
                for i, project in enumerate(st["projects"], 1)]
    return "\n\n".join([
        f"# {config['display_name']}",
        picture("boot", f'{config["logo"]} boot screen. Press start to play the contribution platformer.', game_url),
        picture("intro", config["intro"]),
        buttons(links),
        picture("skills", "Player Select. " + "; ".join(
            f"{sk['name']}: {'in training' if sk['training'] else str(sk['repos']) + ' public repositories with evidence'}"
            for sk in st["skills"])),
        picture("stages", "Unlocked Stages. Open a gold project card below to view its repository."),
        *projects,
        picture("level", f"World {st['year']}. Taller platforms show busier weeks. Click to play.", game_url),
        picture("scores", f"High Scores. {st['contribs']} contributions, {st['streak']}-day current streak, "
                f"{st['stars']} project stars and {st['followers']} followers."),
        picture("contact", "Continue? Use the contact links below."),
        buttons(links[1:], 1),
        picture("footer", "What I learned building this. " + " ".join(config["lessons"])),
    ])


def render_files(st: dict, readme: str, config: dict = CONFIG) -> dict[Path, str]:
    if not st["calendar"]:
        raise ValueError("Cannot render an empty contribution calendar")
    start, end = "<!-- PROFILE:START -->", "<!-- PROFILE:END -->"
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) > readme.index(end):
        raise ValueError("README needs exactly one ordered PROFILE block")
    before, remaining = readme.split(start)
    _, after = remaining.split(end)
    files = {README: f"{before}{start}\n\n{profile_block(st, config)}\n\n{end}{after}",
             LEVEL: export_level(st, config)}
    for theme in THEMES:
        for narrow in (False, True):
            th = palette(theme, config, st["today"], narrow)
            th["mode"] = theme
            suffix = "-mobile" if narrow else ""
            for name, panel in PANELS.items():
                renderer = panel if callable(panel) else panel.render
                if narrow:
                    renderer = mobile.RENDER.get(name, renderer)
                files[Path(f"assets/{theme}/{name}{suffix}.svg")] = renderer(st, th, config)
            for i, project in enumerate(st["projects"], 1):
                files[Path(f"assets/{theme}/project-{i}{suffix}.svg")] = gold.project(project, i, th)
        for i, (label, _) in enumerate(actions(config)):
            files[Path(f"assets/{theme}/action-{i}.svg")] = gold.button(label, {"mode": theme})
    return files


def referenced_art(readme: str) -> set[Path]:
    return {Path(path) for path in re.findall(
        r'(?:src|srcset)="(assets/(?:dark|light)/[a-z0-9-]+\.svg)"', readme
    )}


def validate(files: dict[Path, str]) -> None:
    """Reject incomplete snapshots before replacing any published files."""
    artwork = referenced_art(files[README])
    required = {*artwork, README, LEVEL}
    if not set(art_paths()) <= artwork or set(files) != required:
        raise ValueError("Snapshot has missing or unexpected files")
    for path in sorted(artwork):
        source = files[path]
        if len(source.encode("utf-8")) > BUDGET:
            raise ValueError(f"{path} exceeds {BUDGET:,} bytes")
        doc = ElementTree.fromstring(source)
        if doc.tag != "{http://www.w3.org/2000/svg}svg" or not doc.findtext("{http://www.w3.org/2000/svg}title") or len(doc) < 6:
            raise ValueError(f"{path} has no usable artwork")
        if "prefers-reduced-motion" not in source or "infinite" in source:
            raise ValueError(f"{path} violates the motion policy")
    level = json.loads(files[LEVEL])
    weeks = level["weeks"]
    if level["version"] != 1 or not re.fullmatch("[0-9a-f]{16}", level["id"]) or not 1 <= len(weeks) <= 54:
        raise ValueError("Invalid contribution level")
    if any(len(week) != 7 or any(type(value) is not int or value < 0 for value in week) for week in weeks):
        raise ValueError("Invalid contribution week")


def publish(files: dict[Path, str]) -> None:
    """Stage all changed output before replacing any target."""
    with TemporaryDirectory(dir=ROOT) as directory:
        staging = Path(directory)
        changed = []
        for path, content in files.items():
            target = ROOT / path
            if target.is_file() and target.read_bytes() == content.encode("utf-8"):
                continue
            changed.append(path)
            staged = staging / path
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_text(content, encoding="utf-8")
        for path in changed:
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            (staging / path).replace(target)
        print(f"Updated {len(changed)} snapshot files.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--check", action="store_true", help="Check the committed snapshot without networking")
    source.add_argument("--snapshot", type=Path, help="Render a previously captured shaped snapshot")
    arguments = parser.parse_args()
    try:
        if arguments.check:
            readme = (ROOT / README).read_text(encoding="utf-8")
            files = {path: (ROOT / path).read_text(encoding="utf-8") for path in {*referenced_art(readme), LEVEL}}
            files[README] = readme
        else:
            stats = json.loads(arguments.snapshot.read_text(encoding="utf-8")) if arguments.snapshot else fetch()
            files = render_files(stats, (ROOT / README).read_text(encoding="utf-8"))
        validate(files)
        if not arguments.check:
            publish(files)
        print(f"Verified {len(files) - 2} SVGs, the README, and the game level.")
    except (OSError, TypeError, ValueError, KeyError, ElementTree.ParseError, RuntimeError) as error:
        print(f"Profile snapshot failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
