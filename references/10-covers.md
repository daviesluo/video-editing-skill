# 10: Covers

A cover is the episode's face in the profile grid and wherever the video
is shared. It is a frozen, bare frame of the episode itself, with the
badge and the title over it, designed for the crop the grid actually
shows and checked by measurement.

## Design

- **A frozen, bare frame** (`brand/Cover.tsx`): the episode drawn with
  `bare` (picture only: no captions, no labels, no headline), full bleed,
  at the frame named by a cue and an offset (`cue: "hook$", offset: 0.2`).
  The title sits on it with the halo and the theme's light scrim, never a
  white panel, which reads as washed out.
- **The badge**: the series name and "Part N" in the accent, at x 100, y
  300.
- **The title** under it: two or three lines at 96 to 108 px, weight 880,
  one accent phrase; "|" breaks a line as in the episode's own title, so
  the cover and the video break their title alike.
- **The cover does not answer its own question** any more than the
  episode's opening does (`08-animation.md`): over a question of where
  something lies, the frozen frame shows the picture before the answer's
  evidence is drawn. It shows only what the question names (the owner,
  2026-10-29, on a cover with the finished route across the planet:
  "the cover too": the two countries alone), and its title asks the
  question ("How do you sail from Pakistan to Russia in a straight
  line?"), not the result.
- **One subject**: the route, the shapes, the circle, the bars, the page:
  marked in the episode with `data-cover-subject` so the probe measures
  it. Mark the overlay that is the subject, not a full-bleed base map.
- **The design surface is the 3:4 tile.** The profile grid shows only the
  middle 1080x1440 of a 1080x1920 cover (y 240 to 1680). Judge the cover in
  that crop, not only at 9:16.
- **The audio name** that goes with the cover is at most 50 characters
  and can be set only once (`publish.py check`).

- **A group of people is composed, not lined up.** Cut-out faces on a
  cover stand like a group photograph: a front row and a back row, heads
  at staggered heights, every face whole. Heights rising from one side to
  the other read as a ramp, and a face hidden behind another, or one the
  audience will not know, wastes the place (the owner, on a series cover:
  "staggered like before, not rising one way; it must look designed", "who
  is that, isn't he unknown? use someone like Netflix's founder").
- **Every face has its eyes open** and its mouth at rest. A speaker
  looking down between words reads as eyes closed once cut out small;
  pick the frame by comparing the footage at 0.1 s steps around the
  moments the person looks up (the owner chose a cover and then saw one founder
  "with his eyes closed").
- **Every face looks its best.** Take the person from a photograph or a
  studio-lit interview at high resolution, facing the camera or nearly,
  sharp, flattering, never from a webcam call, a news window or a soft
  frame blown up: a cut-out shows every flaw of its source. Look through
  every source of the person before choosing, and offer the best two or
  three (the owner, of a founder cut out of a webcam interview and a
  profile shot: "neither photo looks good, find others").
- **Cut-outs joined without seams.** A cut-out from a frame that cut the
  person off (a shoulder at the frame's edge) has a straight edge: place
  it where the band's own faded side or a person in front hides it, and
  check every overlap at full size. The feet fade as one group, never
  each person on their own (each one's fade let the white shirt of the
  one behind show through the one in front). Clean every cut-out before
  use: keep its largest piece, drop stray islands, pull the edge in 1 to
  2 px to lose the source's background fringe (a red line of a TV set's
  carpet on a jacket). A low-key film frame is lifted to the others'
  brightness, so no face sits in shadow beside lit ones.
- **The title is measured whole.** A title set in parts (a line, then a
  large last word) is checked as one block: the probe once measured only
  the first part, and a cover whose last word ran into the faces passed.

## The rules, checked (`pipeline/covercheck.py`)

| Rule | Why |
|---|---|
| the title inside the tile with 40 px to spare, and inside x 90 to 960 | the grid crops the rest, and the player's side crop eats the edges |
| the subject inside the tile with 40 px to spare | half a subject in the grid reads as a mistake |
| the subject starts at least 32 px under the title, never under it | type over the subject it names |
| on the bare page, what sits under the title is centred in the tile's space below it: neither gap more than 1.5 times the other, each at least 80 px | shapes bunched up under the title with an empty bottom looked unbalanced |
| a full-bleed map or picture fills the tile and keeps its subject clear of the title | |
| the title prints no markup ("\|" or "*") | a "\|" inside an accented span was printed as a bar ("Where are \| the cracks?") and no box check could see it; the probe reports the title's text |

`node scripts/covers.mjs` (in `studio/`) renders every `Cover<NN>`
composition from one bundle, measures each cover's title and subject in
the page (`kit/CoverProbe.tsx`), writes `covers/cover-NN.json` beside the
PNG and runs `covercheck.py` on them; `publish.py check` runs the same
rules on the staged cover of every release.

## Moving the picture

To move a cover's subject, use the cover's `pictureY`, which the episode
applies to its subject and overlays only (as a camera offset), so the
page and its scrims stay put; shifting the whole frame shows a band of
empty page at the top. **Masks move with the picture too**: a mask whose
edge stayed put while the picture moved once hid a city's dot on a cover,
and another cut a line short of the limb it ran to.

## Look at it

The check measures geometry, not quality. After any re-timing or scene
change, look at each cover at full size and in the tile:

- nothing mid-fade or mid-move (a cover once froze as island names faded
  out, half transparent);
- no counting or moving number (one froze a share mid-count, showing a
  value that was never true);
- the subject sharp and whole, the title balanced, nothing touching.

The cover composition is as long as the episode: Remotion clamps every
frame, frozen ones too, to the composition's range, so a one-frame
composition would always show the episode's frame 0.
