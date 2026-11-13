# MANOJ//OS — Playable Arcade: "Run Through My Year"

A browser game linked from Manoj Kumar's GitHub profile, where the runner from the Level Map panel jumps through his real contribution year and collects coins.
Visitors press START on the profile, play a short level built from his GitHub activity, and add their initials to a shared high-score list.

## Who it's for
- Visitors to github.com/ManojKumar0013 (recruiters, classmates, other developers) who want to play instead of just scroll.
- Manoj, who gets a profile people remember and come back to.

## Core features and experience
1. **PRESS START on the profile.** The boot panel and the Level Map panel become clickable. They open the game page, and a "▶ PLAY THE GAME" link sits under them. The README panels stay exactly as they are.
2. **Title screen.** Same look as the profile: MANOJ//OS logo, blinking PRESS START and today's top 5 scores. Start with Space/Enter, a click or a tap.
3. **The level is Manoj's real year.** Each week of his contribution calendar is one section of the level. Busy weeks become taller brick platforms, quiet weeks become flat ground and small gaps, and every active day is a coin. The level ends at a flag on the current week. When Manoj commits more, the level changes the next day.
4. **Controls.**
   - Keyboard: ←/→ or A/D to move, Space/↑/W to jump. Holding jump gives a higher jump.
   - Phone: large on-screen left, right and jump buttons.
   - P pauses, M mutes.
5. **Gameplay.**
   - The runner moves through the level from January toward the flag.
   - Coins add points. Collecting a whole week's coins gives a "PERFECT WEEK" bonus.
   - Small "bug" enemies walk the empty weeks. Jumping on a bug defeats it. Touching one costs a life.
   - Falling into a gap also costs a life. There are 3 lives.
   - Reaching the flag gives a time bonus.
   - A run lasts about 1–3 minutes.
6. **Skill power-ups.** Six pickups based on Manoj's skills appear in the level. Each one does something small and shows a short "skill unlocked" toast:
   - **Python:** double jump
   - **Java:** a shield that blocks one hit
   - **C:** speed boost
   - **JavaScript:** pulls nearby coins in
   - **React:** a second jump in mid-air
   - **Kotlin:** a short score multiplier
7. **Game over / level clear.** The screen shows score, coins, bugs defeated and time. A player with a top-10 score types 3 initials (arcade style, letters only) to join the board. Buttons: Play again, and "Visit Manoj's GitHub".
8. **Shared leaderboard.**
   - One public top-10 board, the same for every visitor.
   - It shows initials, score and date.
   - It resets each calendar year, to match "World 2026" and the level.
   - The top score also appears on the game's title screen.
9. **Fair scores.** The server checks every score before it goes on the board. Scores that a level of that size can't produce are rejected, and repeated rapid submissions from the same visitor are blocked. Offensive initials are filtered.
10. **Sound.** Short chiptune effects for jump, coin, power-up and game over. Sound is off until the visitor turns it on, so the page never makes noise without warning.
11. **Light and dark.** The game follows the visitor's system theme and uses the same palette as the profile panels.

## User flow
1. A visitor opens github.com/ManojKumar0013 and clicks PRESS START or "▶ PLAY THE GAME".
2. The game page opens on the title screen, showing the top scores.
3. They press Start, read a one-line controls hint and play through Manoj's year.
4. They reach the flag or lose all lives, then see their results.
5. If the score made the top 10, they enter 3 initials and see their place on the board.
6. They play again, or follow the link back to Manoj's GitHub.

## UI/UX feel
- Same premium arcade look as the profile: near-black (or warm paper in light mode), phosphor green, amber coins and a magenta accent. Crisp pixel art with a pixel title font and a clean monospace font for text.
- Smooth motion at a steady frame rate. No screen shake, flashing or fake glitch effects.
- Pixel-perfect scaling that fills laptop screens and fits phone screens, held sideways or upright.
- Clear "Loading level…" and "Couldn't reach the leaderboard, your score is kept on this device" messages. The game never ends on a blank screen.

## Implementation phases
- **Phase 1 (built now):**
  - The playable game page: title screen, a level from Manoj's real contribution year, keyboard and touch controls, coins, bugs, lives, the six skill power-ups, sound toggle and light/dark mode.
  - The shared top-10 leaderboard with initials, server score checks and the yearly reset.
  - The README update: clickable PRESS START and Level Map panels plus a "▶ PLAY THE GAME" link.
  - The game going live at a public web address.
- **Phase 2:**
  - Daily challenge seed (same twist for everyone each day)
  - "Ghost" replay of the current #1 run
  - Shareable result card image
  - Top score shown inside the profile's High Scores panel
- **Phase 3:**
  - Extra worlds from earlier years once Manoj has them
  - Boss fight at the December flag
  - Unlockable runner skins
  - Gamepad support

## Assumptions
- A README can't run a game, so the game lives on its own web page and the profile links to it. The existing animated panels stay unchanged.
- The game page and leaderboard are hosted and published on Emergent, which gives a public address for the README link. Publishing it may use platform credits.
- The level uses Manoj's real public contribution data and refreshes once a day. If GitHub can't be reached, the last good level is used.
- No sign-in for players. Leaderboard entries are just 3-letter initials, and no personal data is collected.
- The leaderboard keeps the top 10 per year, and older years are kept but hidden.
- Sound starts muted, and the game can also be played without sound.
- Difficulty is tuned so a first-time player can usually reach the flag in 1–3 tries.
- Bugs appear only on empty weeks, so a sparse year still feels full and a busy year rewards collecting.
