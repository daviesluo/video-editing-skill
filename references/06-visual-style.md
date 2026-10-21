# 06: Visual style

The house style: light, fresh and restrained, set in one typeface, using
the full height of the 9:16 frame, with nothing a phone's interface
covers. It must look like a high-budget production designed by people:
an ordinary viewer should not be able to tell how it was made. Every
value below lives in `brand.json` (brand) or `studio/src/brand/tokens.ts`
(craft); this page says why.

## Colour

| Token | Hex | Role, never reassigned within an episode |
|---|---|---|
| `ink` | #F2F6F5 | the page: a cool near-white |
| `ocean` | #80B2D2 | water |
| `land` / `landEdge` | #FFFEFA / #8FA9B0 | land and coast |
| `graticule` | rgba(18, 42, 49, 0.08) | grid lines, barely there |
| `paper` | #122A31 | type: a petrol ink |
| `dim` | #5B6F75 | secondary marks |
| `note` | #3B5056 | source lines and small secondary type (7:1 on the page) |
| `accent` | #D04A2C | the subject: the route, the highlighted place, the answer, the spoken caption word |
| `cool` / `coolLight` / `coolDark` | #335F92 / #8DB0D4 / #244E7A | the comparison |
| `warn` | #5E1A3A | the misconception being corrected |
| `mark` | #FFFEFA | casings and marks on colour |
| `pressed` | #DCE5E4 | the pressed Follow button |

- **Light and fresh, not dark.** A deep navy page with a warm glow (the
  look of most generated explainers) reads as machine-made.
- **Light never means washed out**: no pale-grey sea, no grey land, no
  white fog laid over the picture. A map under an 85 to 90 percent white
  veil reads as a washed-out picture; diagrams sit on the clean page.
- **Nor vivid**: fully saturated blue sea and turquoise shelves read as
  cheap. Contrast is carried by lightness, with restrained colour. Choose
  levels from a ladder of stills, not by argument.
- **Colour carries meaning.** Accent is always the subject, cool the
  comparison, warn the misconception. A tint says "this is what the
  sentence is about": never leave a region tinted while the narration
  names a different one.
- The steel blue is a step darker than a pure palette would choose, so it
  holds 6:1 on the page and stays at least 20 CIEDE2000 from the wine and
  the ink under simulated colour-vision deficiencies. Check any new
  palette the same way.

## Type

- **One typeface**, the caption face: Archivo at normal width, vendored
  (SIL OFL). No monospace, no wide or condensed variants, no second
  family: mixed faces read as a template.
- **Sentence case** everywhere, no all-caps letter-spaced labels.

| Use | Size, px | Weight | Notes |
|---|---|---|---|
| headline | 96 to 120 | 820 | tracking -0.03 em, line height 1.02, balanced lines, revealed word by word from a mask |
| cover title | 96 to 108 | 880 | two or three lines |
| stat number | 136 | 880 | shown at its value at once |
| stat label | 36 and up | 600 | |
| caption | 76 (down to 61 when a page is scaled) | 800 | word by word, the spoken word in accent |
| map and chart label | 40 | 720 | horizontal, beside what it names |
| badge | 36 | 760 | series name, then "Part N" in accent |
| chip (a kicker line) | 34 | 650 | |
| source line | 29 | 560 | `note` colour, "Source: …" |

- **Small type is at least 29 px and wears the tight halo** in the page
  colour (`THEME.haloStrong`), so a badge, label or source reads on any
  map, chart or photograph without a box behind it.
- **No orphans**: a line never ends with one word alone. Checked by
  measurement (`OrphanProbe`), because the eye misses it.

## No machine look

Each of these reads as generated or as a template, so none is used:

- boxes, outlined chips, pills, cards with borders behind text;
- "·" separators, dashes or rules as ornaments, arrows in text (write
  natural phrases: "Source: NOAA", "First posted in 2013", "Coming up
  Part 4");
- neon, glow, bloom, lens flares, blur-in type, light leaks;
- counting numbers: a number rolling up shows a false value on every
  frame before it lands, and a paused frame or a cover catches it there;
- stock motion-graphics transitions (zoom blurs, glitches, whip pans for
  their own sake);
- a perfectly clean computer frame: a light grain and a soft vignette
  (`kit/Finish.tsx`) sit over every frame.

## Every detail is designed

Nothing is drawn the quick way. A detail that is merely present (a flat
line laid over a rendered globe, a default marker, a stock arrow) reads at
once as unfinished, however right the rest is.

- **Each element gets its own design pass**: its shape, light, material,
  edges and motion, decided and looked at on stills, not left at the
  library default.
- **Anything that stands for a 3D thing is built in the 3D scene**, lit and
  shaded with it, never a flat 2D stroke over the render. A shaft through
  a planet is a lit tube with a real opening in the surface and a cut-away
  interior, not a red line on top of the picture.
- **It must look like what it represents.** A shaft looks dug, a route looks
  travelled, a document looks like paper.
- **Any change of look is shown first** as stills of two or three finished
  options, and one is picked before anything is rebuilt (see "Style
  changes" below).

## Layout (1080x1920)

- **The full height.** Never the letterboxed look with a picture band in
  the middle and empty bars above and below. The picture runs to the
  edges; type sits on it with halos and a light scrim.
- **Badge** at x 100, `LAYOUT.badge` y 262: its type starts about 34 px
  under the platform's top bar. Close under the bar, not far below it.
- **Headline and stat cards** from `LAYOUT.top` y 314.
- **Captions** at `LAYOUT.captions` y 1450, in a box from x 200 to 880.
- **Key text** inside x 90 to 960 and y 250 to 1,230 (above the captions).
- **One focal point at a time**; everything else dims or leaves.
- **Nothing crowds the headline**: the subject keeps clear space under
  the headline block, and no text sits over the shape, route or circle it
  labels.

## The safe zone, measured on the real player

The platform's interface covers parts of the frame, and the numbers in
guides do not match what a phone shows. These were measured on a posted
Reel on a phone, against a screenshot of it playing:

- the top bar (back arrow, tabs, icons) covers y 0 to about 245;
- the player fills the screen's height and crops about 52 px off each
  side;
- the like, comment, share and audio column covers x 922 to 985 from y
  about 1177 down;
- the name, caption and audio line start about y 1700.

So `SAFE` is x 90 to 960, y 250 to 1690, and no text right of x 900 below
y 1150. `ORPHANS=1 node scripts/stills.mjs` reports any visible text
outside it ("UNSAFE"). Re-measure on your own posted video, on the
platforms you post to, before trusting these: a badge placed by a guide's
numbers sat under the tabs on the first post.

## Style changes

A change of look (palette, globe skin, data texture, type) goes to the
owner as two or three **finished** style frames first, each already
beautiful on its own and designed to a named top-tier reference shown
beside it, never "the technique roughly working". Pick from the frames,
then rebuild. One attempt at a look the owner dislikes is fair; if the
second misses, stop and agree the target before a third.

## Making it your own

Edit `brand.json`: the series name, handle, promise line, avatar image,
and the palette (keep the roles: page, type, accent for the subject, cool
for the comparison, warn for the misconception). The safe zone and cover
tile are measurements, not taste; change them only by measuring again.
