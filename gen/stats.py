"""Collect and summarize public GitHub activity for the profile."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

from .kit import LANG_COLORS

CONFIG = json.loads(Path(__file__).with_name("config.json").read_text(encoding="utf-8"))
LOGIN = os.environ.get("PROFILE_LOGIN") or CONFIG["login"]
API = "https://api.github.com"
HEADERS = {"User-Agent": "manoj-os-renderer", "Accept": "application/vnd.github+json"}
GRAPHQL = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def request(url, *, token=None, payload=None, raw=False):
    headers = dict(HEADERS)
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode("utf-8") if raw else json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (500, 502, 503, 504) or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


class CalendarParser(HTMLParser):
    """Read the public calendar's date cells and their matching tooltips."""

    def __init__(self):
        super().__init__()
        self.dates = {}
        self.tooltips = {}
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and attrs.get("data-date") and attrs.get("id"):
            self.dates[attrs["id"]] = attrs["data-date"]
        if tag == "tool-tip" and attrs.get("for"):
            self.current = attrs["for"]
            self.tooltips[self.current] = ""

    def handle_data(self, data):
        if self.current:
            self.tooltips[self.current] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.current = None

    def days(self):
        for key, day in self.dates.items():
            tip = self.tooltips.get(key, "").strip()
            match = re.match(r"([\d,]+) contributions?\b", tip)
            if match:
                yield day, int(match[1].replace(",", ""))
            elif tip.startswith("No contributions"):
                yield day, 0
            else:
                raise ValueError(f"Unrecognized GitHub calendar tooltip for {day}")


def get_calendar(today, token):
    start = today.replace(month=1, day=1)
    if token:
        try:
            data = request(f"{API}/graphql", token=token, payload={"query": GRAPHQL, "variables": {
                "login": LOGIN, "from": f"{start}T00:00:00Z", "to": f"{today}T23:59:59Z",
            }})
            weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
                    for week in weeks for d in week["contributionDays"]]
            return complete_calendar(days, start, today)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"GraphQL calendar unavailable ({type(error).__name__}). Reading the public calendar.")
    parser = CalendarParser()
    parser.feed(request(f"https://github.com/users/{LOGIN}/contributions?from={start}&to={today}", raw=True))
    days = [(dt.date.fromisoformat(day), count) for day, count in parser.days()]
    return complete_calendar(days, start, today)


def complete_calendar(days, start, today):
    counts = {day: count for day, count in days if start <= day <= today}
    first = min(counts, default=today)
    # A newly created account (or GitHub's trailing calendar window) can start after January 1.
    if not counts or len(counts) != (today - first).days + 1:
        raise ValueError("GitHub returned an empty or incomplete contribution calendar")
    return [(day.isoformat(), count) for day, count in sorted(counts.items())]


def get_repositories(token):
    public = []
    for page in range(1, 101):
        rows = request(f"{API}/users/{LOGIN}/repos?type=owner&sort=full_name&per_page=100&page={page}", token=token)
        public.extend(r for r in rows if not r["private"] and r["owner"]["login"].casefold() == LOGIN.casefold())
        if len(rows) < 100:
            return {r["name"].casefold(): r for r in public}
    raise RuntimeError("GitHub repository pagination exceeded 100 pages")


def streaks(days):
    best = run = previous = 0
    for _, count in days:
        previous, run = run, run + 1 if count else 0
        best = max(best, run)
    return run or previous, best


def fetch():
    today = dt.datetime.now(dt.timezone.utc).date()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    account = request(f"{API}/users/{LOGIN}", token=token)
    public = get_repositories(token)
    own = {name: repo for name, repo in public.items()
           if not repo["fork"] and name != LOGIN.casefold()}
    with ThreadPoolExecutor(max_workers=4) as pool:
        calendar_task = pool.submit(get_calendar, today, token)
        language_tasks = [pool.submit(request, repo["languages_url"], token=token) for repo in own.values()]
        languages = [task.result() for task in language_tasks]
        calendar = calendar_task.result()
    streak, best = streaks(calendar)
    projects = []
    for project in CONFIG["projects"]:
        repo = own.get(project["repo"].casefold())
        if repo is None:
            print(f"Skipping unavailable public project: {project['repo']}")
            continue
        projects.append({**project, "url": repo["html_url"], "stars": repo["stargazers_count"],
                         "color": LANG_COLORS.get(repo["language"], "#8a9892")})
    if not projects:
        raise ValueError("No configured featured projects were found")

    skills = []
    for skill in CONFIG["skills"]:
        count = sum(any(repo.get(lang, 0) for lang in skill["languages"]) for repo in languages)
        skills.append({**skill, "repos": count})

    return {
        "login": account["login"], "name": CONFIG["display_name"], "year": today.year,
        "today": today.isoformat(), "followers": account["followers"], "repos": len(public),
        "own_repos": len(own), "stars": sum(r["stargazers_count"] for r in own.values()),
        "contribs": sum(count for _, count in calendar), "streak": streak, "best_streak": best,
        "calendar": calendar, "skills": skills, "projects": projects,
    }
