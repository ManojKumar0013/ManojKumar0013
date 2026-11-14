import {LEFT, RIGHT, JUMP, HZ, WIDTH, HEIGHT, validateLevel, start, step} from "./engine.mjs";

const el = id => document.getElementById(id);
const ctx = el("game").getContext("2d");
const root = document.documentElement;
const codes = {ArrowLeft: LEFT, KeyA: LEFT, ArrowRight: RIGHT, KeyD: RIGHT,
  Space: JUMP, ArrowUp: JUMP, KeyW: JUMP};
const keys = new Set(), pointers = new Map();
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
  colors = Object.fromEntries(["screen", "green", "soil", "coin", "bug", "fg", "dim"]
    .map(name => [name, css.getPropertyValue("--" + name).trim()]));
}

function draw() {
  const box = (x, y, w, h, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), w, h);
  };
  box(0, 0, WIDTH, HEIGHT, colors.screen);
  if (!run) return;
  const p = run.player, camera = Math.max(0, Math.min(run.end - WIDTH, p.x - 100));
  for (let i = 0; i < 7; i++) {
    box(i * 65 - camera * .18 % 65, 112 - i % 3 * 8, 51, 26 + i % 3 * 8, colors.soil + "35");
  }
  for (const tile of run.solids) {
    if (tile.x + tile.w < camera || tile.x > camera + WIDTH) continue;
    box(tile.x - camera, tile.y, tile.w, tile.y < 148 ? 8 : 32, colors.soil);
    box(tile.x - camera, tile.y, tile.w, 2, colors.green);
    for (let x = 4; x < tile.w - 3; x += 12) box(tile.x - camera + x, tile.y + 5, 4, 2, colors.screen);
  }
  for (const coin of run.coins) if (!coin.used && Math.abs(coin.x - camera - WIDTH / 2) < WIDTH / 2 + 10) {
    box(coin.x - camera + 1, coin.y, 6, 8, colors.coin);
    box(coin.x - camera, coin.y + 2, 8, 4, colors.coin);
    box(coin.x - camera + 3, coin.y + 2, 2, 4, colors.screen);
  }
  for (const item of run.powers) if (!item.used) {
    box(item.x - camera, item.y, 10, 10, colors.bug);
    box(item.x - camera + 4, item.y + 2, 2, 6, colors.screen);
    box(item.x - camera + 2, item.y + 4, 6, 2, colors.screen);
  }
  for (const bug of run.bugs) if (!bug.used) {
    box(bug.x - camera, bug.y + 3, 12, 6, colors.bug);
    box(bug.x - camera + 2, bug.y, 8, 6, colors.bug);
    box(bug.x - camera + 4, bug.y + 3, 2, 2, colors.screen);
    box(bug.x - camera + 8, bug.y + 3, 2, 2, colors.screen);
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
  el("score").textContent = "Score " + run.score;
  el("lives").textContent = "Lives " + run.lives;
}

function showOverlay(title, summary, button) {
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
  if (paused) showOverlay("Paused", "Your run is frozen.", "Resume");
  else {
    el("overlay").hidden = true;
    if (document.activeElement === el("start")) el("game").focus({preventScroll: true});
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
  el("boardLabel").textContent = shared ? "shared this year" : "on this device";
  el("scores").replaceChildren();
  const scores = shared ?? local;
  for (const entry of scores.slice(0, run?.result ? 10 : 5)) {
    const li = document.createElement("li"), when = document.createElement("span");
    li.textContent = `${entry.initials} · ${entry.score.toLocaleString()} `;
    when.textContent = entry.date;
    li.append(when);
    el("scores").append(li);
  }
  el("boardStatus").textContent = scores.length ? "" : "The board is open for your first run.";
}

function finish() {
  playSound(run.result === "level clear" ? "clear" : "hit");
  showOverlay(run.result, `${run.score} points · ${run.coinCount} coins · ${run.bugCount} bugs · ${(run.tick / HZ).toFixed(1)} s`, "Play again");
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
  el("sound").textContent = sound ? "Sound on" : "Sound off";
  el("sound").setAttribute("aria-pressed", String(sound));
};
el("theme").onclick = () => {
  const next = {system: "dark", dark: "light", light: "system"}[root.dataset.theme || "system"];
  root.dataset.theme = next;
  el("theme").textContent = "Theme: " + next;
  updateColors();
  draw();
};
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { updateColors(); draw(); });

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
  if (!e.repeat && e.code === "KeyP") pause();
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
for (const button of document.querySelectorAll("[data-mask]")) {
  button.addEventListener("pointerdown", e => {
    e.preventDefault();
    button.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, Number(button.dataset.mask));
  });
  for (const event of ["pointerup", "pointercancel", "lostpointercapture"]) {
    button.addEventListener(event, e => pointers.delete(e.pointerId));
  }
}
window.addEventListener("blur", () => pause(true));
document.addEventListener("visibilitychange", () => { if (document.hidden) pause(true); });
new ResizeObserver(([entry]) => {
  const width = entry.contentRect.width;
  root.style.setProperty("--canvas-width", Math.min(width, Math.max(1, Math.floor(width / WIDTH)) * WIDTH) + "px");
}).observe(document.querySelector(".screen"));

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
      showOverlay("Level unavailable", "Reconnect and reload to download the contribution calendar.", "Reload to try again");
      el("start").disabled = false;
      el("start").onclick = () => location.reload();
      return;
    }
  }
  settings = level.game ?? {};
  el("profile").href = "https://github.com/" + encodeURIComponent(level.login);
  el("logo").textContent = level.logo;
  el("world").textContent = "World " + level.year;
  local = load(boardKey()) ?? [];
  if (!Array.isArray(local)) local = [];
  displayBoard();
  showOverlay("Press start", "Run through the GitHub year. Grab coins, dodge bugs, reach the flag.", "Start game");
  el("start").disabled = false;
  if (settings.leaderboard) {
    try { shared = await requestBoard(); displayBoard(); }
    catch { el("boardStatus").textContent = "Shared scores are unavailable. This device keeps its own board."; }
  }
}

updateColors();
draw();
requestAnimationFrame(frame);
boot();

navigator.serviceWorker?.register("./sw.js").catch(() => {
  // The current tab still works and can use its last downloaded calendar.
});
