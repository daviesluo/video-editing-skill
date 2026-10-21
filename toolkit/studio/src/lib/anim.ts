import { Easing, interpolate } from "remotion";
import { EASE } from "../brand/tokens";

// Everything is a pure function of the frame: no CSS transitions or
// keyframes, no Math.random (use Remotion's random(seed)), no tweens on
// wall-clock time. A render is then the same on every machine.

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const enter = Easing.bezier(...EASE.enter);
export const move = Easing.bezier(...EASE.move);
export const exit = Easing.bezier(...EASE.exit);
export const fade = Easing.bezier(...EASE.fade);

// How far ahead of its word a drawn reveal starts: it must already read
// when the word begins. The eye forgives a picture slightly early, never
// late, and an ease-in from the word itself lands a third of a second late.
export const LINE_LEAD = 0.2;

// 0 -> 1 over [start, start + dur] seconds, eased.
export const ramp = (frame: number, fps: number, start: number, dur: number, easing = enter): number =>
  dur <= 0 ? (frame >= start * fps ? 1 : 0) : interpolate(frame, [start * fps, (start + dur) * fps], [0, 1], { ...clamp, easing });

// Visible window: 0 before, 1 inside, 0 after, eased in and out, so a fade
// never ends in a jump.
export const windowed = (frame: number, fps: number, start: number, end: number, fadeIn = 0.35, fadeOut = 0.3): number =>
  Math.min(ramp(frame, fps, start, fadeIn, enter), 1 - ramp(frame, fps, end - fadeOut, fadeOut, fade));

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
