// Deterministic 60 Hz simulation shared by the browser and score verifier.
export const LEFT = 1, RIGHT = 2, JUMP = 4;
export const HZ = 60, LIMIT = 180 * HZ;
export const WIDTH = 320, HEIGHT = 180, FLOOR = 148, WEEK = 240;
const POWERS = ["Python", "Java", "C", "JavaScript", "React", "Kotlin"];
const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

export function validateLevel(level) {
  if (level?.version !== 1 || !Number.isInteger(level.year) || level.year < 2008 ||
      !/^[a-f0-9]{16}$/.test(level.id) || !Array.isArray(level.weeks) ||
      level.weeks.length < 1 || level.weeks.length > 54 ||
      level.weeks.some(week => !Array.isArray(week) || week.length !== 7 ||
        week.some(count => !Number.isSafeInteger(count) || count < 0))) {
    throw new Error("Invalid contribution level");
  }
  return level;
}

export function start(level) {
  validateLevel(level);
  const peak = Math.max(1, ...level.weeks.map(days => days.reduce((a, b) => a + b, 0)));
  // Use the runway before the first week to space pickups safely even in January.
  const offset = 264, solids = [{x: 0, w: offset, y: FLOOR}], coins = [], bugs = [];
  const weeks = level.weeks.map((days, i) => {
    const x = offset + i * WEEK;
    const sum = days.reduce((a, b) => a + b, 0);
    const rise = sum ? 8 * Math.ceil(5 * Math.sqrt(sum / peak)) : 0;
    const gap = !sum && i % 4 === 2 && i < level.weeks.length - 1;
    if (gap) {
      solids.push({x, w: 108, y: FLOOR}, {x: x + 142, w: 98, y: FLOOR});
    } else {
      solids.push({x, w: WEEK, y: FLOOR});
    }
    if (rise) {
      solids.push({x: x + 57, w: 126, y: FLOOR - rise});
      days.forEach((count, day) => {
        if (count) coins.push({x: x + 62 + day * 18, y: FLOOR - rise - 22, w: 8, h: 8, week: i});
      });
    } else {
      bugs.push({x: x + 35, low: x + 23, high: x + 86, y: FLOOR - 10, w: 12, h: 10, dir: 1});
    }
    return {x, goal: days.filter(Boolean).length, collected: 0};
  });
  const end = offset + level.weeks.length * WEEK;
  const powers = POWERS.map((name, i) => {
    const x = 45 + Math.floor(i * (end - 100) / POWERS.length);
    const y = Math.min(...solids.filter(tile => x + 10 > tile.x && x < tile.x + tile.w).map(tile => tile.y), FLOOR);
    // Move a pickup off a gap to the closest solid surface.
    const safe = solids.some(tile => x >= tile.x && x + 10 <= tile.x + tile.w);
    const tile = solids.find(tile => tile.x > x);
    return {name, x: safe || !tile ? x : tile.x + 6, y: (safe || !tile ? y : tile.y) - 14, w: 10, h: 10};
  });
  return {level, solids, weeks, coins, bugs, powers, end, flag: end - 22, tick: 0,
    score: 0, lives: 3, coinCount: 0, bugCount: 0, result: null, previous: 0, events: [],
    checkpoint: {x: 12, y: FLOOR}, nextCheckpoint: 0,
    player: {x: 12, y: FLOOR - 14, w: 10, h: 14, vx: 0, vy: 0, grounded: true,
      extra: 0, double: false, shield: false, speed: 0, magnet: 0, multiplier: 0, safe: 0}};
}

function award(game, points) {
  game.score += points * (game.player.multiplier > game.tick ? 2 : 1);
}

function hit(game, fall) {
  const p = game.player;
  if (!fall && p.safe > game.tick) return;
  if (!fall && p.shield) {
    p.shield = false;
  } else {
    game.lives--;
  }
  p.safe = game.tick + 75;
  game.events.push("hit");
  if (!game.lives) game.result = "game over";
  Object.assign(p, {x: game.checkpoint.x, y: game.checkpoint.y - p.h, vx: 0, vy: 0, grounded: true});
}

