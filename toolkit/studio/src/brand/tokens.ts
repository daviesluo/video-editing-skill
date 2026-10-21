import BRAND from "../../../brand.json";

// The house style in code. Brand values (name, handle, palette, safe zone,
// layout) come from brand.json at the project root, the one file a series
// edits, which the pipeline's checks read too. The craft values below
// (eases, halos) are the style itself and stay as they are.
//
// Colour carries meaning and is never reassigned within an episode:
// accent = the subject (the route, the highlighted place, the answer),
// cool = the comparison, warn = the misconception being corrected. `ink` is
// the page and `paper` the type. The palette is light and restrained:
// contrast is carried by lightness, not saturation, because a dark navy
// page with a warm glow reads as machine-made, a pale-grey page reads as
// washed out, and fully saturated colour reads as vivid and cheap.

export type Palette = typeof BRAND.palette;

export const COLORS: Palette = BRAND.palette;
export const SERIES: string = BRAND.series;
export const HANDLE: string = BRAND.handle;
export const PROMISE: string = BRAND.promise;
export const FRAME = BRAND.frame;

const page = BRAND.scrim;
export const THEME = {
  scrim: page,
  // Shadows that keep type legible over a picture, in the page colour, so
  // type reads on any map or photo without a box behind it.
  halo: `0 0 10px rgba(${page},0.95), 0 0 2px rgba(${page},0.95)`,
  haloSoft: `0 0 18px rgba(${page},0.95), 0 0 4px rgba(${page},0.95)`,
  // A tight outline for small type (badge, sources, labels): at 29 px and
  // up it reads on any background, map, chart or photograph.
  haloStrong: `0 0 1.5px rgba(${page},1), 0 0 3px rgba(${page},1), 0 0 3px rgba(${page},1), 0 0 7px rgba(${page},0.9), 0 0 16px rgba(${page},0.55)`,
  vignette: 0.05,
  grain: 0.045,
  // Scrims behind headlines stay light: a white fog laid over a picture
  // reads as washed out, so the type's halo does most of the work.
  scrimScale: 0.3,
  name: "relief",
  light: true,
  // Flat maps: relief plates, the globe's own skin reprojected
  // (pipeline/textures.py builds them), under crisp vector borders.
  plates: "relief" as "relief" | "satellite" | "vector",
  // How a data layer is laid over the globe.
  glow: "normal" as "normal" | "add",
  // The globe: a sea coloured by real depth, cream land with hypsometric
  // tints and a multi-directional hillshade, white ice, all calmed so it
  // reads neither washed out nor vivid; light that falls off across the
  // sphere, a soft sky fill, a contact shadow on the page, and an
  // atmosphere at the limb (a blue haze on the lit side, a cool shadow on
  // the far side, a thin halo outside). The textures are built by
  // pipeline/textures.py and are not committed.
  globe: {
    texture: "textures/earth-relief.jpg",
    tint: "#ffffff",
    ambient: 0.28,
    key: 3.1,
    sky: 0.75,
    skyColors: ["#EAF3FF", "#A9B8C4"] as [string, string],
    atmosphere: "#7DB9EA",
    atmosphereStrength: 0.6,
    bump: "textures/earth-bump.png" as string | undefined,
    rough: "textures/earth-rough.png" as string | undefined,
    bumpScale: 2.0,
    shadow: true,
    limb: { haze: "#9DC8EA", shade: "#1C3550", limbStrength: 0.62, shadeStrength: 0.3, haloStrength: 0.5 } as
      | { haze: string; shade: string; limbStrength: number; shadeStrength: number; haloStrength: number }
      | undefined,
    exposure: 1.0,
    roughness: 1.75,
  },
} as const;

// Key text stays inside this box, clear of the platform's interface,
// measured on a posted Reel on a phone: the top bar covers y 0 to about
// 245, the player crops about 52 px off each side, the like, comment and
// share column covers x 922 to 985 from y about 1177, and the name and
// caption start about y 1700. kit/OrphanProbe.tsx reports any text outside
// it. Re-measure on your own posted video before trusting it.
export const SAFE = BRAND.safe;

// The vertical layout uses the full height: the badge just under the top
// bar, the headline under it, the picture through the middle, the captions
// low, just above the interface.
export const LAYOUT = BRAND.layout;

// The smallest type on screen, px: smaller does not survive a phone.
export const SMALL_MIN = BRAND.type.smallMinPx;

// Easing presets as cubic-bezier control points.
export const EASE = {
  // Entrances: fast, but at most about a fifth of the change in one frame,
  // so a short fade never pops.
  enter: [0.3, 0.7, 0.4, 1],
  // Camera moves and shapes travelling: slow start and end.
  move: [0.65, 0, 0.35, 1],
  // Dissolves: eased at both ends, never steep in the middle.
  fade: [0.37, 0, 0.63, 1],
  // Exits: a gentle ease-in. A steeper one dropped half a fade in its last
  // frame and read as a cut.
  exit: [0.42, 0, 1, 1],
} as const;
