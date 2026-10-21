# 07: Visual grammars by kind of content

The style is fixed; the content is not. A business story, a history, a
book or a scientific result each needs its own way of showing evidence,
in the same light, one-face, no-ornament style. Rights for each kind of
material are in `02-research-and-rights.md`; this page is how to draw it.

Common to all:

- **The picture is the evidence.** Show the thing the sentence is about:
  the map, the figure from the filing, the line in the document, the page
  of the book. Generic mood pictures over talk are the weakest episodes.
- **One focal point at a time**, the subject in accent.
- **Every number on screen says what it measures**, with its unit and,
  where it has one, its source line.
- **Draw to scale, or say so.** Anything drawn at true scale is checked
  and logged; anything schematic says "drawn schematically" in its
  source line.
- **Mark the cover's subject** with `data-cover-subject`, so the cover
  check can measure it.

## Maps and globes

- **Projection with a reason.** Equal Earth for the world (it keeps area);
  Mercator only when its distortion is the point; an equal-area conic or
  azimuthal for a country or a region, centred on it. Define every
  projection once, in one module, and use the same factory for vector
  overlays and any raster plate, or they will not line up.
- **Locate before zooming in.** An episode about a place most viewers
  cannot place opens on a view wide enough to recognise (a hemisphere
  with its continents named), holds it while the hook is said, then moves
  in. Viewers dropped into a close-up do not know where they are.
