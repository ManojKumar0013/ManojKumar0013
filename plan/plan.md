# MANOJ//OS release plan

## Audit and milestones

1. **Playable game.** The original boot and contribution map formed a strong visual identity, but the original plan had no playable game or board. Implemented a canvas platformer, daily calendar export, local scores, and an optional replay-validated service.
2. **AI/ML evidence.** The original cards measured language mix and inferred React from TypeScript. The updated cards count public repository evidence. Added training goals, latest authored commit, and achievements.
3. **Visual polish.** Original art compressed to tiny type at phone widths and used perpetual animations. Added dedicated narrow layouts, improved text palettes, finite motion, seasonal palettes, and a cosmetic title-screen code. The browser QA target is both themes at 390 and 840 pixels.
4. **Quality.** Added defensive data validation, offline snapshot checks, CI, retry/backoff, and safe fast-forward refresh commits.
5. **Docs.** Documented architecture, fork setup, game controls, leaderboard choices, deployment and interview talking points.

## Backlog by priority

| Priority | Item | How to verify |
| --- | --- | --- |
| P1 | Publish a reproducible ML baseline with metrics, a fixed data split, and error analysis | Run it from a clean environment and compare the report with the baseline |
| P1 | Exercise the shared board against a deployed Worker and keep a short grace window for previous level IDs | Finish a run across a snapshot refresh and confirm both IDs are verified against their own content |
| P2 | Add a daily challenge and verified ghost replays | Replay the same seed and input log in two browsers and compare completion time and score |
| P3 | Extend to archived contribution years, gamepads, and unlockable skins | Add seeded fixtures and verify keyboard, touch, and gamepad runs independently |
