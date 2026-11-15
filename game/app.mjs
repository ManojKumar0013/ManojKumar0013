import {LEFT, RIGHT, JUMP, HZ, LIMIT, WIDTH, HEIGHT, validateLevel, start, step} from "./engine.mjs";
import {scenery} from "./scenery.mjs";

const el = id => document.getElementById(id);
const ctx = el("game").getContext("2d");
const root = document.documentElement;
const codes = {ArrowLeft: LEFT, KeyA: LEFT, ArrowRight: RIGHT, KeyD: RIGHT,
  Space: JUMP, ArrowUp: JUMP, KeyW: JUMP};
const keys = new Set(), pointers = new Map();
const controls = [...document.querySelectorAll("[data-mask]")];
const scheme = matchMedia("(prefers-color-scheme: dark)");
const secret = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight",
  "ArrowLeft", "ArrowRight", "KeyB", "KeyA"];
let level, settings, run, audio, paused = false, sound = false, rainbow = false, sequence = 0;
let timer = 0, last = 0, mask = 0, replay = [], pending, local = [], shared = null, colors;
const timeout = () => AbortSignal.timeout(5000);
const date = () => new Date().toISOString().slice(0, 10);
const load = key => {
  try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
};
const store = (key, value) => {
  try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
};
const boardKey = () => `arcade:${level.login}:${level.year}`;

function playSound(type) {
  if (!sound || !audio || audio.state !== "running") return;
  const frequency = {jump: 330, coin: 780, stomp: 150, hit: 110, clear: 660}[type] ?? 510;
  const osc = audio.createOscillator(), gain = audio.createGain(), now = audio.currentTime;
  osc.type = "square";
  osc.frequency.setValueAtTime(frequency, now);
  osc.frequency.exponentialRampToValueAtTime(frequency * (type === "hit" ? .55 : 1.4), now + .11);
  gain.gain.setValueAtTime(.033, now);
  gain.gain.exponentialRampToValueAtTime(.001, now + .13);
  osc.connect(gain).connect(audio.destination);
  osc.start();
  osc.stop(now + .14);
}

function updateColors() {
  const css = getComputedStyle(root);
  const names = {
    soil: "soil", green: "green", coin: "coin", bug: "bug", fg: "fg", dim: "dim",
    skyTop: "sky-top", skyHorizon: "sky-horizon", far: "far", ridge: "ridge", pine: "pine", moon: "moon",
  };
  colors = Object.fromEntries(Object.entries(names).map(([key, name]) =>
    [key, css.getPropertyValue("--" + name).trim()]));
}

function draw() {
  const box = (x, y, w, h, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), w, h);
  };
  const p = run?.player;
  const camera = p ? Math.max(0, Math.min(run.end - WIDTH, p.x - 100)) : 0;
  scenery(ctx, WIDTH, HEIGHT, camera, colors);
  if (!p) return;
  for (const tile of run.solids) {
    if (tile.x + tile.w < camera || tile.x > camera + WIDTH) continue;
    box(tile.x - camera, tile.y, tile.w, tile.y < 148 ? 7 : 32, colors.soil);
    box(tile.x - camera, tile.y, tile.w, 2, colors.green);
    for (let x = 4; x < tile.w - 3; x += 12) {
      box(tile.x - camera + x, tile.y + 4, 3, 2, colors.pine);
      if (tile.y === 148) box(tile.x - camera + x + 3, tile.y + 14 + x % 9, 7, 2, colors.ridge);
    }
  }
  for (const coin of run.coins) if (!coin.used && Math.abs(coin.x - camera - WIDTH / 2) < WIDTH / 2 + 10) {
    box(coin.x - camera + 1, coin.y, 6, 8, colors.coin);
    box(coin.x - camera, coin.y + 2, 8, 4, colors.coin);
    box(coin.x - camera + 3, coin.y + 2, 2, 4, "#a36832");
  }
  for (const item of run.powers) if (!item.used) {
    box(item.x - camera, item.y, 10, 10, colors.bug);
    box(item.x - camera + 4, item.y + 2, 2, 6, colors.soil);
    box(item.x - camera + 2, item.y + 4, 6, 2, colors.soil);
  }
  for (const bug of run.bugs) if (!bug.used) {
    box(bug.x - camera, bug.y + 3, 12, 6, colors.bug);
    box(bug.x - camera + 2, bug.y, 8, 6, colors.bug);
    box(bug.x - camera + 4, bug.y + 3, 2, 2, colors.soil);
    box(bug.x - camera + 8, bug.y + 3, 2, 2, colors.soil);
  }
  box(run.flag - camera, 109, 2, 39, colors.fg);
  box(run.flag - camera + 2, 109, 15, 8, colors.bug);
  const x = p.x - camera, y = p.y;
  if (p.shield) box(x - 2, y - 2, 14, 18, colors.green);
  box(x + 2, y, 7, 3, rainbow ? "#ac82ff" : colors.bug);
  box(x + 3, y + 3, 6, 4, "#edb899");
  box(x + 1, y + 7, 8, 4, colors.coin);
  box(x + (p.vx && run.tick % 12 < 6 ? 1 : 3), y + 11, 7, 3, colors.fg);
}

