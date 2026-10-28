# 08: Animation

The picture follows the words. Whatever the narration points at happens
on screen on that word, a little early rather than late, and nothing else
moves without a reason. Scenes live in `studio/src/episodes/EpNN.tsx`;
every time in them comes from a word cue.

## The picture follows the words

- **Pointing words** ("this map", "this curve", "here", "that", "it",
  "these") show exactly that thing at that word: "Blame this map" pulls
  back to the whole map; "this curve" redraws the curve. Search every
  script for "this", "these", "that", "here" and "it" and check each one
  in the picture audit.
- **A described change is seen happening**, not just stated.
- **A named distance is drawn as a line** with its label, on the number;
  **an "in fact" size comparison is shown at true size** on the same map.
- **Every spoken number is on screen** with what it measures, or the thing
  it measures is highlighted while it is said.
- **The call to action is spoken and shown**, word for word on the end
  card.
- **"Stories like this" points at the story**: the episode's own picture
  stays in view as a card above the profile in the follow beat.
- **The screen is never empty while the voice talks about something**:
  hold the last picture until the next arrives.
- **A headline says what the voice says, in its words**, and names what
  the voice names: "Whole continents fool us too" over a voice saying
  "Whole continents fool us the same way" showed two wordings of one
  sentence at once, and "Memory lines them up" left "them" without the
  continents the voice had named. A headline starts on its own first word
  (a little ahead, as any reveal), never on the start of a sentence whose
  opening words are not in it: one began on "Actually," and was written
  out a second before the voice reached it.
- **A line built word by word is laid out whole from its first frame**,
  each word shown in its final place: a title assembled from the words
  so far ("It blew both.") re-centred at every word and dropped its
  baseline when the large last word landed, and its first word, held for
  its own onset, left three black frames after the cut. The first word
  shows on the cut; the others lead their words.
- **Words on a picture leave with it**: a caption, subtitle or credit ends
  at the cut that ends its picture at the latest. A real voice's subtitle
  that ran its 0.3 s tail past the cut sat over the next shot, on top of
  that shot's own caption.
- **A label that names a change appears with the change**, not before
  it: a chip saying "The line moved to New York" came up before the line
  moved, and "Lined up" now names its card as the shape slides into line.
- **The picture never answers the question before the voice does.** While
  the hook asks whether one city lies east or west of another, the map
  does not yet show where both are: a hook once asked it with both
  cities' dots already on the map, so the answer was on screen before
  "West." was said. The evidence for an answer arrives on the word that
  gives it, and the cover keeps the same rule (`10-covers.md`).
- **Open wide, then move in.** An opening map is framed wide enough to
  place the story, and moves in as a designed camera move (the `move`
  ease, scale eased in log space) on the words that narrow it, rather
  than starting in close: an opening in close came back with "the map
  bigger at the start, then zoom in".

## Reveals lead the word; moves start on it

- **A reveal tied to a word is on screen when the word begins.** A line or
  label that draws starts about 0.2 s ahead (`LINE_LEAD`) with the `enter`
  ease. The eye forgives a picture slightly early, never late; an ease-in
  from the word itself lands about a third of a second late and reads as
  delayed against the voice.
- **Camera moves and shapes travelling use the `move` ease**, slow at both
  ends.
- **Eases** (`EASE` in `tokens.ts`):

| Name | Bezier | Use |
|---|---|---|
| enter | 0.3, 0.7, 0.4, 1 | entrances: fast, but at most about a fifth of the change in one frame, so a short fade never pops |
| move | 0.65, 0, 0.35, 1 | camera moves, shapes travelling |
| fade | 0.37, 0, 0.63, 1 | dissolves: eased at both ends, never steep in the middle |
| exit | 0.42, 0, 1, 1 | exits: gentle, so a fade never drops half its value in its last frame |

- **Durations**: hero entrances 400 to 800 ms, camera 0.8 to 2 s, word
  stagger 40 to 70 ms, line stagger 60 to 100 ms. Springs, if any,
  critically damped; no bounce.
