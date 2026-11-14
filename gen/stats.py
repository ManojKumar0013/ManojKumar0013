"""Collect and summarize public GitHub activity for the profile."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from urllib.parse import urlencode
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

from .kit import LANG_COLORS


def utc_day(now: dt.datetime) -> dt.date:
    """Use a single UTC boundary for snapshots, streaks and levels."""
    if now.tzinfo is None:
        raise ValueError("An aware timestamp is required")
    return now.astimezone(dt.timezone.utc).date()

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
            secondary_limit = error.code == 403 and error.headers.get("Retry-After")
            if (error.code not in (429, 500, 502, 503, 504) and not secondary_limit) or attempt == 2:
                raise
            retry_after = error.headers.get("Retry-After", "")
            if retry_after.isdecimal():
                time.sleep(min(15, int(retry_after)))
                continue
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


def get_calendar(today, token, created):
    start = max(today.replace(month=1, day=1), created)
    if token:
        try:
            data = request(f"{API}/graphql", token=token, payload={"query": GRAPHQL, "variables": {
                "login": LOGIN, "from": f"{start}T00:00:00Z", "to": f"{today}T23:59:59Z",
            }})
            if data.get("errors"):
                raise ValueError("GitHub rejected the GraphQL calendar query")
            weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
                    for week in weeks for d in week["contributionDays"]]
            return complete_calendar(days, start, today)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"GraphQL calendar unavailable ({type(error).__name__}). Reading the public calendar.")
    print("Using the best-effort public GitHub contribution calendar.")
    parser = CalendarParser()
    parser.feed(request(f"https://github.com/users/{LOGIN}/contributions?from={start}&to={today}", raw=True))
    days = [(dt.date.fromisoformat(day), count) for day, count in parser.days()]
    return complete_calendar(days, start, today)


def complete_calendar(days, start, today):
    counts = {}
    for day, count in days:
        if start <= day <= today:
            if day in counts or type(count) is not int or count < 0:
                raise ValueError("Invalid contribution count or duplicate date")
            counts[day] = count
    if len(counts) != (today - start).days + 1:
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


def streaks(days: list, today: str | None = None) -> tuple[int, int]:
    if not days:
        return 0, 0
    end = dt.date.fromisoformat(today or max(day for day, _ in days))
    best = run = 0
    counts = {dt.date.fromisoformat(day): count for day, count in days if day <= end.isoformat()}
    for day in sorted(counts):
        if counts[day]:
            run = run + 1 if counts.get(day - dt.timedelta(days=1), 0) else 1
            best = max(best, run)
        else:
            run = 0
    cursor = end if counts.get(end) else end - dt.timedelta(days=1)
    current = 0
    while counts.get(cursor, 0):
        current += 1
        cursor -= dt.timedelta(days=1)
    return current, best


def repo_evidence(repo: dict, token: str | None) -> dict:
    """Collect public Linguist bytes and repository topic declarations."""
    languages = request(repo["languages_url"], token=token)
    if not isinstance(languages, dict) or any(type(v) is not int or v < 0 for v in languages.values()):
        raise ValueError("Invalid GitHub language response")
    declared = set()
    # Check configured public manifests. Framework usage is never inferred from TypeScript alone.
    for path in CONFIG.get("manifests", {}).get(repo["name"], []):
        url = f"https://raw.githubusercontent.com/{LOGIN}/{repo['name']}/{repo['default_branch']}/{path}"
        try:
            manifest = request(url, token=None)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                continue
            raise
        declared.update(manifest.get("dependencies", {}))
        declared.update(manifest.get("devDependencies", {}))
    return {**repo, "languages": languages, "dependencies": declared}


def skill_levels(repos: list[dict], config: dict) -> list[dict]:
    """Report an evidence count and a capped arcade level, never proficiency."""
    result = []
    for skill in config["skills"]:
        names = set(skill.get("languages", []))
        topics = set(skill.get("topics", []))
        hits = [repo for repo in repos if
                names.intersection(name for name, size in repo["languages"].items() if size > 0)
                or topics.intersection(repo.get("topics", []))
                or set(skill.get("dependencies", [])).intersection(repo.get("dependencies", []))]
        count = len(hits)
        result.append({**skill, "repos": count, "level": min(count, config["level_cap"]), "training": not count})
    return result


def last_commit(repos: list[dict], token: str | None) -> dict | None:
    """Find the latest matching public default-branch authored commit."""
    candidates = sorted(repos, key=lambda repo: repo["pushed_at"] or "", reverse=True)
    latest = None
    for repo in candidates:
        if latest and repo["pushed_at"] and timestamp(repo["pushed_at"]) < latest["instant"]:
            break
        query = urlencode({"author": LOGIN, "per_page": 1})
        try:
            commits = request(f"{API}/repos/{LOGIN}/{repo['name']}/commits?{query}", token=token)
        except urllib.error.HTTPError as error:
            if error.code == 409:  # A new or empty repository has no commits.
                continue
            raise
        if commits:
            commit = commits[0]
            instant = timestamp(commit["commit"]["committer"]["date"])
            if latest is None or instant > latest["instant"]:
                latest = {"instant": instant, "date": instant.date().isoformat(),
                          "repo": repo["name"], "url": commit["html_url"],
                          "title": commit["commit"]["message"].splitlines()[0]}
    if latest:
        latest.pop("instant")
    return latest


def first_public_pr(token: str | None) -> str | None:
    query = urlencode({"q": f"is:pr is:public author:{LOGIN}", "sort": "created", "order": "asc", "per_page": 1})
    result = request(f"{API}/search/issues?{query}", token=token)
    if result.get("incomplete_results"):
        raise ValueError("GitHub returned incomplete pull request search results")
    return result["items"][0]["html_url"] if result["items"] else None


def timestamp(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def shape(account: dict, repos: list[dict], calendar: list, today: dt.date,
          shipped: dict | None, first_pr: str | None, config: dict = CONFIG) -> dict:
    """Build the shared snapshot without performing network calls."""
    own = [r for r in repos if not r["fork"] and not r.get("archived") and
           r["name"].casefold() != account["login"].casefold()]
    today_key = today.isoformat()
    calendar = sorted((day, count) for day, count in calendar if day[:4] == str(today.year) and day <= today_key)
    streak, best = streaks(calendar, today_key)
    featured = config.get("featured", {})
    excluded = {name.casefold() for name in config.get("exclude_projects", [])}
    candidates = [repo for repo in own if repo["name"].casefold() not in excluded]
    ordering = {key: i for i, key in enumerate(featured)}
    candidates.sort(key=lambda r: (ordering.get(r["name"], len(ordering)), -r["stargazers_count"],
                                   -timestamp(r["pushed_at"] or r["created_at"]).timestamp(), r["name"]))
    projects = []
    for r in candidates[:config["max_projects"]]:
        project = featured.get(r["name"], {})
        language = r.get("language")
        projects.append({"name": r["name"], "title": project.get("title"), "url": r["html_url"],
                         "stars": r["stargazers_count"], "days": max(0, (today - timestamp(r["pushed_at"] or r["created_at"]).date()).days),
                         "kb": r["size"], "desc": project.get("description", r.get("description") or ""),
                         "lang": language, "n_langs": len(r["languages"]), "color": LANG_COLORS.get(language, "#687c74")})
    languages = {name for repo in own for name, size in repo["languages"].items() if size > 0}
    return {"login": account["login"], "name": config["display_name"], "today": today_key, "year": today.year,
            "uptime_days": (today - timestamp(account["created_at"]).date()).days, "followers": account["followers"],
            "repos": len(repos), "own_repos": len(own), "stars": sum(r["stargazers_count"] for r in own),
            "contribs": sum(c for _, c in calendar), "calendar": calendar, "streak": streak, "best_streak": best,
            "skills": skill_levels(own, config), "projects": projects, "shipped": shipped, "first_pr": first_pr,
            "languages": len(languages), "generated": today_key + " UTC"}


def fetch() -> dict:
    today = utc_day(dt.datetime.now(dt.timezone.utc))
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    account = request(f"{API}/users/{LOGIN}", token=token)
    public = list(get_repositories(token).values())
    own = [r for r in public if not r["fork"] and not r.get("archived") and r["name"].casefold() != LOGIN.casefold()]
    with ThreadPoolExecutor(max_workers=6) as pool:
        cal = pool.submit(get_calendar, today, token, timestamp(account["created_at"]).date())
        pr = pool.submit(first_public_pr, token)
        shipped = pool.submit(last_commit, own, token)
        tasks = {repo["name"]: pool.submit(repo_evidence, repo, token) for repo in own}
        repos = [tasks[r["name"]].result() if r["name"] in tasks else r for r in public]
        return shape(account, repos, cal.result(), today, shipped.result(), pr.result())