function updateHud() {
  const seconds = Math.max(0, Math.ceil((LIMIT - run.tick) / HZ));
  el("clock").textContent = Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");
  el("score").textContent = run.score.toLocaleString();
  el("lives").textContent = "♥ ".repeat(run.lives) + "♡ ".repeat(Math.max(0, 3 - run.lives));
  el("lives").setAttribute("aria-label", run.lives + (run.lives === 1 ? " life" : " lives"));
  el("progress").value = Math.min(100, Math.max(0, (run.player.x + run.player.w) / run.flag * 100));
}

function setControls(active) {
  for (const button of controls) {
    button.disabled = !active;
    button.removeAttribute("data-held");
  }
}

function showOverlay(state, title, summary, button) {
  el("overlay").dataset.state = state;
  el("headline").textContent = title;
  el("summary").textContent = summary;
  el("start").textContent = button;
  el("overlay").hidden = false;
}

function launch() {
  if (!level) return;
  if (paused) {
    pause(false);
    return;
  }
  if (run && !run.result) return;
  run = start(level);
  if (document.activeElement === el("start")) el("game").focus({preventScroll: true});
  paused = false;
  timer = 0;
  replay = [];
  mask = 0;
  pending = null;
  el("save").hidden = true;
  el("overlay").hidden = true;
  el("pause").disabled = false;
  el("pause").textContent = "Pause";
  setControls(true);
  el("notice").textContent = "The current week’s flag is the finish.";
  updateHud();
  draw();
}

function pause(value = !paused) {
  if (!run || run.result) return;
  paused = value;
  timer = 0;
  keys.clear();
  pointers.clear();
  el("pause").textContent = paused ? "Resume" : "Pause";
  setControls(!paused);
  if (paused) showOverlay("paused", "Run paused", "Pick up where you left off.", "Resume run");
  else {
    el("overlay").hidden = true;
    el("game").focus({preventScroll: true});
  }
}

function requestBoard(params = {}) {
  const endpoint = new URL(settings.leaderboard);
  endpoint.searchParams.set("year", String(level.year));
  return fetch(endpoint, {...params, signal: timeout()}).then(async response => {
    if (!response.ok) throw new Error("Shared scores are temporarily unavailable");
    const payload = await response.json();
    if (!Array.isArray(payload.scores)) throw new Error("Invalid leaderboard response");
    return payload.scores;
  });
}

const sorted = scores => scores.sort((a, b) => b.score - a.score || a.date.localeCompare(b.date)).slice(0, 10);
const qualifies = (scores, score) => scores.length < 10 || score > scores.at(-1).score;
function displayBoard() {
  el("boardLabel").textContent = shared ? "Shared this year" : "On this device";
  el("scores").replaceChildren();
  const scores = shared ?? local;
  scores.slice(0, 10).forEach((entry, index) => {
    const li = document.createElement("li");
    const rank = document.createElement("span");
    const initials = document.createElement("strong");
    const score = document.createElement("strong");
    const when = document.createElement("time");
    rank.textContent = String(index + 1).padStart(2, "0");
    initials.textContent = entry.initials;
    score.textContent = entry.score.toLocaleString();
    when.textContent = entry.date;
    li.append(rank, initials, score, when);
    el("scores").append(li);
  });
  el("boardStatus").textContent = scores.length ? "" : "The board is open for your first run.";
}

function finish() {
  playSound(run.result === "level clear" ? "clear" : "hit");
  setControls(false);
  el("pause").disabled = true;
  const title = {"level clear": "Course complete", "time up": "Time’s up", "game over": "Run ended"}[run.result];
  showOverlay("result", title, `${run.score} points · ${run.coinCount} coins · ${run.bugCount} bugs · ${(run.tick / HZ).toFixed(1)} s`, "Play again");
  pending = {id: level.id, ticks: run.tick, changes: replay};
  displayBoard();
  el("save").hidden = !(run.score && (qualifies(local, run.score) || shared && qualifies(shared, run.score)));
}

function frame(now) {
  if (run && !run.result && !paused) {
    timer += Math.min(now - last, 100);
    while (timer >= 1000 / HZ && !run.result) {
      const input = [...keys, ...pointers.values()].reduce((out, val) => out | val, 0);
      if (input !== mask) {
        mask = input;
        replay.push([run.tick, mask]);
      }
      step(run, mask);
      for (const event of run.events) {
        if (event === "perfect week") el("notice").textContent = "PERFECT WEEK · bonus points";
        else if (/^[A-Z]/.test(event)) el("notice").textContent = event + " skill unlocked";
        if (event !== "perfect week") playSound(event);
      }
      timer -= 1000 / HZ;
    }
    updateHud();
    draw();
    if (run.result) finish();
  }
  last = now;
  requestAnimationFrame(frame);
}

