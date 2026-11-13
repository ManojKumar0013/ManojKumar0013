"""Live profile data: GitHub GraphQL when a token exists, public REST + calendar otherwise."""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import urllib.request
from collections import Counter
from .kit import LANG_COLORS

CONFIG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
LOGIN = os.environ.get("PROFILE_LOGIN") or CONFIG["login"]
UA = {"User-Agent": "manoj-os-renderer", "Accept": "application/vnd.github+json"}

Q = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login){
    name login createdAt followers{totalCount}
    contributionsCollection(from:$from, to:$to){
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, orderBy:{field:PUSHED_AT,direction:DESC}){
      totalCount
      nodes{ name url isFork stargazerCount pushedAt diskUsage description primaryLanguage{name color}
        languages(first:12, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{name color} } } }
    }
  }
}"""


def _get(url, token=None, raw=False):
    h = dict(UA)
    if token: h["Authorization"] = f"bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
        body = r.read().decode()
    return body if raw else json.loads(body)


def _graphql(token, year):
    body = json.dumps({"query": Q, "variables": {
        "login": LOGIN, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
                                 headers={**UA, "Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors") or not data.get("data", {}).get("user"):
        raise RuntimeError(f"graphql: {data.get('errors')}")
    u = data["data"]["user"]
    days = [(d["date"], d["contributionCount"]) for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    repos = [{
        "name": r["name"], "url": r["url"], "fork": r["isFork"], "stars": r["stargazerCount"],
        "pushed": r["pushedAt"], "kb": r["diskUsage"] or 0, "desc": r["description"] or "",
        "lang": (r["primaryLanguage"] or {}).get("name"),
        "langs": {e["node"]["name"]: e["size"] for e in r["languages"]["edges"]},
        "colors": {e["node"]["name"]: e["node"]["color"] for e in r["languages"]["edges"]},
    } for r in u["repositories"]["nodes"]]
    return {"login": u["login"], "name": u["name"], "created": u["createdAt"], "followers": u["followers"]["totalCount"],
            "public_repos": u["repositories"]["totalCount"], "days": days, "repos": repos}


def _public(year):
    u = _get(f"https://api.github.com/users/{LOGIN}")
    raw = _get(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&sort=pushed&type=owner")
    repos = []
    for r in raw:
        langs = {} if r["fork"] else _get(r["languages_url"])
        repos.append({"name": r["name"], "url": r["html_url"], "fork": r["fork"], "stars": r["stargazers_count"],
                      "pushed": r["pushed_at"], "kb": r["size"] or 0, "desc": r["description"] or "",
                      "lang": r["language"], "langs": langs, "colors": {}})
    html = _get(f"https://github.com/users/{LOGIN}/contributions?from={year}-01-01&to={year}-12-31", raw=True)
    tips = {m.group(1): m.group(2) for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html)}
    days = []
    for m in re.finditer(r'<td[^>]*data-date="(\d{4}-\d\d-\d\d)"[^>]*id="([^"]+)"', html):
        n = re.match(r"\s*(\d+) contribution", tips.get(m.group(2), ""))
        days.append((m.group(1), int(n.group(1)) if n else 0))
    if not days:
        raise RuntimeError("contribution calendar could not be read")
    days.sort()
    return {"login": u["login"], "name": u["name"], "created": u["created_at"], "followers": u["followers"],
            "public_repos": u["public_repos"], "days": days, "repos": repos}


def fetch():
    year = dt.datetime.now(dt.timezone.utc).year
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    raw = _graphql(token, year) if token else _public(year)
    return shape(raw, year)


def _streaks(days, today):
    best = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    cur = 0
    for d, c in reversed(days):
        if d > today: continue
        if c > 0: cur += 1
        elif cur == 0 and d == today: continue
        else: break
    return cur, best


def _skills(own):
    share, total = Counter(), 0.0
    for r in own:
        tot = sum(r["langs"].values())
        if not tot: continue
        total += 1
        for k, v in r["langs"].items():
            share[k] += v / tot
    out = []
    for sk in CONFIG["skills"]:
        s = sum(share.get(lang, 0) for lang in sk["languages"]) / (total or 1)
        hits = [r["name"] for r in own if any(r["langs"].get(lang) for lang in sk["languages"])]
        level = max(1, min(10, round((s ** 0.5) * 14)))
        out.append({**sk, "share": s, "level": level, "repos": len(hits),
                    "training": s < CONFIG.get("training_below", 0.03)})
    return out


def shape(raw, year):
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date().isoformat()
    days = [(d, c) for d, c in raw["days"] if d[:4] == str(year)]
    cur, best = _streaks([x for x in days if x[0] <= today], today)
    profile_repo = raw["login"].lower()
    own = [r for r in raw["repos"] if not r["fork"]]
    colors = dict(LANG_COLORS)
    for r in own: colors.update({k: v for k, v in r["colors"].items() if v})
    skip = {profile_repo, *[x.lower() for x in CONFIG.get("exclude_projects", [])]}
    cands = [r for r in own if r["name"].lower() not in skip]
    for r in cands:
        r["days"] = (now - dt.datetime.fromisoformat(r["pushed"].replace("Z", "+00:00"))).days
    cands.sort(key=lambda r: (-r["stars"], r["days"]))
    projects = [{"name": r["name"], "url": r["url"], "stars": r["stars"], "days": r["days"], "kb": r["kb"],
                 "desc": r["desc"].strip(), "lang": r["lang"] or (max(r["langs"], key=r["langs"].get) if r["langs"] else None),
                 "n_langs": len(r["langs"])} for r in cands[: CONFIG.get("max_projects", 6)]]
    for p in projects: p["color"] = colors.get(p["lang"] or "", "#8a9892")
    created = dt.datetime.fromisoformat(raw["created"].replace("Z", "+00:00"))
    return {
        "login": raw["login"], "name": CONFIG.get("display_name") or raw["name"] or raw["login"], "year": year,
        "today": today, "uptime_days": (now - created).days,
        "followers": raw["followers"], "repos": raw["public_repos"], "own_repos": len(own),
        "stars": sum(r["stars"] for r in own),
        "contribs": sum(c for _, c in days), "streak": cur, "best_streak": best,
        "calendar": days, "skills": _skills(own), "projects": projects, "colors": colors,
        "generated": now.strftime("%Y-%m-%d %H:%M UTC"),
    }
