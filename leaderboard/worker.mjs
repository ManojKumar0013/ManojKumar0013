import {validateLevel, verifyReplay} from "../game/engine.mjs";

const WINDOW = 60_000;
const BLOCKED = new Set(["ASS", "KKK", "FAG", "SEX", "FUQ"]);
const json = (body, status = 200, headers = {}) => Response.json(body, {status, headers});
const today = () => new Date().toISOString().slice(0, 10);

async function visitorKey(ip) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(today() + ":" + ip));
  return Array.from(new Uint8Array(bytes), v => v.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");
    const cors = {"Access-Control-Allow-Origin": env.GAME_ORIGIN, "Vary": "Origin"};
    if (origin && origin !== env.GAME_ORIGIN) return json({error: "Origin denied"}, 403);
    if (new URL(request.url).pathname !== "/scores") return json({error: "Not found"}, 404, cors);
    if (request.method === "OPTIONS") {
      return new Response(null, {status: 204, headers: {...cors, "Access-Control-Allow-Methods": "GET, POST",
        "Access-Control-Allow-Headers": "Content-Type"}});
    }
    const year = Number(new URL(request.url).searchParams.get("year"));
    if (!Number.isInteger(year) || year < 2008 || year > Number(today().slice(0, 4))) {
      return json({error: "Invalid year"}, 400, cors);
    }
    const headers = new Headers(request.headers);
    headers.delete("X-Visitor");
    if (request.method === "POST") {
      const ip = request.headers.get("CF-Connecting-IP");
      if (!ip) return json({error: "Missing visitor address"}, 400, cors);
      headers.set("X-Visitor", await visitorKey(ip));
    }
    let response;
    try {
      response = await env.SCORES.get(env.SCORES.idFromName(String(year))).fetch(new Request(request, {headers}));
    } catch {
      return json({error: "Leaderboard temporarily unavailable"}, 503, cors);
    }
    return new Response(response.body, {status: response.status, headers: {...Object.fromEntries(response.headers), ...cors}});
  },
};

export class ArcadeScores {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    this.db = ctx.storage.sql;
    this.db.exec("CREATE TABLE IF NOT EXISTS scores (run TEXT PRIMARY KEY, initials TEXT, score INTEGER, date TEXT)");
    this.db.exec("CREATE TABLE IF NOT EXISTS limits (visitor TEXT PRIMARY KEY, since INTEGER, attempts INTEGER)");
  }

  board() {
    return this.db.exec("SELECT initials, score, date FROM scores ORDER BY score DESC, date ASC, run ASC LIMIT 10").toArray();
  }

  rate(visitor, now) {
    this.db.exec("DELETE FROM limits WHERE since <= ?", now - WINDOW);
    const entry = this.db.exec("SELECT attempts FROM limits WHERE visitor = ?", visitor).toArray()[0];
    if (entry?.attempts >= 4) return false;
    this.db.exec(`INSERT INTO limits VALUES (?, ?, 1)
      ON CONFLICT(visitor) DO UPDATE SET attempts = attempts + 1`, visitor, now);
    return true;
  }

  async fetch(request) {
    if (request.method === "GET") return json({scores: this.board()});
    if (request.method !== "POST") return json({error: "Method not allowed"}, 405);
    const visitor = request.headers.get("X-Visitor");
    if (!visitor || !this.rate(visitor, Date.now())) return json({error: "Try again in a minute"}, 429);
    let data;
    try {
      const reader = request.body.getReader(), chunks = [];
      let size = 0;
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        if ((size += value.length) > 32_768) {
          await reader.cancel();
          return json({error: "Replay too large"}, 413);
        }
        chunks.push(value);
      }
      data = JSON.parse(await new Blob(chunks).text());
    } catch {
      return json({error: "Invalid replay"}, 400);
    }
    if (typeof data?.initials !== "string" || !/^[A-Z]{3}$/.test(data.initials) || BLOCKED.has(data.initials)) {
      return json({error: "Choose three allowed initials"}, 422);
    }
    const levelResponse = await fetch(this.env.LEVEL_URL, {cf: {cacheTtl: 30}});
    if (!levelResponse.ok) return json({error: "Level temporarily unavailable"}, 503);
    const level = validateLevel(await levelResponse.json());
    const year = Number(new URL(request.url).searchParams.get("year"));
    if (data.id !== level.id || year !== level.year) return json({error: "This level has refreshed"}, 409);
    let score;
    try {
      score = verifyReplay(level, data.changes, data.ticks);
    } catch {
      return json({error: "Replay failed verification"}, 422);
    }
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify([data.id, data.changes, data.ticks])));
    const hash = Array.from(new Uint8Array(digest), v => v.toString(16).padStart(2, "0")).join("");
    this.db.exec("INSERT OR IGNORE INTO scores VALUES (?, ?, ?, ?)", hash, data.initials, score, today());
    this.db.exec("DELETE FROM scores WHERE run NOT IN (SELECT run FROM scores ORDER BY score DESC, date ASC, run ASC LIMIT 10)");
    return json({scores: this.board()});
  }
}