el("start").onclick = launch;
el("pause").onclick = () => pause();
el("sound").onclick = async () => {
  try {
    sound = !sound;
    if (sound) {
      audio ??= new (window.AudioContext || window.webkitAudioContext)();
      await audio.resume();
      playSound("coin");
    }
  } catch { sound = false; }
  el("sound-label").textContent = sound ? "Sound on" : "Sound off";
  el("sound").setAttribute("aria-pressed", String(sound));
};
let theme = load("arcade:theme") || "system";
if (!["system", "dark", "light"].includes(theme)) theme = "system";
function applyTheme() {
  root.dataset.theme = theme === "system" ? (scheme.matches ? "dark" : "light") : theme;
  el("theme-label").textContent = "Theme: " + theme;
  updateColors();
  draw();
}
el("theme").onclick = () => {
  theme = {system: "dark", dark: "light", light: "system"}[theme];
  store("arcade:theme", theme);
  applyTheme();
};
scheme.addEventListener("change", applyTheme);

document.addEventListener("keydown", e => {
  if (e.altKey || e.ctrlKey || e.metaKey || e.target.matches("input,textarea,select")) return;
  if (!e.repeat && (!run || run.result)) {
    sequence = e.code === secret[sequence] ? sequence + 1 : Number(e.code === secret[0]);
    if (sequence === secret.length) {
      sequence = 0;
      rainbow = !rainbow;
      el("notice").textContent = rainbow ? "Hidden runner palette unlocked" : "Original runner palette restored";
    }
  }
  if (!e.repeat && ["KeyP", "Escape"].includes(e.code)) pause();
  if (!e.repeat && e.code === "KeyM") el("sound").click();
  if (!e.repeat && ["Space", "Enter"].includes(e.code) && (!run || run.result || paused) &&
      !e.target.matches("button,a")) {
    e.preventDefault();
    launch();
  }
  if (codes[e.code] && run && !run.result && !paused &&
      !(e.code === "Space" && e.target.matches("button,a"))) {
    e.preventDefault();
    keys.add(codes[e.code]);
  }
});
document.addEventListener("keyup", e => keys.delete(codes[e.code]));
for (const button of controls) {
  button.addEventListener("pointerdown", e => {
    e.preventDefault();
    if (button.disabled) return;
    button.setPointerCapture(e.pointerId);
    button.dataset.held = "";
    pointers.set(e.pointerId, Number(button.dataset.mask));
  });
  for (const event of ["pointerup", "pointercancel", "lostpointercapture"]) {
    button.addEventListener(event, e => {
      pointers.delete(e.pointerId);
      if (![...pointers.values()].includes(Number(button.dataset.mask))) button.removeAttribute("data-held");
    });
  }
}
window.addEventListener("blur", () => pause(true));
document.addEventListener("visibilitychange", () => { if (document.hidden) pause(true); });

el("save").addEventListener("submit", async e => {
  e.preventDefault();
  if (!pending) return;
  const initials = el("initials").value.trim().toUpperCase();
  if (!/^[A-Z]{3}$/.test(initials)) return;
  const body = {...pending, initials};
  const score = run.score;
  pending = null;
  el("save").hidden = true;
  local = sorted([...local, {initials, score, date: date()}]);
  const saved = store(boardKey(), local);
  if (settings.leaderboard && navigator.onLine) {
    try {
      shared = await requestBoard({method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
      displayBoard();
      el("boardStatus").textContent = "Run checked by the shared leaderboard.";
      return;
    } catch { shared = null; }
  }
  displayBoard();
  el("boardStatus").textContent = saved ? "Score saved on this device." : "Score kept for this session.";
});

async function boot() {
  try {
    const response = await fetch("./level.json", {signal: timeout()});
    if (!response.ok) throw new Error("Level unavailable");
    level = validateLevel(await response.json());
    store("arcade:last-level", level);
  } catch {
    try { level = validateLevel(load("arcade:last-level")); }
    catch {
      showOverlay("error", "Level unavailable", "Reconnect and reload to download the contribution calendar.", "Reload to try again");
      el("start").disabled = false;
      el("start").onclick = () => location.reload();
      return;
    }
  }
  settings = level.game ?? {};
  el("profile").href = "https://github.com/" + encodeURIComponent(level.login);
  el("logo").textContent = level.logo;
  el("world").textContent = String(level.year);
  local = load(boardKey()) ?? [];
  if (!Array.isArray(local)) local = [];
  displayBoard();
  showOverlay("ready", "Ready to run?", "Grab coins, dodge bugs, and reach the finish flag.", "Start run");
  el("start").disabled = false;
  if (settings.leaderboard) {
    try { shared = await requestBoard(); displayBoard(); }
    catch { el("boardStatus").textContent = "Shared scores are unavailable. This device keeps its own board."; }
  }
}

applyTheme();
requestAnimationFrame(frame);
boot();

navigator.serviceWorker?.register("./sw.js").catch(() => {
  // The current tab still works and can use its last downloaded calendar.
});
