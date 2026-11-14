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
from .panels import achievements, boot, contact, level, mobile, scores, skills, stages, training
from .stats import CONFIG, fetch

ROOT = Path(__file__).resolve().parents[1]
PANELS = {"boot": boot, "training": training, "skills": skills, "achievements": achievements,
          "stages": stages, "level": level, "scores": scores, "contact": contact}
BUDGET = 150_000
PLAY = "▶ PLAY THE GAME"
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


def profile_block(st: dict, config: dict) -> str:
    game_url = config["game"]["url"]
    shipped = st["shipped"]
    evidence = []
    if shipped:
        evidence.append(f"[Latest public commit]({shipped['url']})")
    if st["first_pr"]:
        evidence.append(f"[Earliest public PR found]({st['first_pr']})")
    projects = ["| Project | What it does |", "| --- | --- |"]
    for project in st["projects"]:
        name = project["title"] or project["name"]
        description = " ".join((project["desc"] or "Public GitHub project").split()).replace("|", r"\|")
        projects.append(f"| [{name}]({project['url']}) | {description} |")
    links = " · ".join(f"[{link['label'].title()}]({link['url']})" for link in config["links"])
    return "\n\n".join(filter(None, [
        f"# {config['display_name']}",
        picture("boot", f'{config["logo"]} boot screen. Press start to play the contribution platformer.', game_url),
        f"**[{PLAY}]({game_url})**",
        config["intro"],
        links,
        picture("training", "Now Training. " + " · ".join(config["goals"]) + ". The loss curve is illustrative."),
        picture("skills", "Player Select. " + "; ".join(
            f"{sk['name']}: {'in training' if sk['training'] else str(sk['repos']) + ' public repositories with evidence'}"
            for sk in st["skills"])),
        picture("achievements", f"Achievements. Best streak: {st['best_streak']} days. "
                f"{st['own_repos']} public projects and {st['languages']} languages."),
        " · ".join(evidence),
        picture("stages", "Unlocked Stages. Featured public repositories are linked below."),
        "\n".join(projects),
        picture("level", f"World {st['year']}. Taller platforms show busier weeks. Click to play.", game_url),
        picture("scores", f"High Scores. {st['contribs']} contributions, {st['streak']}-day current streak, "
                f"{st['stars']} project stars and {st['followers']} followers."),
        picture("contact", "Continue? Use the contact links below."),
        links,
    ]))


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
            suffix = "-mobile" if narrow else ""
            for name, panel in PANELS.items():
                renderer = mobile.RENDER.get(name, panel.render) if narrow else panel.render
                files[Path(f"assets/{theme}/{name}{suffix}.svg")] = renderer(st, th, config)
    return files


def validate(files: dict[Path, str]) -> None:
    """Reject incomplete snapshots before replacing any published files."""
    required = {*art_paths(), README, LEVEL}
    if set(files) != required:
        raise ValueError("Snapshot has missing or unexpected files")
    for path in art_paths():
        source = files[path]
        if len(source.encode("utf-8")) > BUDGET:
            raise ValueError(f"{path} exceeds {BUDGET:,} bytes")
        doc = ElementTree.fromstring(source)
        if doc.tag != "{http://www.w3.org/2000/svg}svg" or not doc.get("aria-label") or len(doc) < 6:
            raise ValueError(f"{path} has no usable artwork")
        if "prefers-reduced-motion" not in source or "infinite" in source:
            raise ValueError(f"{path} violates the motion policy")
    links = set(re.findall(r'(?:src|srcset)="(assets/[^"]+)"', files[README]))
    if links != {str(path) for path in art_paths()}:
        raise ValueError("README panel links do not match the generated artwork")
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
            files = {path: (ROOT / path).read_text(encoding="utf-8") for path in {*art_paths(), README, LEVEL}}
        else:
            stats = json.loads(arguments.snapshot.read_text(encoding="utf-8")) if arguments.snapshot else fetch()
            files = render_files(stats, (ROOT / README).read_text(encoding="utf-8"))
        validate(files)
        if not arguments.check:
            publish(files)
        print(f"Verified {len(art_paths())} panels, the README, and the game level.")
    except (OSError, TypeError, ValueError, KeyError, ElementTree.ParseError, RuntimeError) as error:
        print(f"Profile snapshot failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
