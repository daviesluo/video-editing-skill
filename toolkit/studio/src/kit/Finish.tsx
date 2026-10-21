import { AbsoluteFill, useCurrentFrame } from "remotion";
import { THEME } from "../brand/tokens";
import { OrphanProbe } from "./OrphanProbe";

// The film finish over every frame: moving grain and a soft vignette. A
// perfectly clean computer-drawn frame is one of the things that reads as
// machine-made. The grain is SVG noise with a new seed every frame, so it
// is deterministic for the render and needs no texture file. It also
// mounts the orphan and safe-zone probe, so every composition that wears
// the finish can be scanned.
export const Finish: React.FC<{ grain?: number; vignette?: number }> = ({ grain = THEME.grain, vignette = THEME.vignette }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(0,0,0,${vignette}) 100%)` }} />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, mixBlendMode: "overlay", opacity: grain }}>
        <filter id="finishGrain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={frame % 997} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#finishGrain)" />
      </svg>
      <OrphanProbe />
    </AbsoluteFill>
  );
};