- **Speed, not only duration.** A camera move is judged by how far it goes
  in its time, against the episode's other moves of its kind: two half-turns
  of one globe run at about the same speed. One shipped at 140° in 0.55 s
  beside its twin's 2.25 s and read as a whip pan; it came from moving the
  turn's start to wait for a cut while its end stayed on its word. When a
  move's start moves, its end moves with it, or the words make room for it
  (`04-voice.md`, pauses only).
- **A long turn of a globe flies out and back.** Turning more than about
  45° close in races the surface across the frame: four turns of 95° to
  172° in 1.3 to 1.5 s peaked at 4,400 to 5,250 px/s at the frame's
  centre, two to three times a half-turn the owner had accepted (1,865
  px/s), between it and a rejected whip pan. Compute each move's peak
  surface speed per frame (angle per frame × focal length ÷ (distance −
  1)) and keep long turns at or under about 2,000 px/s: the camera climbs
  to 7 to 10 radii at the middle of the turn (distance × (1 + k·sin πe))
  and comes back, over 1.5 to 2 s. Keep longitude and latitude going
  straight rather than on a great circle when the great circle passes
  near a pole: a north-up camera spins there. A change the narration
  describes (the sea draining) happens after the camera lands, never
  during the turn, or it is not seen.
- **Hold still between beats.** Nothing drifts, floats or breathes for its
  own sake. Nothing travels more than a third of the frame without a
  keyframe, and no more than a third of the elements move at once.
- **No run of moves without a beat to read.** After each camera move the
  picture holds long enough to be read before the next one starts. Four
  moves in 3 s, each on its word, made a part feel rushed together with a
  fast take; the pace of the picture is measured with the pace of the
  voice, against the same reference parts ("The picture's rhythm",
  below).

## Cues are words, never seconds

- Segments in `episode.json` carry ids; scenes read `cueAt(timeline, lead,
  "seg")` (its first word), `"seg@k"` (its k-th word, from 0) or `"seg$"`
  (the end of its last word). Sound-effect cues use the same strings.
  Write cues as string literals, in double or single quotes, so
  `recue.py` can find and move them; a cue built at run time (a template
  string) is not moved and must be checked by hand after
  any wording change.
- **Never hard-code a second.** Every re-voice, re-time or added line
  moves words; a cue moves with its word, a second does not.
- **After any wording change**, run `python pipeline/recue.py
  episodes/<id> studio/src/episodes/EpNN.tsx <seg> "<old text>"`, read its
  plan, then `--apply`. One symbol becoming one word ("square kilometres"
  to "km²") shifted every later word by one, and a label meant for
  "Montana" silently pointed into the next sentence and never showed.
  `cueAt` and `mix.cue_time` refuse a cue past the end of its own segment.

## Designed, not drawn the quick way

Motion is part of each element's design pass, with its shape, light,
material and edges: how it enters, what it does on its word, how it
leaves. A thing that stands for a 3D object moves in the 3D scene with the
camera and the light (a shaft through a planet opens in the surface and
is seen in cut-away), never as a flat stroke sliding over the render; the
cut is fixed to the object, opened turned off square to the camera, and
shut before the camera turns, never during the turn; a label tied to the
cut leaves before it shuts (`kit/CutAway3D.tsx`, `07-visual-grammars.md`).
A place it passes through is a dot sized for the view, not a modelled
hole. An element belongs to its scene and is drawn only while that scene
is: a shaft only while its cut is open, so no tick of it is left on the
planet's edge once the cut has shut. What gives way to something else is
tied to that thing's arrival, never to its whole window: an outline faded
as `on × (1 − detailOn)` comes back as both leave together (at a quarter,
halfway through two equal fades), and a country's straight border crossed
the frame for a fifth of a second in a shipped part. Search every scene
for that product whenever one turns up. Judge every element on stills against two questions: does it look
designed, and does it look like what it represents?

## Lines and labels

- **A drawn line and its name come and go together.** A label that
  appeared without its line (a mask sized to its content, which for one
  level line has no height) and stayed after the line had gone was a
  failure; size masks in frame units.
- **Labels never sit half-transparent over a moving shape**: they move
  with it or leave. Every text block finishes fading before a camera move
  starts.
- **No faint stray label under an end card or a title**: labels fade out
  with the scene they belong to.

## Nothing over the captions

