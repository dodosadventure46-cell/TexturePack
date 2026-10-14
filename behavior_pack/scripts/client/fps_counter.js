import { world, system } from '@minecraft/server';

const updateRate = 10; // ticks; ~0.5s
let frameCounter = 0;
let lastTime = Date.now();
let lastFps = 0;

system.runInterval(() => {
  frameCounter += 1;
  const now = Date.now();
  const deltaSec = (now - lastTime) / 1000;

  if (deltaSec > 0) {
    lastFps = Math.min(999, Math.max(0, Math.round(frameCounter / deltaSec)));
    frameCounter = 0;
    lastTime = now;
  }

  for (const player of world.getPlayers()) {
    player.runCommand(`title @s actionbar FPS: ${lastFps}`);
  }
}, updateRate);
