import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { Avatar } from "../brand/Avatar";
import { DISPLAY } from "../brand/fonts";
import { COLORS, HANDLE, PROMISE, SERIES, THEME } from "../brand/tokens";
import { enter, exit, fade, lerp, move, ramp } from "../lib/anim";
import { KineticTitle } from "./Type";

// The follow beat, which ends every episode: after the content a light veil
// comes over the picture and the account's profile rises (avatar, name,
// handle, the promise). The narrator says "Enjoy stories like this? Follow
// for a new one every day." and on "Follow" a fingertip taps the Follow
// button, which turns to Following. On "Next" the whole profile shrinks
// into the end card's header and the next part's title rises under it: one
// continuous move, no cut. "Stories like this" points at the episode, so
// its own picture stays in view above the profile as a card (`card`, laid
// out by the episode inside FOLLOW_CARD) until the profile moves up. The
// end card says "Coming up" and the part, and the teaser title is the next
// episode's hook word for word.

// The profile, laid out once at full size (state A, the follow beat) and
// moved as a single block into the end card's header (state B).
const GROUP = { x: 150, y: 720, w: 780 };
const AVATAR = 200;
const BUTTON = { y: 252, h: 100, r: 24 };
// In the header the name and handle stay at least 29 px (the series' small
// type floor); the promise and the button, which would fall under it, fade.
const HEADER = { x: 100, y: 300, k: 0.8 };
// The tap lands on the button right of its label, so the label stays in
// view through the press.
const TAP = { x: GROUP.x + GROUP.w / 2 + 210, y: GROUP.y + BUTTON.y + BUTTON.h / 2 };
// Where an episode puts its picture during "Enjoy stories like this?": above
// the profile, inside the safe box.
export const FOLLOW_CARD = { x: 100, y: 290, w: 880, h: 380 } as const;
// The pressed "Following" state: the page colour, a shade darker.
const FOLLOWING = COLORS.pressed;
// The short end's title block: "Coming up" on the headline line, the title
// under it, all above the profile with room to spare.
const SHORT_TITLE_TOP = 314;

const mix = (a: string, b: string, t: number) => {
  const p = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [x, y] = [p(a), p(b)];
  return `rgb(${x.map((v, i) => Math.round(lerp(v, y[i], t))).join(",")})`;
};

// The episode hides its own badge under the veil (`followVeil`): the
// profile carries the name from here on, and a badge dimmed under the veil
// would read as a leftover.
// An even dissolve (in and out eased), never a flash: an ease-out put most
// of the change into the first four frames.
export const followVeil = (frame: number, fps: number, cta: number) => ramp(frame, fps, cta - 0.6, 0.75, fade);

// What does not go into the header (the promise, the button, an episode's
// picture card) leaves first, before the title rises, fading evenly through the
// start of the move rather than popping out.
// The short end (`short`) moves nothing into a header: only the episode's
// picture card leaves, and it has gone before the next title rises in its
// place.
export const followLeave = (frame: number, fps: number, next: number, short = false) =>
  short ? ramp(frame, fps, next - 0.85, 0.55, fade) : ramp(frame, fps, next - 0.6, 0.55, fade);

