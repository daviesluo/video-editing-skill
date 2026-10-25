# 07: Visual grammars by kind of content

The style is fixed; the content is not. A business story, a history, a
book or a scientific result each needs its own way of showing evidence,
in the same light, one-face, no-ornament style. Rights for each kind of
material are in `02-research-and-rights.md`; this page is how to draw it.

Common to all:

- **The picture is the evidence.** Show the thing the sentence is about:
  the map, the figure from the filing, the line in the document, the page
  of the book. Generic mood pictures over talk are the weakest episodes.
  A real thing is drawn from its data, never as a stand-in shape: a
  mountain as its cross-section from a terrain model, a coast from the
  map, a building from its plan. Symmetric cones for three summits read
  as AI-made clip art, even with true heights, and so did true sections
  cut to 3 km and stood on columns: draw the thing wide enough to show its
  shape, from its own base up, its cut ends fading out, with nothing
  under it that it does not have.
- **One focal point at a time**, the subject in accent.
- **Every number on screen says what it measures**, with its unit and,
  where it has one, its source line.
- **Draw to scale, or say so.** Anything drawn at true scale is checked
  and logged; anything schematic (a path whose course is not published,
  a count or shape the source does not give) says "drawn schematically"
  in its source line.
- **A name sits nearer its own place than any other marked thing.** A
  country's name set level with the ringed place of something else, 90 px
  from the ring and further from the country, read as the ring's name.
- **Mark the cover's subject** with `data-cover-subject`, so the cover
  check can measure it.
- **Start from the kit.** `studio/src/kit/` has a designed component for
  each grammar below (`MapView`, `GlobeView`, `Sheet`, `CutAway3D`,
  `Bars`, `Stat`, `Timeline`, `Document`, `Quote`, `Logo`), and the
  example episode (`studio/src/episodes/Example.tsx`) uses each, keyed to
  its words.

## Maps and globes

- **Projection with a reason.** Equal Earth for the world (it keeps area);
  Mercator only when its distortion is the point; an equal-area conic or
  azimuthal for a country or a region, centred on it. Define every
  projection once, in one module, and use the same factory for vector
  overlays and any raster plate, or they will not line up
  (`lib/projections.ts`; `textures.py` builds a relief plate for each
  projection in its `PLATES`).
- **Locate before zooming in.** An episode about a place most viewers
  cannot place opens on a view wide enough to recognise (a hemisphere
  with its continents named), holds it while the hook is said, then moves
  in as a designed camera move (the `move` ease, scale eased in log
  space), never a cut to a close-up. Viewers dropped into a close-up do
  not know where they are, and an opening framed in close came back with
  "the map bigger at the start, then zoom in".
- **The map does not answer before the voice.** A question about where
  things lie is asked over a map that does not yet show the answer: both
  cities' dots sat on screen while the hook asked whether one lay east or
  west of the other. The places that answer it appear on the reveal word,
  and the cover follows the same rule.
