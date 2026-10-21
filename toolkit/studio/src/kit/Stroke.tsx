import { COLORS } from "../brand/tokens";

// A line with its casing: a light under-stroke, as printed maps case their
// roads. Red or blue on a mid-blue sea or a busy photograph is under 3:1 in
// luminance, and the casing keeps the line clear of any ground. No glow.
export const Stroke: React.FC<{ d: string; color: string; width: number; opacity?: number; dash?: string }> = ({
  d,
  color,
  width,
  opacity = 1,
  dash,
}) =>
  opacity > 0.001 ? (
    <g opacity={opacity}>
      <path d={d} fill="none" stroke={COLORS.mark} strokeOpacity={0.85} strokeWidth={width + 6} strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} />
    </g>
  ) : null;
