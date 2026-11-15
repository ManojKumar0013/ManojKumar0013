// Draw the landscape separately from the deterministic collision simulation.
const ridge = (ctx, width, height, camera, color, points, speed) => {
  const offset = Math.floor(camera * speed) % width;
  ctx.fillStyle = color;
  for (let tile = -offset; tile < width; tile += width) {
    ctx.beginPath();
    ctx.moveTo(tile, height);
    for (const [x, y] of points) ctx.lineTo(tile + x, y);
    ctx.lineTo(tile + width, height);
    ctx.closePath();
    ctx.fill();
  }
};

export function scenery(ctx, width, height, camera, c) {
  const sky = ctx.createLinearGradient(0, 0, 0, 128);
  sky.addColorStop(0, c.skyTop);
  sky.addColorStop(1, c.skyHorizon);
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = c.moon;
  ctx.beginPath();
  ctx.arc(244 - Math.floor(camera * .012) % 145, 48, 26, 0, 2 * Math.PI);
  ctx.fill();
  ctx.globalAlpha = .27;
  for (let i = 0; i < 18; i++) {
    ctx.fillRect((i * 47 + 13) % width, 15 + i * 17 % 58, i % 4 ? 1 : 2, 1);
  }
  ctx.globalAlpha = 1;
  ridge(ctx, width, height, camera, c.far,
    [[0, 109], [31, 86], [47, 91], [84, 55], [113, 82], [126, 74], [158, 105],
      [188, 85], [214, 61], [253, 94], [278, 80], [320, 109]], .16);
  ridge(ctx, width, height, camera, c.ridge,
    [[0, 129], [27, 120], [65, 96], [99, 118], [126, 126], [157, 113],
      [187, 99], [218, 123], [256, 113], [280, 107], [320, 129]], .32);
  ctx.fillStyle = c.pine;
  ctx.fillRect(0, 139, width, height - 139);
  const offset = Math.floor(camera * .49) % width;
  for (let i = -1; i < 24; i++) {
    const x = ((i * 23 + 19 - offset) % width + width) % width;
    const h = 7 + ((i + 1) * 11) % 21;
    for (let tier = 0; tier < 3; tier++) {
      const y = 140 - h + tier * Math.ceil(h / 5);
      ctx.fillRect(x - tier, y, 2 + tier * 2, Math.ceil(h / 3));
    }
    ctx.fillRect(x, 140 - Math.ceil(h / 2), 2, Math.ceil(h / 2));
  }
}