The caption band is sacred. A line that sweeps during a camera move once
crossed a caption word. Draw lines and their labels inside
`<g mask="url(#captionClear)">` with `<CaptionClearDefs />` in the
scene's SVG, which fades anything drawn under it out above the band; end
lines above the band by geometry where the facts allow; and move a label,
never the caption.

## Scene changes

- **A change of scene is one continuous move**, not a run of short
  stop-start moves: the big map going and the cards coming up move
  together, the map's return runs straight into the slide that follows
  it. One part made each change of scene two short moves with a beat
  between (the map out, then the cards in; the cards out, then the map
  back, then a slide), and its picture measured busier than the
  reference parts on every count while each move looked right on its own.
- **Sequence, do not cross-dissolve, when two scenes would collide.** The
  outgoing scene is gone before the incoming one starts; a map fading in
  over a card for 0.1 s is a double exposure. The outgoing picture leaves
  on its own ramp, timed to end before the arrival: a big map faded out
  with a veil whose window ran past the start of the card that replaced
  it, and the two maps showed half-transparent together for seven frames.
- **Two moving things never cross**: a card settles before the profile
  rises under it.
- **Dissolves are eased in and out**, never a flash: an ease-out once put
  most of a veil into four frames.
- **Nothing pops out in two frames** while something else is still moving.
- **The caption band never empties at a page change**: a page's first
  word shows at once.
- **Every cut is meant and smooth** (an owner, on a story reel cut on the
  words, 2026-10-24: "the cut points need strengthening, smoother"): a cut
  lands on the onset of the word it belongs to, or on a beat of the bed
  where no word cues it; the two shots meet: the subject's place, scale
  and brightness carry across, or change on purpose; neither shot starts
  mid-gesture or holds a frame of its source's own next shot; cuts closer
  than about half a second only in a deliberate burst.
