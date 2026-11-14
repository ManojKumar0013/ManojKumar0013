# MANOJ//OS — Arcade Edition (GitHub profile README for ManojKumar0013)
## Problem
Unique animated profile README like github.com/Ru0k3/Ru0k3, showing skills, with great ideas.
## Architecture
Pure Python (stdlib only) generator `python -m gen` -> animated SVGs in assets/{dark,light}/; README uses <picture> for theme switching.
- gen/stats.py: GraphQL (Actions token) or public REST + contributions page locally
- gen/panels: boot, skills, scores, level, stages, contact
- .github/workflows/render.yml: daily 03:17 UTC refresh; failed fetch exits 1, assets untouched
- gen/config.json: name, tagline, links, skills mapping (React->TypeScript), exclusions
- preview.html (gitignored) for local viewing
## Done (2026-11-13)
- Phase 1: all 6 panels, light/dark, daily refresh, auto project links in README; tested (iteration_1: 100%)
## Backlog
- P1: achievements panel, "now playing" line, visitor credits counter
- P2: seasonal looks, cheat-code easter egg, weekly health report
