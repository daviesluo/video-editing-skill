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

- **Sequence, do not cross-dissolve, when two scenes would collide.** The
  outgoing scene is gone before the incoming one starts; a map fading in
  over a card for 0.1 s is a double exposure.
- **Two moving things never cross**: a card settles before the profile
  rises under it.
- **Dissolves are eased in and out**, never a flash: an ease-out once put
  most of a veil into four frames.
- **Nothing pops out in two frames** while something else is still moving.
- **The caption band never empties at a page change**: a page's first
  word shows at once.

## First frame, last frame, covers

- **The first frame is complete**: the title fully set, the subject up. A
  title meant to be read on frame 0 starts its reveal at -1.0 s; a title
  still rising on frame 1 was a review blocker.
- **The last frame** is the end card ("Coming up" and the part, the next
  title), clean, with the bed still sounding under it.
- **Covers never catch a fade**: after any re-timing, look at each cover
  at full size for half-transparent type or a shape mid-move.

## Density and pacing

- A 35 to 45 s episode is about 14 to 20 beats; a 60 s one about 24. A
  beat adds a number, a label, a highlight, a camera move or a new layer,
  on the word that names it.
- Vary the interval between beats (2 to 4 s): a metronome reads as
  boredom.
- Reveal in sequence; never dump a full slide.

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

## Determinism

Everything is a pure function of the frame: no CSS transitions or
keyframe animations, no `Math.random` (use Remotion's `random(seed)`), no
three-fiber `useFrame`, no tween on wall-clock time. Two renders of one
commit on two machines must give the same frames, or a helper's render
cannot be trusted as the same video.
