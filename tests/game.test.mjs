import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {DatabaseSync} from "node:sqlite";
import {LEFT, RIGHT, JUMP, FLOOR, start, step, validateLevel, verifyReplay} from "../game/engine.mjs";
import worker, {ArcadeScores} from "../leaderboard/worker.mjs";

const level = {id: "a".repeat(16), year: 2026, version: 1, weeks: [[0, 4, 0, 0, 0, 0, 0]]};
function walkthrough() {
  const play = start(level), changes = [];
  let previous = 0;
  while (!play.result) {
    const x = play.player.x;
    const input = RIGHT | (x > 263 && x < 380 ? JUMP : 0);
    if (previous !== input) changes.push([play.tick, input]);
    previous = input;
    step(play, input);
  }
  return {play, changes};
}

test("real snapshot produces its weeks, day coins, six powers and finish flag", () => {
  const actual = JSON.parse(readFileSync(new URL("../game/level.json", import.meta.url)));
  const game = start(actual);
  assert.equal(game.coins.length, actual.weeks.flat().filter(Boolean).length);
  assert.equal(game.powers.length, 6);
  assert.equal(game.lives, 3);
  assert.ok(game.flag > 0);
  assert.throws(() => validateLevel({...actual, weeks: [[-1]]}));
});

test("platform traversal, perfect week and deterministic score verification", () => {
  const {play, changes} = walkthrough();
  assert.equal(play.result, "level clear");
  assert.equal(play.coinCount, 1);
  assert.ok(play.score >= 250);
  assert.equal(verifyReplay(level, changes, play.tick), play.score);
  assert.throws(() => verifyReplay(level, [[0, 9]], play.tick));
  assert.throws(() => verifyReplay(level, changes, play.tick - 1));
});

test("jumps, landing, and three falls", () => {
  const game = start(level);
  step(game, LEFT | JUMP);
  assert.ok(game.player.y < FLOOR - game.player.h);
  for (let i = 0; i < 3; i++) {
    game.player.y = 300;
    step(game, 0);
  }
  assert.equal(game.result, "game over");
  assert.equal(game.lives, 0);
});

test("worker verifies scores, deduplicates and rate limits", async () => {
  const sqlite = new DatabaseSync(":memory:");
  const ctx = {storage: {sql: {exec(query, ...parameters) {
    const statement = sqlite.prepare(query);
    if (query.trim().startsWith("SELECT")) return {toArray: () => statement.all(...parameters)};
    statement.run(...parameters);
  }}}};
  const service = new ArcadeScores(ctx, {LEVEL_URL: "https://example.com/level.json"});
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => Response.json(level);
  try {
    const {play, changes} = walkthrough();
    const post = (data, visitor = "visitor") => service.fetch(new Request("https://worker.test/scores?year=2026",
      {method: "POST", headers: {"X-Visitor": visitor}, body: JSON.stringify(data)}));
    const valid = {initials: "MKB", id: level.id, changes, ticks: play.tick, score: 999999999};
    const accepted = await post(valid);
    assert.equal(accepted.status, 200);
    assert.equal((await accepted.json()).scores[0].score, play.score);
    assert.equal((await (await post(valid)).json()).scores.length, 1);
    assert.equal((await post({...valid, id: "invalid"})).status, 409);
    assert.equal((await post({...valid, initials: "KKK"})).status, 422);
    assert.equal((await post(valid)).status, 429);
    assert.equal((await post({...valid, ticks: 2}, "other")).status, 422);
    const rejectedOrigin = await worker.fetch(new Request("https://worker.test/scores?year=2026",
      {headers: {Origin: "https://elsewhere.test"}}), {GAME_ORIGIN: "https://game.test"});
    assert.equal(rejectedOrigin.status, 403);
  } finally {
    globalThis.fetch = originalFetch;
    sqlite.close();
  }
});
