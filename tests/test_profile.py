"""Offline contracts for profile statistics, rendering and generated output."""
import datetime as dt
from hashlib import sha256
from unittest import TestCase
from xml.etree import ElementTree

from gen.__main__ import LEVEL, README, ROOT, art_paths, render_files, validate
from gen.kit import fit, palette, wrap
from gen.stats import CONFIG, CalendarParser, complete_calendar, shape, skill_levels, streaks, utc_day


def repository(name, languages, **overrides):
    return {"name": name, "languages": languages, "topics": [], "size": 4, "fork": False,
            "archived": False, "pushed_at": "2026-01-04T12:00:00Z", "created_at": "2026-01-01T00:00:00Z",
            "html_url": f"https://github.com/example/{name}", "stargazers_count": 0, "language": "Python", **overrides}


def fixture():
    config = {**CONFIG, "login": "example", "display_name": "Example"}
    repos = [repository("Example", {"Python": 500}), repository("Fork", {"Cuda": 10}, fork=True),
             repository("My_Very_Long-Project_Name", {"TypeScript": 30, "Python": 150},
                        topics=["pytorch", "react"], stargazers_count=2),
             repository("Notebook", {"Jupyter Notebook": 100}, topics=["jupyter"])]
    account = {"login": "example", "created_at": "2025-12-01T12:00:00Z", "followers": 0}
    today = dt.date(2026, 1, 6)
    calendar = [("2026-01-01", 0), ("2026-01-02", 2), ("2026-01-03", 1), ("2026-01-04", 0),
                ("2026-01-05", 3), ("2026-01-06", 0)]
    return shape(account, repos, calendar, today, None, None, config), config


class StatsTests(TestCase):
    def test_shape_excludes_forks_and_profile_from_evidence(self):
        result, _ = fixture()
        self.assertEqual((result["repos"], result["own_repos"], result["stars"]), (4, 2, 2))
        self.assertEqual((result["contribs"], result["streak"], result["best_streak"]), (6, 1, 2))
        self.assertEqual(result["projects"][0]["name"], "My_Very_Long-Project_Name")
        self.assertEqual(result["languages"], 3)
        self.assertIsNone(result["shipped"])

    def test_skill_topics_not_inferred_from_unrelated_languages(self):
        repo = repository("typescript", {"TypeScript": 40, "Jupyter Notebook": 10})
        skills = {skill["key"]: skill for skill in skill_levels([repo], CONFIG)}
        self.assertTrue(skills["react"]["training"])
        self.assertFalse(skills["jupyter"]["training"])
        self.assertEqual(skills["pytorch"]["level"], 0)
        from_topics = repository("react", {}, topics=["reactjs"])
        skills = {skill["key"]: skill for skill in skill_levels([from_topics] * 12, CONFIG)}
        self.assertEqual(skills["react"]["level"], CONFIG["level_cap"])
        self.assertEqual(skills["react"]["repos"], 12)

    def test_boundaries_today_yesterday_gap_and_midnight(self):
        self.assertEqual(streaks([("2026-01-01", 1), ("2026-01-03", 1)], "2026-01-04"), (1, 1))
        self.assertEqual(streaks([("2026-01-01", 1)], "2026-01-03"), (0, 1))
        self.assertEqual(streaks([("2026-01-01", 1), ("2026-01-02", 1)], "2026-01-02"), (2, 2))
        self.assertEqual(utc_day(dt.datetime.fromisoformat("2026-01-01T00:30:00+05:30")), dt.date(2025, 12, 31))
        self.assertEqual(utc_day(dt.datetime.fromisoformat("2026-01-01T23:45:00-02:00")), dt.date(2026, 1, 2))
        with self.assertRaises(ValueError):
            utc_day(dt.datetime(2026, 1, 1))

    def test_fallback_schema(self):
        parser = CalendarParser()
        parser.feed('<tool-tip for="first">1,234 contributions on January 1st.</tool-tip>'
                    '<td id="first" data-date="2026-01-01"></td>'
                    '<td data-date="2026-01-02" id="second"></td>'
                    '<tool-tip for="second">No contributions on January 2nd.</tool-tip>')
        rows = [(dt.date.fromisoformat(day), n) for day, n in parser.days()]
        self.assertEqual(complete_calendar(rows, rows[0][0], rows[1][0])[-1], ("2026-01-02", 0))
        for invalid in (rows[1:], rows + rows, [(rows[0][0], -1), rows[1]]):
            with self.assertRaises(ValueError):
                complete_calendar(invalid, rows[0][0], rows[1][0])
        parser.feed('<td id="invalid" data-date="2026-01-03"></td>')
        with self.assertRaises(ValueError):
            list(parser.days())


class RenderTests(TestCase):
    def test_text_fit(self):
        self.assertEqual(fit("  plain  text ", 10), "plain text")
        self.assertEqual(fit("long", 1), "…")
        self.assertEqual(fit("long", 0), "")
        self.assertEqual(wrap("a very long word", 5, 2), ["a", "very…"])
        self.assertTrue(all(len(line) <= 12 for line in wrap("HungryHub-Online-Food-Ordering-System-", 12, 2)))
        self.assertEqual(wrap("any", 4, 0), [])

    def test_snapshot_budget_and_semantics(self):
        stats, config = fixture()
        source = "<!-- PROFILE:START -->\n<!-- PROFILE:END -->"
        result = render_files(stats, source, config)
        self.assertEqual(result, render_files(stats, source, config))
        validate(result)
        encoded = "".join(result[path] for path in sorted(result))
        self.assertEqual(sha256(encoded.encode()).hexdigest(), "c8311da7924c1f6a7d44e00022f005a991658b7dc89f8bc48aedcf9454aaa43a")
        self.assertIn("IN TRAINING", result[README].upper())
        self.assertEqual(len(art_paths()), 32)
        self.assertNotEqual(palette("dark", config, "2026-12-01")["green"],
                            palette("dark", config, "2026-11-01")["green"])
        for path in art_paths():
            xml = ElementTree.fromstring(result[path])
            width = "420" if path.stem.endswith("-mobile") else "840"
            self.assertEqual(xml.get("width"), width)
        malformed = {**result, art_paths()[0]: "<svg>"}
        with self.assertRaises(ElementTree.ParseError):
            validate(malformed)

    def test_published_snapshot(self):
        paths = {*art_paths(), README, LEVEL}
        validate({path: (ROOT / path).read_text(encoding="utf-8") for path in paths})
