# Make your own

1. Create a public repository with the same name as your GitHub username and copy this project into it.
2. Edit `gen/config.json` with your login, name, links, intro, learning goals, featured projects, skill evidence and seasonal colors. Set `game.url` to `https://YOUR-LOGIN.github.io/YOUR-LOGIN/game/`.
3. Run `python -m gen` from the repository root with Python 3.10 or later. It can use public GitHub endpoints without a token. For GraphQL locally, set a GitHub token in your shell as `GH_TOKEN`. GitHub Actions uses the built-in token automatically.
4. Run `python -m unittest discover -s tests -v`, `python -m gen --check`, and `node --test tests/game.test.mjs` (Node 24). Use `python -m http.server 8000` and open `http://localhost:8000/game/` to play locally.
5. Commit the generated README, SVGs and `game/level.json`. Deploy using the steps below.

The local snapshot test reads the checkout’s config. Recalculate its SHA-256 expectation after intentional rendering or config changes and inspect the changed artwork. Keep project and skill claims grounded in public repositories, linked evidence, or explicitly labeled learning goals.

## Publish the game

1. Open the profile repository on GitHub. Go to **Settings → Pages → Build and deployment → Source** and select **GitHub Actions**.
2. Open **Actions → Deploy arcade to Pages → Run workflow**, select `main`, and run it. Open the game at the configured `game.url`. Scheduled snapshot refreshes trigger subsequent game deployments.
3. In **Actions → Render profile**, run a manual refresh and confirm that the generator, snapshot check, and commit step succeed. The built-in `GITHUB_TOKEN` needs repository contents write permission for this job. If branch rules block its push, use a branch rules exception for the workflow or publish generated commits by pull request.

## Enable the shared score board

1. Sign in to a Cloudflare account on Workers Free. From the repo root run `cd leaderboard` followed by `npx wrangler login`.
2. Verify `GAME_ORIGIN` and `LEVEL_URL` in `wrangler.toml`. Run `npx wrangler deploy` in that directory. Its SQLite-backed Durable Object is migrated by Wrangler. No custom secret is required.
3. In `gen/config.json`, set `game.leaderboard` to the deployed Worker URL followed by `/scores`. Run the generator, commit the config and output, and redeploy the game.
4. From the deployed game, finish a scoring run and submit three initials. Confirm the shared score appears in a separate browser. Disable the network and confirm that the game still loads after an online visit and saves scores on-device.

### Leaderboard trade-offs

- The game ships in local-only mode and works without any accounts or tokens for players.
- An optional Workers Free deployment gives all players the same yearly top ten, within Cloudflare’s free quotas.
- The Worker recomputes each score from the replay and the current published level. It rejects impossible inputs, but software can still play valid runs.
- A per-visitor rate limit allows four submissions per minute. Throttling uses a day-scoped hash of the network address; public rows contain only initials, score, and date.
- A changed level or an unreachable service falls back to local saves. Local scores are not uploaded later.