- **Pull back when the narration points at the whole map** ("Blame this
  map", "maps like this one"): the camera pulls straight back about one
  point, scale eased in log space, until the whole map sits as a printed
  sheet on the page with a soft shadow, and returns when the story moves
  on.
- **A fixed plate for imagery.** Rasterise the basemap once (at most 4,096
  px wide) and move the image; zoom at most plate width ÷ 1,080; split a
  deep zoom into a second, higher-resolution plate rather than upscaling,
  and keep the wider plate drawn underneath so a plate edge can never
  slide into frame during a pull-back (one did, for five frames).
- **Overlays in screen space** from the projection, with stroke widths
  constant through zooms. Blur only plate images, never live vector
  layers.
- **Lines are cased** (`kit/Stroke.tsx`): a light under-stroke keeps a red
  or blue line clear of a mid-blue sea. Routes draw on with the move ease;
  great circles come from interpolation on the sphere, split at the
  antimeridian.
- **A distance the narration names is drawn as a line** between the two
  things it separates, drawn on the number, with its label ("671 km from
  the North Pole"). The end of a line is never left in empty sea: what it
  reaches is marked and named when it is drawn.
- **A change the narration describes is seen happening**: "real flights
  bend again" bends the route away from a dashed ghost of the straight
  one.
- **A coordinate the narration names is drawn as that line**, labelled,
  as it is said ("at 45 degrees", "the equator"); a bare number beside a
  shape does not say where 45 degrees is.
- **True-size comparisons rotate the shape on the sphere** (`lib/geo.ts`
  `slide`), which keeps its real area, and re-project it, so it shrinks or
  grows correctly; sliding it on screen keeps the wrong size, which is the
  lie the comparison exists to correct. Pass `upright` for a long east or
  west move, or it arrives on its side, and move its name with it
  (`slider`).
- **Labels** sit horizontal, beside what they name, never on a line or a
  coast; names go outside a circle, away from its rim; a moving dot's name
  rides on the side away from its path and fades near the frame's edges
  rather than stopping at them.
- **Borders fine and quiet**, the same weight in every episode; disputed
  borders dashed, taking no side; a past era's map shows no modern
  borders.
- **Any colour that encodes a quantity has a legend** saying what it
  measures and its scale, on screen from the first frame for as long as
  the encoding is, never fading in later.
- **Data texture must look pleasant at a glance**: a speckle of red dots
  reads as a rash. Choose the encoding from finished style frames.
- **The globe** is a top-standard 3D object: real relief, sea and land
  materials, soft studio light, a contact shadow, a crisp limb with an
  atmosphere rim, light falling off across the sphere, a sun glint on the
  sea; never a flat disc fading into haze. Slerp the camera direction and
  animate altitude separately (out, travel, in); a 4K texture unless a
  close zoom needs 8K. In React Three Fiber under Remotion, a texture that
  arrives after the first frame is never drawn unless something advances
  the frame loop.
- **Anything that stands for a 3D thing lives in the 3D scene.** A shaft or
  line through the planet is geometry in the scene (a lit tube with a real
  opening in the surface and a cut-away interior), occluded by the planet
  where it should be and lit by the same lights; a flat 2D stroke laid over
  the render has no depth and looks strange. Overlays drawn in screen space
  are for labels and marks on the surface, never for solid things.
- **Moving a picture for a cover or layout** is done with a camera offset
  applied to the picture and its overlays alike, never by moving a layer,
  which shows a straight edge of empty page.

## Charts and stat cards

- **A bar is as long as its value and nothing more** (`kit/Bars.tsx`): no
  empty track, box or frame runs past it, because an empty track makes a
  small value read as a big box. The longest value spans the scale. Every
  row comes with its own number.
- **A stat shows its final value at once** (`Stat`), with what it
  measures under it and its source line. No counting.
- **Rows named before numbers when the voice does it** ("Here are three
  bars" shows the rows' names; each bar grows on its number).
- **A list that reflows never squeezes**: each item moves at full speed
  under its own mask, so no two touch mid-move.
- **Axes only when they carry meaning**; gridlines faint; units in the
  label, not on every tick.
- **Shares are called shares, rates are called rates**, and the
  denominator is on screen when it matters ("72.5% of Argentina", not
  "72.5%").
- Money: the currency, the year, and nominal or inflation-adjusted, in the
  label or the source line.

## Timelines and dates

- **A real time scale**: positions proportional to time, so a gap that
  looks long was long. Mark breaks in the scale if one is unavoidable.
- **No paused frame shows a false date or position.** A marker that
  slides from the 21st to the 10th is wrong on every frame before it
  lands: place it at its value, then show the comparison.
- **Calendars change**: name the calendar where it matters (Julian and
  Gregorian, a year that began on 25 March), and write dates the way the
  source does when the episode is about the difference.
- **Eras as quiet bands**, labelled in sentence case; one "now" marker if
  the story needs it.

## Archival photographs, documents and portraits

- **Show the real thing, full bleed or as a print on the page** with a soft
  shadow; no fake film borders, sepia filters or scratches.
- **Motion with a reason.** A push-in goes to the detail the narration
  names, on its word; nothing drifts or breathes for its own sake.
- **Documents**: show the page, then bring the quoted line forward by
  dimming the rest of the page; the line stays at full strength while it
  is read. No boxes, no marker-pen overlays.
- **Portraits** carry the person's name and dates as a label, with the
  source line. No generated portraits of real people, no face-swaps, no
  "restoration" that invents detail.
- **Credit lines** in the form each licence asks for, on screen as a
  source line and in the caption's Sources.
- **Reconstructions** of what no camera saw are labelled "AI
  reconstruction" on screen and with the platform's label, kept short, and
  never stand in for evidence.

## Quotes and book text

- **Set the quote in the house type**, large, on the clean page, with
  curly quotation marks and a plain attribution line under it (author,
  work, year; translator if any).
- **Reveal it in sync with the voice**, word by word or line by line, and
  the narrator reads it exactly; an omission is marked with an ellipsis
  and does not change the meaning.
- **A book is shown by its title set in type**, or by a public-domain
  edition's page; in-copyright cover art is not decoration.
- Long passages are never put on screen; a short quotation with a stated
  purpose is.

## Companies, logos and products

- **A logo identifies, never decorates or endorses**: shown unaltered, at
  its own colours, beside the company's name, from the press kit. No
  morphing it, no placing it to imply a sponsorship.
- **Products** from press-kit images or our own photographs; competitors'
  marks only in a fair, factual comparison.
- **Business figures** as charts in the house style, with the fiscal year
  and currency in the label and "Source: <company> annual report <year>"
  as the source line.

## Science and diagrams

- **Diagrams drawn to scale, or marked "not to scale"**; dimension lines
  for any size the narration names.
- **Units** in SI with a plain explanation where the unit is the subject;
  uncertainty shown where the source gives it, not dropped.
- **Figures redrawn from data** in the house style, credited, rather than
  screenshots of papers.
