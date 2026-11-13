# MANOJ//OS — Arcade Edition (GitHub Profile README)

A new animated GitHub profile for Manoj Kumar (github.com/ManojKumar0013). The whole page tells one story: an old-style arcade machine starts up a hacker-style operating system, and the visitor "plays" through Manoj's skills, stats and projects.
It replaces the current README, which uses standard badges and third-party stats cards, with a set of original moving panels. Like the Ru0k3 profile, the panels update themselves every day with live GitHub data.

## Who it's for
- Recruiters, internship reviewers, classmates and other developers who visit github.com/ManojKumar0013.
- Manoj, a B.Tech CSE student who wants a profile that stands out and updates itself without manual edits.

## Core features and experience
Each section of the README is one moving panel. The animation is built into the images, so it plays on GitHub with no outside services.

1. **Opening screen** — a sleek screen powers on with a soft glow and a short startup log typing out. Then "MANOJ//OS" appears with a blinking `PRESS START` and a tagline: "B.Tech CSE · Machine Learning & Systems".
2. **Player Select (skills)** — six skills shown as game character cards, each with a pixel icon and a level bar: C, Python, Java, React, Kotlin, JavaScript. Each card also looks like a program installed on the system (`pkg: python · installed`). Level bars are based on how much each language appears across Manoj's repos. Skills with little or no code yet (for example Kotlin or React) show as "in training" with a small starting bar, not as empty.
3. **High Score Table (stats)** — live numbers shown as an arcade scoreboard: contributions this year, current and longest streak, public repos, stars and followers.
4. **Level Map (contributions)** — the yearly activity graph drawn as a pixel game level. Days with activity become platforms and coins, and a small pixel character jumps across them. It's built to look good even when activity is spread out.
5. **Unlocked Stages (projects)** — top projects shown as game cartridges with name, description, main language and stars. These are picked automatically from recent and popular repos. Today that would be icepop, Circle-Accuracy-Challenge, Time-Tick-Quiz, portfolio, neetcode-submissions and the Clinic Appointment System.
6. **Continue? (contact)** — an "INSERT COIN TO CONNECT" panel for LinkedIn and email. Plain clickable links sit below it, because individual links inside an image can't be clicked on GitHub.
7. **Daily refresh** — an automatic daily job on GitHub redraws the panels with fresh data and saves them to the repo.
8. **Light and dark mode** — the panels look right in both GitHub themes.

## User flow
1. A visitor opens the profile. The machine starts up, MANOJ//OS appears and `PRESS START` blinks.
2. They scroll down: Player Select shows the skills, High Score shows the stats and the Level Map shows the year's activity.
3. Under Unlocked Stages they click into a project.
4. At Continue? they click LinkedIn or email.
5. The panels update on their own every day.

## UI/UX feel
- **High-end, not cartoonish.** The arcade and hacker-system idea is done in a premium way, like a polished game studio's title screen, not a cheap retro template.
- Deep near-black base with one controlled palette: soft phosphor green as the main color, warm amber and a single magenta accent used sparingly. Subtle glow and depth, no neon overload.
- Clean, crisp text everywhere. A sharp pixel-style display font is used only for big titles, and a refined monospace font for everything else, so it stays easy to read.
- Every panel is the same width, with the same corner radius, spacing grid and window title bar (for example `player_select.exe`), so the page reads as one designed product.
- Smooth, calm motion: elements ease in, bars fill, the character runs, text types out once. No flicker, no shaking, no fake "glitch" effects, nothing that flashes or looks broken.
- Pixel icons for each skill are drawn by hand for this profile, not low-resolution logos.

## Quality bar ("everything works, no glitches")
- **No broken images:** everything is generated and stored in Manoj's own repo. No outside stats services that can go down, be rate-limited or show errors (the reason the current cards sometimes fail).
- **Sharp on every screen:** panels are vector images, so they stay crisp on phones, laptops and high-resolution displays, and they shrink cleanly to fit the GitHub mobile app and narrow screens.
- **Right in both themes:** each panel has a separate light and dark version that GitHub picks automatically. No invisible text or white boxes on dark mode.
- **Animations that GitHub actually plays:** only animation types that GitHub allows inside images are used, and every panel also looks complete as a still frame, so nothing appears half-loaded in viewers that don't animate.
- **Safe daily refresh:** if GitHub's data can't be fetched one day, the last good panels stay up instead of showing zeros or blanks. A failed run never replaces working panels.
- **Real numbers only:** every number shown comes from Manoj's live GitHub data. Nothing is made up or hard-coded.
- **Text never spills:** long project names and descriptions are shortened neatly so they never overflow their cards.
- **Loads fast:** panels are kept small so the profile appears quickly.
- **Checked before handover:** every panel is reviewed in light mode, dark mode, desktop width and phone width before delivery.

## Implementation phases
- **Phase 1 (first version, built now):** all six panels above at the full quality bar, a new README for ManojKumar0013 that replaces the old badges and stats cards, the daily refresh job, contact links and light/dark support.
- **Phase 2:** an achievements panel (first commit, longest streak, languages unlocked, NeetCode problems solved), a "now playing" line showing what Manoj is working on, and a visitor counter styled as game credits.
- **Phase 3:** seasonal and festival looks for the arcade machine, a hidden "cheat code" easter egg in a collapsible section, and a weekly profile health report like Ru0k3's.

## Assumptions
- Name: Manoj Kumar. GitHub user: ManojKumar0013. The finished files are meant for the `ManojKumar0013/ManojKumar0013` profile repo.
- The workspace currently holds a different person's profile repo (saharshbaiju). Its content will be replaced with Manoj's new profile, and nothing from it is kept or shown. To publish, Manoj uses "Save to GitHub" to push to his own ManojKumar0013 repo, or copies the files into it.
- Contact links come from the current README: LinkedIn (linkedin.com/in/manoj-kumar-bondada-a92410384) and email (manojkumarbondada123@gmail.com). There's no X or Instagram unless added later.
- The tagline uses the current bio ("B.Tech CSE Student · Interested in Machine Learning & Systems") and can be edited.
- The old README's skill badges also listed HTML5 and CSS3. The new profile shows only the six skills Manoj named.
- "High class" is read as a premium, polished version of the chosen arcade and hacker-system theme, not a switch to a different theme. Scan lines and screen noise are dropped in favor of a clean glow.
- "No glitches" is read as: no broken or missing images, no flicker or fake glitch effects, and correct display on mobile and in light and dark mode.
- The third-party stats cards, streak card and random quote are removed and replaced by the built-in panels.
- The repos named in feature 5 are examples from today's profile. The panel picks featured projects automatically and skips forks and the profile repo itself.
- Skill levels are based on repo language data, not self-rated.
- Live data uses the access GitHub gives the daily job by default. No paid tools or outside services are needed.