function pickup(game, item) {
  const p = game.player;
  switch (item.name) {
    case "Python": p.double = true; p.extra = Math.max(p.extra, 1); break;
    case "Java": p.shield = true; break;
    case "C": p.speed = game.tick + 480; break;
    case "JavaScript": p.magnet = game.tick + 540; break;
    case "React": p.extra += 1; break;
    case "Kotlin": p.multiplier = game.tick + 600; break;
  }
  item.used = true;
  game.events.push(item.name);
}

export function step(game, input) {
  if (game.result) return;
  game.events.length = 0;
  game.tick++;
  const p = game.player;
  const direction = Number(Boolean(input & RIGHT)) - Number(Boolean(input & LEFT));
  p.vx = direction * (p.speed > game.tick ? 2.9 : 1.85);
  if ((input & JUMP) && !(game.previous & JUMP) && (p.grounded || p.extra)) {
    if (!p.grounded) p.extra--;
    p.vy = -5.8;
    p.grounded = false;
    game.events.push("jump");
  }
  game.previous = input;
  const previousBottom = p.y + p.h;
  p.x = Math.min(game.end - p.w, Math.max(0, p.x + p.vx));
  p.vy = Math.min(8, p.vy + (input & JUMP && p.vy < 0 ? .25 : .44));
  p.y += p.vy;
  const landing = game.solids.find(tile => p.vy >= 0 && previousBottom <= tile.y &&
    p.y + p.h >= tile.y && p.x + p.w > tile.x && p.x < tile.x + tile.w &&
    !game.solids.some(other => other.y < tile.y && previousBottom <= other.y && p.y + p.h >= other.y &&
      p.x + p.w > other.x && p.x < other.x + other.w));
  p.grounded = Boolean(landing);
  if (landing) {
    p.y = landing.y - p.h;
    p.vy = 0;
    p.extra = Number(p.double) + Number(game.powers.some(item => item.name === "React" && item.used));
  }
  if (p.y > HEIGHT + 20) hit(game, true);
  for (const bug of game.bugs) {
    if (bug.used) continue;
    bug.x += bug.dir * .55;
    if (bug.x <= bug.low || bug.x >= bug.high) bug.dir *= -1;
    if (!overlap(p, bug)) continue;
    if (previousBottom <= bug.y + 3 && p.vy > 0) {
      p.vy = -3.2;
      bug.used = true;
      game.bugCount++;
      award(game, 50);
      game.events.push("stomp");
    } else {
      hit(game, false);
    }
  }
  if (game.result) return;
  for (const item of game.powers) if (!item.used && overlap(p, item)) pickup(game, item);
  for (const coin of game.coins) {
    if (coin.used || !(overlap(p, coin) ||
      p.magnet > game.tick && Math.abs(p.x - coin.x) < 42 && Math.abs(p.y - coin.y) < 35)) continue;
    coin.used = true;
    game.coinCount++;
    award(game, 100);
    game.events.push("coin");
    const week = game.weeks[coin.week];
    if (++week.collected === week.goal) {
      award(game, 150);
      game.events.push("perfect week");
    }
  }
  if (landing?.y === FLOOR && p.x >= game.nextCheckpoint && p.x + 28 < landing.x + landing.w) {
    game.checkpoint = {x: p.x, y: FLOOR};
    game.nextCheckpoint = landing.x + landing.w;
  }
  if (p.x + p.w >= game.flag && p.y < FLOOR) {
    award(game, Math.max(0, 900 - Math.floor(game.tick / 12)));
    game.result = "level clear";
  } else if (game.tick >= LIMIT) {
    game.result = "time up";
  }
}

export function verifyReplay(level, changes, ticks) {
  if (!Number.isInteger(ticks) || ticks < 1 || ticks > LIMIT ||
      !Array.isArray(changes) || changes.length > 1800) throw new Error("Invalid replay length");
  let last = -1;
  for (const change of changes) {
    if (!Array.isArray(change) || change.length !== 2) throw new Error("Invalid input");
    const [time, mask] = change;
    if (!Number.isInteger(time) || time <= last || time >= ticks ||
        !Number.isInteger(mask) || mask < 0 || mask > 7) throw new Error("Invalid input");
    last = time;
  }
  const run = start(level);
  let i = 0, input = 0;
  while (run.tick < ticks && !run.result) {
    if (changes[i]?.[0] === run.tick) input = changes[i++][1];
    step(run, input);
  }
  if (!run.result || run.tick !== ticks || !run.score) throw new Error("Replay did not finish with a score");
  return run.score;
}