export const FollowBeat: React.FC<{
  // Video times (s): the start of "Enjoy stories like this?", the word
  // "Follow", and the start of "Next, in part N: ...".
  cta: number;
  tap: number;
  next: number;
  // The next part's number and title (KineticTitle markup: *word* in accent).
  part: number;
  title: string;
  // The episode's picture during "Enjoy stories like this?", in frame
  // coordinates inside FOLLOW_CARD; it leaves with the button.
  card?: React.ReactNode;
  // Or a picture under the veil kept in view through a round window (a
  // globe the episode shrinks into the card): its final centre y and
  // radius. The window opens from the whole frame and closes as the card
  // would leave.
  // `t` is the episode's own progress into the card (default: the veil's).
  hole?: { y: number; r: number; t?: number };
  // The short end, for every new series: one line, "Enjoy stories
  // like this? Follow for part N: <the next question>", about 5 s. On a
  // series' first parts the retention curve fell from about a quarter of
  // the viewers to about 5% on "Enjoy", so the teaser after a separate
  // follow line was seen by almost no one. The profile stays where it
  // rose, its button left at Following; the picture card leaves after the
  // tap, and the next title rises in its place above the profile on the
  // question's first word (`next`).
  short?: boolean;
  // The next title's size: below 96 when its lines would not fit.
  titleSize?: number;
}> = ({ cta, tap, next, part, title, card, hole, short = false, titleSize = 96 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const veil = followVeil(frame, fps, cta);
  if (veil <= 0) return null;

  // State A: the profile rises piece by piece, from 0.4 s after "Enjoy",
  // once the episode's picture has shrunk into its card: two moving things
  // never cross (from cta + 0.1 the profile rose into the shrinking card).
  const inAt = (d: number) => ramp(frame, fps, cta + 0.4 + d, 0.55, enter);
  const avatarIn = inAt(0);
  const nameIn = inAt(0.08);
  const handleIn = inAt(0.14);
  const promiseIn = inAt(0.2);
  const buttonIn = inAt(0.28);

  // The tap: a fingertip glides in, presses on the word, lifts; a ripple
  // spreads from the press and the button turns to Following.
  const touch = Math.min(ramp(frame, fps, tap - 0.5, 0.25, enter), 1 - ramp(frame, fps, tap + 0.18, 0.3, exit));
  const glide = ramp(frame, fps, tap - 0.5, 0.42, move);
  const press = Math.min(ramp(frame, fps, tap - 0.08, 0.08, enter), 1 - ramp(frame, fps, tap + 0.06, 0.16, enter));
  const ripple = ramp(frame, fps, tap, 0.55, enter);
  const done = ramp(frame, fps, tap, 0.22, enter);
  const tick = ramp(frame, fps, tap + 0.06, 0.3, enter);

  // State B: the profile moves into the end card's header.
  const toHeader = short ? 0 : ramp(frame, fps, next - 0.35, 0.8, move);
  const leave = followLeave(frame, fps, next, short);
  // What leaves on the long end: in the short one the promise and the
  // button stay.
  const stays = short ? 0 : leave;
  const k = lerp(1, HEADER.k, toHeader);
  const gx = lerp(GROUP.x, HEADER.x, toHeader);
  const gy = lerp(GROUP.y, HEADER.y, toHeader);
  // On the short end the title leads its first word, as every reveal does.
  const titleIn = short ? ramp(frame, fps, next - 0.25, 0.4, enter) : ramp(frame, fps, next + 0.3, 0.45, enter);

  const rise = (p: number): React.CSSProperties => ({ opacity: p, translate: `0px ${(1 - p) * 18}px` });
  const fill = mix(COLORS.accent, FOLLOWING, done);
  const label = mix(COLORS.ink, COLORS.paper, done);

  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          backgroundColor: `rgba(${THEME.scrim},${0.9 * veil})`,
          ...(hole
            ? (() => {
                const k = hole.t ?? veil;
                const y = lerp(960, hole.y, k);
                const r = lerp(1100, hole.r, k);
                const a = leave.toFixed(3);
                const m = `radial-gradient(circle ${r + 3}px at 540px ${y}px, rgba(0,0,0,${a}) 0, rgba(0,0,0,${a}) ${r}px, #000 ${r + 3}px)`;
                return { maskImage: m, WebkitMaskImage: m };
              })()
            : {}),
        }}
      />
      {card ? <AbsoluteFill style={{ opacity: 1 - leave }}>{card}</AbsoluteFill> : null}
      <div style={{ position: "absolute", left: gx, top: gy, width: GROUP.w, transformOrigin: "0 0", scale: `${k}` }}>
        {/* Avatar: the account's own picture, cropped to a circle as the platform shows it. */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: AVATAR,
            height: AVATAR,
            borderRadius: "50%",
            overflow: "hidden",
            opacity: avatarIn,
            scale: `${lerp(0.84, 1, avatarIn)}`,
            boxShadow: "0 14px 34px rgba(18,42,49,0.20), 0 2px 6px rgba(18,42,49,0.12)",
          }}
        >
          <Avatar size={AVATAR} />
        </div>
        <div style={{ position: "absolute", left: AVATAR + 40, top: 18, fontFamily: DISPLAY }}>
          <div style={{ fontWeight: 820, fontSize: 64, lineHeight: 1, letterSpacing: "-0.025em", color: COLORS.paper, ...rise(nameIn) }}>{SERIES}</div>
          <div style={{ marginTop: 14, fontWeight: 600, fontSize: 37, lineHeight: 1, color: COLORS.note, ...rise(handleIn) }}>{HANDLE}</div>
          <div style={{ marginTop: 16, fontWeight: 600, fontSize: 34, lineHeight: 1, color: COLORS.accent, ...rise(promiseIn), opacity: promiseIn * (1 - stays) }}>{PROMISE}</div>
        </div>
        {/* The button. */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: BUTTON.y,
            width: GROUP.w,
            height: BUTTON.h,
            borderRadius: BUTTON.r,
            background: fill,
            overflow: "hidden",
            ...rise(buttonIn),
            opacity: buttonIn * (1 - stays),
            scale: `${1 - 0.035 * press}`,
          }}
        >
          {/* The ripple spreads from where the finger pressed. */}
          {ripple > 0 && ripple < 1 ? (
            <div
              style={{
                position: "absolute",
                left: TAP.x - GROUP.x - lerp(30, 640, ripple),
                top: BUTTON.h / 2 - lerp(30, 640, ripple),
                width: 2 * lerp(30, 640, ripple),
                height: 2 * lerp(30, 640, ripple),
                borderRadius: "50%",
                background: "rgba(255,255,255,0.55)",
                opacity: 0.6 * (1 - ripple),
              }}
            />
          ) : null}
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", gap: 16, fontFamily: DISPLAY, fontWeight: 760, fontSize: 42, letterSpacing: "-0.01em", color: label }}>
            {done < 0.5 ? (
              <span style={{ opacity: 1 - done * 2 }}>Follow</span>
            ) : (
              <>
                <svg width={34} height={34} viewBox="0 0 34 34" style={{ opacity: (done - 0.5) * 2 }}>
                  <path d="M6 18 L14 26 L28 9" fill="none" stroke={label} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - tick} />
                </svg>
                <span style={{ opacity: (done - 0.5) * 2 }}>Following</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* The fingertip, drawn as a phone's touch marker: a light ring with a
          soft shadow, open in the middle, that firms up as it presses. */}
      {touch > 0 && toHeader === 0 ? (
        <div
          style={{
            position: "absolute",
            left: lerp(TAP.x + 120, TAP.x, glide) - 40,
            top: lerp(TAP.y + 220, TAP.y, glide) - 40,
            width: 80,
            height: 80,
            borderRadius: "50%",
            background: `rgba(255,255,255,${0.22 + 0.2 * press})`,
            boxShadow: "inset 0 0 0 4px rgba(255,255,255,0.95), 0 0 0 1.5px rgba(18,42,49,0.22), 0 8px 20px rgba(18,42,49,0.22)",
            opacity: touch,
            scale: `${1 - 0.14 * press}`,
          }}
        />
      ) : null}

      {/* The end card: the next part's title under the header. */}
      {titleIn > 0 ? (
        <div style={{ position: "absolute", left: 100, right: 100, top: short ? SHORT_TITLE_TOP : 560 }}>
          {/* "Coming up" and the part, set like the series badge, the part in the accent. */}
          <div style={{ display: "flex", alignItems: "baseline", gap: 14, fontFamily: DISPLAY, fontSize: 36, fontWeight: 760, letterSpacing: "-0.005em",
            textShadow: THEME.haloStrong, opacity: titleIn }}>
            <span style={{ color: COLORS.paper }}>Coming up</span>
            <span style={{ color: COLORS.accent }}>Part {part}</span>
          </div>
          <KineticTitle text={title} start={short ? next - 0.2 : next + 0.35} size={titleSize} style={{ marginTop: short ? 22 : 30 }} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
