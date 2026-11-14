# MANOJ//OS Arcade Edition

The GitHub profile README leads with a short introduction, public portfolio and contact links, and a curated project catalog. Local light and dark SVGs show the arcade banner, project cartridges, language counts, contribution map, and scoreboard.

- `gen/config.json` contains the profile identity, public project descriptions, and languages.
- `gen/stats.py` reads public repositories via REST. It uses GitHub’s contribution calendar via GraphQL when available and falls back to the public calendar.
- `python -m gen` builds a snapshot. `python -m gen --check` verifies the README references and all ten SVG files offline.
- `.github/workflows/render.yml` checks pull requests and refreshes the default branch daily, on eligible pushes, and on demand. A failed refresh leaves the published commit in place.
- `plan/plan.md` records the original arcade concept.