- **Pull back when the narration points at the whole map** ("Blame this
  map", "maps like this one"): the camera pulls straight back about one
  point, scale eased in log space, until the whole map sits as a printed
  sheet on the page with a soft shadow, and returns when the story moves
  on (`kit/Sheet.tsx`: `sheetRect`, `pullBack`, `SheetFrame`).
- **A fixed plate for imagery.** Rasterise the basemap once (at most 4,096
  px wide) and move the image; zoom at most plate width ÷ 1,080; split a
  deep zoom into a second, higher-resolution plate rather than upscaling,
  and keep the wider plate drawn underneath so a plate edge can never
  slide into frame during a pull-back (one did, for five frames). Where
  no finer source exists (open ocean), the plate may give way to the
  sea's own colour instead, on an eased band of the zoom's log scale that
  ends where the plate is enlarged about 3.5 times; driven by the scale
  alone, one such change fell on the zoom's fastest stretch and went in
  five frames.
  The detail plate also fades out before its own edge (a gradient mask
  from a little inside the edge to the edge, worked out in the view's
  projection), or its edge shows as a hard line where the coarser plate
  under it takes over: a detail plate ending at 55°N drew a straight seam
  across the top of a wide opening, on frame 0. `kit/MapView.tsx` draws a
  plate and hands its children the projection and the plate's transform,
  so overlays land on the raster to the pixel; `lib/plateLook.ts` sets
  each plate's grading.
- **A flat map view stays inside its plate**, with its span worked out
  from its scale before it is drawn: a view w px wide at k px a radian
  spans w ÷ k radians, so an 880 px card at 200 px a radian spans about 250° and
  shows a blank strip where a world plate ends at ±180°. One card did,
  through two renders and two reviews, because the stills taken happened
  to look full; at 240 px a radian it spans 210° and fills. Work out every
  inset, card and opening view this way, both across and up and down, and
  centre it so no side passes the plate's edge: a regional plate fetched
  only to the equator, under a wide view whose top row reached 2.6° N,
  drew a hard edge across the top of 52 seconds of frames.
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
- **A marked place is a dot sized for the view**, never a modelled hole
  or pin: "a dot of the right size, it doesn't need to be a real hole".
  Anything sized in world units swells as the camera closes in (a hole
  0.026 radii across ballooned three to six times in the close-ups,
  covering its labels and the line it measured), so draw a marker as a 2D
  overlay from the projection, or, if it must live in the 3D scene, size
  it by the camera's distance (`lib/viewScale.ts`, `worldForPx`). 3D is
  only for what is truly 3D.
- **Labels** sit horizontal, beside what they name, never on a line or a
  coast; names go outside a circle, away from its rim; a moving dot's name
  rides on the side away from its path and fades near the frame's edges
  rather than stopping at them.
- **Borders fine and quiet**, the same weight in every episode; disputed
  borders dashed, taking no side; a past era's map shows no modern
  borders.
- **Any colour that encodes a quantity has a legend** saying what it
  measures and its scale, on screen from the first frame for as long as
  the encoding is, never fading in later. The encoding must be the
  quantity the legend names: a glow computed per grid cell is not "people
  per km²" until each cell is divided by its area on the sphere.
- **Data texture must look pleasant at a glance**: a speckle of red dots
  reads as a rash. Choose the encoding from finished style frames.
- **The globe** is a top-standard 3D object: real relief, sea and land
  materials, soft studio light, a contact shadow, a crisp limb with an
  atmosphere rim, light falling off across the sphere, a sun glint on the
  sea; never a flat disc fading into haze. Slerp the camera direction and
  animate altitude separately (out, travel, in); a 4K texture unless a
  close zoom needs 8K. In React Three Fiber under Remotion, a texture that
  arrives after the first frame is never drawn unless something advances
  the frame loop. `kit/GlobeView.tsx` is that globe, lit from
  `THEME.globe` (`keyLight` gives its key light's direction for anything
  else in the scene); it takes a camera (`lerpCam` between two), clipping
  planes (`clip`, `clipIntersection`) and objects of its own (`scene`).
- **Overlays on a globe use the camera's own projection.** Draw filled
  shapes and lines with the vertical-perspective projection that matches
  the 3D camera to the pixel (`makeGlobePath`, `makeGlobeProject`),
  clipped at the camera's horizon; offset the view with the camera
  (`shiftY`, which sets `setViewOffset`), never by moving the layer. A d3
  projection fitted by its box polygon fits the whole world; fit by edge
  points instead.
- **Anything that stands for a 3D thing lives in the 3D scene.** A shaft or
  line through the planet is geometry in the scene (a lit tube through a
  cut-away interior, its way in and way out marked as dots), occluded by the planet
  where it should be and lit by the same lights; a flat 2D stroke laid over
  the render has no depth and looks strange. Overlays drawn in screen space
  are for labels and marks on the surface, never for solid things.
- **A cut-away 3D object** (`kit/CutAway3D.tsx`, worked through on a shaft
  through a planet, and in the example's globe beat) shows the inside of
  something solid: `wedge` gives the clipping planes and the two section
  faces, `SectionFace` shades the layers under the scene's key light,
  `Shaft` is the lit tube. Its rules, each learned frame by frame:
  - the cut is fixed to the object, so it turns with it;
  - it is opened turned off square to the camera (about 0.6 rad), so one
    face reads broad and the other foreshortened, which reads as depth;
    square on, a wedge reads as flat petals;
  - it is shut before the camera turns, never during the turn: shut while
    the camera turned, the broad face swept the planet as a band, the page
    showed through the wedge, and a sliver of shaft showed through the
    closing seam. Close it fast, ending as the turn begins;
  - a label tied to the cut ("Earth's centre") leaves before the cut shuts,
    or it is left floating over the surface;
  - the layer radii come from a cited model (`LAYERS`, from PREM) and are
    logged as facts when any is said or labelled;
  - seams stay a pixel wide at any distance, and a long object fades out
    above the captions in screen space (`fadeBelow`) so no camera move
    crosses them.
  Explore a new cut-away in the lab composition `CutAwayLab`
  (`studio/src/lab/`), every choice a prop, before it goes into an episode
  (`06-visual-style.md`, "Every detail is designed").
- **Moving a picture for a cover or layout** is done with a camera offset
  applied to the picture and its overlays alike, never by moving a layer,
  which shows a straight edge of empty page. Every mask and clip moves
  with it (`CaptionClearDefs`'s `dy`, a 3D object's `fadeBelow`, the
  globe's `shiftY`): a mask left in screen coordinates on a shifted cover
  hid a city's dot and faded the far end of a line.

## Charts and stat cards

- **A bar is as long as its value and nothing more** (`kit/Bars.tsx`): no
  empty track, box or frame runs past it, because an empty track makes a
  small value read as a big box. The longest value spans the scale. Every
  row comes with its own number, centred on its bar: beside the bar's end
  where there is room, inside the bar in the mark colour where there is
  not (`kit/barsLayout.ts`).
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
- `kit/Timeline.tsx` draws the axis to scale (years to x, ticks at a
  round step), places each event at its value on its word, alternates
  labels above and below when they would collide, and takes eras and a
  calendar label.

## Archival photographs, documents and portraits

- **Show the real thing, full bleed or as a print on the page** with a soft
  shadow; no fake film borders, sepia filters or scratches.
- **Motion with a reason.** A push-in goes to the detail the narration
  names, on its word; nothing drifts or breathes for its own sake.
- **Documents**: show the page, then bring the quoted line forward by
  dimming the rest of the page; the line stays at full strength while it
  is read. No boxes, no marker-pen overlays. `kit/Document.tsx` sets a
  page as a print with a soft shadow, either a scan (`src`, with the
  line's box) or set text (`paragraphs`), pushes in gently on the line's
  word and dims the rest; its credit is the source line. On a dark film a
  white page shows at about 0.9 of its brightness: cut in at full white
  from the black page, four documents were the film's hardest jolts.
- **Portraits** carry the person's name and dates as a label, with the
  source line. No generated portraits of real people, no face-swaps, no
  "restoration" that invents detail.
- **Old footage as it survives.** Fetch the best copy there is, and show
  it as it is, at a size its detail carries (a band at the full width, not
  blown up to fill the frame). Never clean it with an upscaler: a 2007
  broadcast scaled down to its true detail and back up with Real-ESRGAN
  (`realesr-general-x4v3`, no face model) came out with smooth, waxy skin
  and drawn edges, and the owner read it as AI-made and asked for the
  original back. A soft archive picture reads as real; a restored one does
  not.
- **A broadcaster's caption that carries the story stays readable.** A
  news shot's lower third is cropped off when it only names the channel
  or the show, but when it states what the story is about (a deal and its
  price, a record, a verdict), the shot is held whole with the caption
  readable: no punch-in, no crop that cuts into it. The owner asked for a
  CNN bite to be shown "without pushing in, so viewers can see clearly
  the price it sold for". A number in it that differs from the narration's
  (an announced price later cut) is reconciled on screen before the shot,
  each value with its date, so the viewer never sees two prices for one
  thing unexplained. One name per speaker: our own credit is left off
  where the broadcaster's lower third already names who is speaking (a
  correspondent was named twice at once).
- **A logo that is the subject is shown whole, with room round it.** A
  sign cut through its letters reads as careless (the owner: "the Verizon
  logo is cut off; show it whole"). Find the mark's foot on the source
  frame row by row: if its letters' pixel count holds steady down to a
  news band, the band covers the mark in the source itself and no crop
  shows it whole (a crop at 604 left the letters touching the edge, their
  feet under CBSN's band from row 608; it was judged whole on a reduced
  still and a review sent it back). Then take another shot of the same
  mark: a photograph inside another broadcast's split screen, its panel
  alone, served (CNN's Getty picture of the sign, at 1.8 times). A panel
  whose neighbour cuts a second logo is shown alone.
- **A clip that fills the upright frame is chosen for it.** A landscape
  clip filled to 9:16 keeps a slice 0.56 of its width, enlarged 1.78
  times: what reads in the wide shot (two founders at a laptop) becomes a
  fragment (one of them looking down, cut at the shoulders), and the
  owner found it odd. The full frame gets an upright source, or a shot
  whose subject is whole and readable inside that slice; check the slice
  on a still before using it.
- **A quote is one card.** A quoted passage is shown once, on its own
  card with its source line, and the words that carry it are highlighted
  in place on that card as they are read. No cut or zoom to a second card
  of the same quote: the text jumps before it can be read, and the viewer
  takes the second card for a different quote. The owner, on three quote
  cards each zoomed to a closer card of their key line: "show the quote
  only once, highlight on it, no second one; otherwise the text jumps too
  fast to read and looks like different quotes". A long quote is held
  long enough to read rather than cut into. The card holds the whole quote
  the narration reads, every sentence inside its quote marks: a sentence
  left off the card and laid over other pictures reads as the narrator's
  own words, not the speaker's (the owner, on a card that stopped one
  sentence short: "why isn't that line in the quote?").
- **Every source once.** No clip, shot, photograph or camera set-up
  appears twice in an episode, and no shot is shown twice back to back
  reframed (an upright slice of it, then the whole frame). The owner:
  "replace any material that repeats in the video". A cut made for pace
  takes new material, never a picture already used (a re-cut at a fast
  reference's pace put the film's title, a logo and two photographs on
  screen twice). An interview is cut so each of its camera set-ups is
  seen once: a cutaway carries the voice between them rather than a
  return to the same framing, and a wide shot that opens a bite does not
  close it too. List every source and its uses from the code before the
  render and read it for repeats.
- **A title the voice names is shown by its strongest image.** When the
  narration names a film, a book or a show, the picture is its poster or
  cover, whole in the frame and then pushed in with the eased camera to
  its face or its title, not the work's own title card: white letters over
  a dark street read as text, not as the thing. The owner, on a film's
  title shot: "this would look better as the poster, with a zoom; design
  it", and "that clip is too weak". Pick the version whose title reads in
  the frame while the voice names it: a teaser whose title ran down its
  edge, under the player's top bar, left the name unseen, and the
  one-sheet with its title box replaced it. The poster counts as a source
  like any other: shown once, so a second appearance (a broadcaster's
  frame of it later on) goes.
- **Moving footage where the series cuts on footage.** In an edit built on
  clips, a page that stands for a company or a person is a clip, not a
  photograph, from the company's own stage: a keynote or talk with its
  name on the wall behind the speaker. The owner sent back stage
  photographs ("use video, not photos") and then the company's brand films
  ending on its wordmark ("not that kind; a launch event or a talk, with
  the name as the backdrop"). A full talk posted by the company's own
  people on X is often fetchable where the conference's YouTube copy is
  not.
- **No step in brightness inside a shot.** Darkening a clip from a beat
  partway through it (so a line reads) drops the shot's brightness by a
  notch at once, and the owner saw it as the page flickering. Darken a
  clip from its first frame or not at all, and choose shots whose own dark
  area holds the line.
- **A speaker filled into the upright frame** from a 16:9 shot has the
  head at the very top, under the player's top bar: stop the box at the
  safe top (y 250) and let the page show above it. A line set over a person
  sits on the body, never across the face.
- **Credit lines** in the form each licence asks for, on screen as a
  source line and in the caption's Sources. A credit shows only over the
  picture it credits: a photograph's credit kept running across a film
  shot cut in between two photographs, crediting the film to the wrong
  source.
- **Reconstructions** of what no camera saw are labelled "AI
  reconstruction" on screen and with the platform's label, kept short, and
  never stand in for evidence.

## Quotes and book text

- **Set the quote in the house type**, large, on the clean page, with
  curly quotation marks and a plain attribution line under it (author,
  work, year; translator if any).
- **Reveal it in sync with the voice**, word by word or line by line, and
  the narrator reads it exactly; an omission is marked with an ellipsis
  and does not change the meaning. `kit/Quote.tsx` takes the words and the
  time of each from the word cues.
- **Every quoted passage carries its source on screen**, the whole time
  it is shown, including a close-up of one line: a press release opened
  straight on its key passage lost the attribution line the full view
  had. And a quote cut short is cut where it does not narrow what it
  says: an annual report's "65 million Web pages per day on Yahoo! …" read
  as Yahoo.com alone, where the sentence went on "and other
  Yahoo!-branded online media properties".
- **A book is shown by its title set in type**, or by a public-domain
  edition's page; in-copyright cover art is not decoration.
- Long passages are never put on screen; a short quotation with a stated
  purpose is.

## Companies, logos and products

- **A logo identifies, never decorates or endorses**: shown unaltered, at
  its own colours, beside the company's name, from the press kit. No
  morphing it, no placing it to imply a sponsorship. `kit/Logo.tsx`
  shows a mark beside its name and moves it by opacity only; the toolkit
  ships only a placeholder mark (`PlaceholderMark`), never a real
  company's.
- **Products** from press-kit images or our own photographs; competitors'
  marks only in a fair, factual comparison.
- **Products in use are real footage**: a robot on its engineering
  walking test, a headset worn by a person, a drone in flight, never the
  company's advert (an owner, of a humanoid's polished ad: "a robot
  people made themselves, engineering test footage, not a marketing
  video") and never a generated screen or game demo ("too AI").
- **People in a collage**: each face once in the film (one allowed
  exception at most), faces the audience knows (an owner, of a founder
  less known abroad: "who is that? use someone like Netflix's founder"),
  each framed on the person at the moment it is shown (a frame of legs, a
  blur or pillarbox bars is replaced or cropped).
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