- **No dead length** (the same owner: "some clips have extra, unneeded
  sound or length"): a bite's source ends where its last word fades into
  the room, read on the waveform, and its picture leaves on that frame;
  what follows takes over there, in the short pause before the narrator's
  next word (about 0.2 s, never more than the cut lead). Held to the next
  word's cut, the speaker is seen falling silent, drawing breath or
  starting a sentence the viewer never hears; the owner saw three to
  seven such frames on two bites and sent them back twice ("the last few
  frames of the interview and the CNN clip are still extra"). A card, a year or a number holds as long as it takes to read
  and not a beat more; a pause around a bite is the narrator's own pause
  length, not longer; a clip's own breath, room noise or a word's tail
  from the next sentence never rides in at a bite's head or end.
- **A change to the clock or to a timing rule is followed through.** A
  trimmed bite, a shortened pause or a wider beat window moves every time
  derived from it; list what moved and check each against what depends on
  it before rendering. Widening the window moved five cuts, and two
  caption pages that ended on those cuts left before their last word was
  said.

## First frame, last frame, covers

- **The first frame is complete**: the title fully set, the subject up. A
  title meant to be read on frame 0 starts its reveal at -1.0 s; a title
  still rising on frame 1 was a review blocker.
- **The first seconds catch the eye** (the owner, 2026-10-29: the very
  start and the first few seconds must grab attention, or the skip rate
  is high). Frame 0 is already a striking picture, not a plain page or a
  slow fade-in, and the picture moves or changes within the first second
  (the line starts drawing, the camera starts its move, the first mark
  lands) while the hook is spoken. The review judges frame 0 and the first
  three seconds as a stranger scrolling past would.
- **The last frame** is the end card ("Coming up" and the part, the next
  title), clean, with the bed still sounding under it. Its title is broken
  into lines by meaning, phrase by phrase, with no word alone ("Drain
  every ocean. / Where is / the longest / mountain range?"; left to wrap,
  "longest" fell alone on a line).
- **Covers never catch a fade**: after any re-timing, look at each cover
  at full size for half-transparent type or a shape mid-move.

- **A call to follow is one designed lockup.** When an end card carries
  a Follow button, the mark, the handle and the button are composed as
  one block: the button's edges flush with the handle's ink (or with the
  mark's), its corners the mark's own, the spaces between the three
  equal, measured on the ink (the mark's squares, the ascenders, the
  baseline), never on the boxes, and the block centred on the page. A tap
  reads as a phone's: a fingertip comes in, the button gives under it,
  then changes state, with a ring from the touch and a soft click in the
  mix on the touch; the button's colours for each state are the series'
  (in its layer). Options go to the owner as a short side-by-side clip
  with the sound, since a tap is judged in motion (the owner: "the whole
  page needs careful design").

## Density and pacing

- A 35 to 45 s episode is about 14 to 20 beats; a 60 s one about 24. A
  beat adds a number, a label, a highlight, a camera move or a new layer,
  on the word that names it.
- Vary the interval between beats (2 to 4 s): a metronome reads as
  boredom.
- Reveal in sequence; never dump a full slide.
- Nothing that looks broken. A line alone on an empty page for about two
  seconds, between full-frame footage, reads as a render fault to a
  viewer (the owner asked what had gone wrong there): put footage under
  it, a bright shot whose own dark area holds the line (a hall with a
  black screen, darkened, still read as "most of the screen is black"),
  darkened if at all from its first frame (`07-visual-grammars.md`, "No
  step in brightness inside a shot"). A still held where the story moves
  on reads as a frozen player: after a sound bite ends, cut to motion that
  pays it off.

## Imitating a reference reel

When the owner asks for a video in the form of a reference reel, the
reference is the specification, and it is read at every frame, never by
samples (an owner, on a first draft built from frames 0.5 s apart: "far
worse than the original"; "every 0.5 s is not nearly enough"):

- Compare each frame with the one before it, group the changes into
  events, and list every event to the frame: what appears, where, at what
  size, and how (in one frame, sliding in from an edge over a few frames,
  growing in steps, typing a word or a letter at a time). Then look at
  every event as a strip of consecutive frames.
- Copy its motion grammar exactly. Where the reference cuts layers in
  within one frame, steps a clip from small to large to full-bleed in hard
  steps, and types whole words, do the same: a default eased pop, a
  scale-fade or a letter-by-letter fade on top of it reads as a template.
- Measure what it shows as well as how: type sizes by frame width, how
  densely pictures overlap, which pictures move, how long each line holds,
  and how often something new arrives (count events per 10 s and compare).
- Read its sound the same way (`05-music-and-sound.md`, "Matching a
  reference's sound") before writing a music request.
- Write the beat-by-beat plan against the reference's own times, build
  the first part, and show it beside the reference at the same moments
  before building the rest.
- **Measure the edit against it before the first render**, not after the
  owner has watched: shots, median shot, cuts per 10 s and the longest
  hold, on both films by the same scene detection. A remade story reel
  cut at 28 shots, a 2.0 s median, 3.6 cuts per 10 s and holds of 5 to
  10 s, against a reference of 61 shots, 1.0 s and 8.4, was "far worse
  than the original" at first sight. Match its pace at least, with new
  pictures: a long bite is cut into at its phrases with a cutaway or the
  speaker's other camera, and a long stretch gets more shots of the story,
  never a quote card cut into a second card of its own line, a shot
  reframed and shown again, a picture brought back or a shot held for its
  pull cut short. One remake reached the reference's 8 cuts per 10 s by
  seven splits "from material already in the repository": four pictures
  came back, a quote card zoomed to its key line, a quote card stopped a
  sentence short, and the hook's party shot was split at a word; the owner
  sent back every one ("replace any material that repeats", "show the quote
  only once", "why isn't that line in the quote?", "don't cut it short").
  Where new material runs out, the count yields: readability, every source
  once and a shot's pull come first, and the report gives the numbers with
  the reason (that film settled at about 6.8 cuts per 10 s against the
  reference's 8, by the owner's own notes).
- **A shot that pulls is held.** A hook shot chosen for its draw on the
  audience runs its whole phrase; it is not split for pace or for a
  literal match with the words. The owner, restoring a party crowd under
  "a generation want to be founders" that a review had split at "want",
  for an audience largely of young men: "don't cut it short; it's
  eye-catching and will draw a lot of the male target audience". Held
  does not mean overstaying: it leaves as its phrase ends, not on a later
  beat ("it's a little long, cut it by 0.1 s"; it now cuts as the bed
  falls quiet before the next hit).
- **A bite is cut to the lines that carry the story.** The owner cut a
  writer's 10 s answer to its first sentence and its last ("after 'tragic
  hero' go straight to 'It wasn't my intention'"); the join is hidden on a
  picture cut.

## The finishing pass on collage footage

When a film is built from archive footage and press photos (a reel of
pictures cutting in on the drums, not a drawn explainer), these lift it
from assembled to finished; an owner asked for all of them after seeing
the edit "a level below" a reference reel:

- **A sound bite comes in over its section's pictures**, not on a page of
  its own: the speaker's band laid over the lower part of the pile, under
  the logos and the line that name the story, so the page reads as one
  thought (an owner, of a founder's bite that cut to a new black page:
  "put it over the page before it, like the other interviews, below the
  first photo's and the second photo's logos"). The pile is laid out for
  it: the pictures that carry the names high, the rest low, where the band
  will cover them.
- **One grade over every picture and clip**, not over the page or the
  type: a touch more contrast, a little less saturation, a slight warmth,
  so footage from five decades and four broadcasters reads as one film,
  while a black page stays pure black and white type pure white.
- **Film grain and a soft vignette over the frame**, the grain in overlay
  so it shows on the pictures and not on pure black or white.
- **People cut out of their press photos** (rembg with the BiRefNet
  portrait model on CPU, about 35 s an image; run one image per process, as
  a batch in one process grew past 14 GB and was killed), cropped to the
  bust and fading into the page at their foot, so they stand on nothing.
  Check every edge by eye: take a coloured backdrop's spill off the hair
  (clamp green to the larger of red and blue), crop away legs and chairs.
- **Motion blur on every move** (Remotion's `CameraMotionBlur`, 180 degree
  shutter, about ten samples, only on the frames that move, since it
  renders each of them that many times): a picture sliding in streaks in
  as a camera would see it; without it, a slide reads as drawn.
- Not upscaling: a GAN invents face detail, which is the look to avoid.

## The picture's rhythm

How busy the picture is belongs to the series as much as how fast the
narrator speaks, and the same first approved parts are its standard
(`brand.json` `rhythm.reference`). `pipeline/rhythm.py` measures the
delivered video in the picture band, between the headline and the
captions (`rhythm.band`), so the captions turning their pages never count:

- **how much of the time it moves**: frames whose change from the last,
  smoothed over five frames, is above a small threshold, which a camera
  move, a shape travelling, a fill or a line drawing all cross;
- **how many separate movements** there are per 10 s, each a run of 0.2 s
  or more;
- **how long it holds still** between them, as the median hold.

`rhythm.py standard` takes the reference parts' busiest values as the
limits and QA gates every part on them (`12-qa-gates.md`, "picture
rhythm"); `rhythm.py report episodes/<id>` prints a part against them
before it is sent. On one series' four reference parts the picture moved
at most 18 percent of the time, in at most 1.89 movements per 10 s, with
a median hold of at least 2.57 s. A part heard as rushed moved 29 percent
of the time, in 2.81 movements per 10 s, with a median hold of 2.03 s. A
change shorter than 0.2 s (a dot appearing) counts as still: counted as a
movement, one-frame blips cut long holds in two.
Four camera moves in 3 s and a half-turn whipped through in 0.55 s are
the kind of thing these measures catch: a picture that moves more often,
with less still time between. Passing them is no reason to skip looking
at each run of moves; what they add is that a picture busier than the
series' own is caught by a number before the owner has to feel it.

Before trusting a fault, list what the measure counted: `rhythm.py moves
episodes/<id>` prints every movement and hold it found, with the word
being spoken as each starts. The list names the moves to fix, all of them
at once, and it shows when a fault is the measure's own limit: a faint,
translucent shape whose slow start stays under the threshold reads as a
short hold where the eye sees a move, and that one is left as is, with
the reason written down. The measure's own rules are kept where a reading
cannot jump between runs: a threshold never sits on the grid its inputs
come in (`04-voice.md`: a pause is a gap over 0.125 s, since word timings
come in 20 ms steps), and a change under 0.2 s counts as still.

## Determinism

Everything is a pure function of the frame: no CSS transitions or
keyframe animations, no `Math.random` (use Remotion's `random(seed)`), no
three-fiber `useFrame`, no tween on wall-clock time. Two renders of one
commit on two machines must give the same frames, or a helper's render
cannot be trusted as the same video.
