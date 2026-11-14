"""Export the calendar to the versioned game data contract."""
from datetime import date, timedelta
from hashlib import sha256
import json


def export_level(stats: dict, config: dict) -> str:
    first = date(stats["year"], 1, 1)
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    today = date.fromisoformat(stats["today"])
    counts = dict(stats["calendar"])
    weeks = [[counts.get((start + timedelta(days=i + j)).isoformat(), 0) for j in range(7)]
             for i in range(0, (today - start).days + 1, 7)]
    level = {"version": 1, "year": stats["year"], "weeks": weeks}
    level["id"] = sha256(json.dumps(level, separators=(",", ":")).encode()).hexdigest()[:16]
    level.update(login=stats["login"], logo=config["logo"], game=config["game"])
    return json.dumps(level, separators=(",", ":"), ensure_ascii=False) + "\n"
