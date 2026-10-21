import { EM } from "./archivo800.ts";

// Where a bar's number sits, kept free of React so the selftest can check
// it: centred on the bar, beside its end when there is room, inside the bar
// in the mark colour when there is not. The number is sized to the bar, so
// it never rides over the bar's edge.

// The row's name above the bar: 36 px type at line height 1.1, then a 12 px gap.
export const LABEL_LINE = 36 * 1.1 + 12;
const PAD = 16;

export type NumberBox = { top: number; left: number; width: number; height: number; size: number; inside: boolean };

export const numberWidth = (text: string, size: number) => [...text].reduce((w, c) => w + (EM[c] ?? 0.6), 0) * size;

export const barNumber = (text: string, len: number, width: number, thickness: number): NumberBox => {
  const size = Math.min(52, Math.round(thickness * 0.8));
  const w = numberWidth(text, size);
  const height = size * 1.1;
  const inside = len + PAD + w > width;
  return {
    top: LABEL_LINE + thickness / 2 - height / 2,
    left: inside ? len - PAD - w : len + PAD,
    width: w,
    height,
    size,
    inside,
  };
};
