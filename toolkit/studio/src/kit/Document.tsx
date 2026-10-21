import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, THEME } from "../brand/tokens";
import { DISPLAY } from "../brand/fonts";
import { enter, LINE_LEAD, move, ramp } from "../lib/anim";
import { SourceTag } from "./Type";

// A document shown as itself: a page on the page, with a soft shadow, as a
// print lies on a desk; no fake film borders, no sepia, no boxes. Then, on
// the word that reads it, the quoted line is brought forward: the rest of
// the page dims and the camera pushes in a little toward the line, which
// stays at full strength while it is read.
//
// Either `src` (a public-domain scan or photograph in public/, with
// `focusBox` the line's box in the image's own pixels) or `paragraphs` (a
// page set in the house face, with `focus` the paragraph brought forward and
// `focusY` where it sits down the page, 0 to 1, for the push-in).
export const Document: React.FC<{
  x?: number;
  y?: number;
  width?: number;
  // When the page appears, and when the line comes forward (the word that
  // points at it).
  start: number;
  at: number;
  end?: number;
  src?: string;
  imageSize?: readonly [number, number];
  focusBox?: readonly [number, number, number, number];
  paragraphs?: string[];
  heading?: string;
  focus?: number;
  focusY?: number;
  credit: string;
}> = ({ x = 110, y = 620, width = 860, start, at, end, src, imageSize, focusBox, paragraphs = [], heading, focus = 0, focusY = 0.3, credit }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shown = Math.min(ramp(frame, fps, start, 0.45, enter), end === undefined ? 1 : 1 - ramp(frame, fps, end - 0.3, 0.3));
  const forward = ramp(frame, fps, at - LINE_LEAD, 0.5, enter);
  const push = ramp(frame, fps, at - LINE_LEAD, 1.2, move);
  const dim = interpolate(forward, [0, 1], [0, 0.72]);
  const pad = 56;
  const size = 33;
  const lead = size * 1.45;
  const pageH = src && imageSize ? (width * imageSize[1]) / imageSize[0] : undefined;
  // The point the push-in moves toward: the focused line or paragraph.
  const origin = src && imageSize && focusBox ? `50% ${((focusBox[1] + focusBox[3] / 2) / imageSize[1]) * 100}%` : `50% ${focusY * 100}%`;
  const k = 1 + 0.1 * push;
  return (
    <div style={{ position: "absolute", left: x, top: y, width, opacity: shown, translate: `0px ${(1 - shown) * 30}px` }}>
      <div
        style={{
          position: "relative",
          width,
          height: pageH,
          transformOrigin: origin,
          scale: `${k}`,
          backgroundColor: COLORS.mark,
          borderRadius: 3,
          overflow: "hidden",
          boxShadow: "0 30px 70px -26px rgba(18,42,49,0.42), 0 3px 10px rgba(18,42,49,0.14)",
        }}
      >
        {src && imageSize ? (
          <>
            <Img src={staticFile(src)} style={{ position: "absolute", inset: 0, width, height: pageH }} />
            {focusBox ? (
              <div
                style={{
                  position: "absolute",
                  left: (focusBox[0] / imageSize[0]) * width,
                  top: (focusBox[1] / imageSize[1]) * (pageH ?? 0),
                  width: (focusBox[2] / imageSize[0]) * width,
                  height: (focusBox[3] / imageSize[1]) * (pageH ?? 0),
                  boxShadow: `0 0 0 4000px rgba(${THEME.scrim},${dim})`,
                }}
              />
            ) : null}
          </>
        ) : (
          <div style={{ padding: pad, fontFamily: DISPLAY, fontWeight: 430, fontSize: size, lineHeight: `${lead}px`, color: COLORS.paper }}>
            {heading ? <div style={{ fontWeight: 700, fontSize: size * 1.1, marginBottom: lead * 0.8, opacity: 1 - dim }}>{heading}</div> : null}
            {paragraphs.map((p, i) => (
              <p key={i} style={{ margin: i ? `${lead * 0.6}px 0 0` : 0, textWrap: "pretty", opacity: i === focus ? 1 : 1 - dim, fontWeight: i === focus ? 430 + 200 * forward : 430 }}>
                {p}
              </p>
            ))}
          </div>
        )}
      </div>
      <SourceTag text={credit} style={{ marginTop: 34 }} />
    </div>
  );
};
