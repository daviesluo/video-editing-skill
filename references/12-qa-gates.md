# 12: QA gates

Every gate runs on the real artefact: the delivered `final.mp4`, the
rendered PNG, the staged release folder. Code that should produce the
right thing is not evidence that it did. Green means every gate green;
"passes except" is a fail. The gates are necessary, never sufficient:
after them comes the independent review (`13-review-and-agents.md`).

## 1. Automated (`build.py episodes/<id> qa`)

Writes `out/qa.json` and `out/contact-sheet.png`, and exits non-zero on
any failure.

The rhythm and tone rows hold every part to the series' first approved
parts, which are the measured standard for how fast the voice speaks, how
the narrator sounds and how busy the picture is (`04-voice.md`, "Pace,
measured against the reference parts" and "Tone, measured against the
reference parts"; `08-animation.md`, "The picture's rhythm"). A part that
felt rushed beside its four reference parts was outside on every measure:
5.22 syllables a second in speech against 4.86 to 5.13, the picture moving 29
percent of the time against at most 18, 2.81 movements per 10 s against at
most 1.89, a median hold of 2.03 s against at least 2.57. Words a second
had not shown it. A take slowed into the pace range by a direction tag kept
the pace and lost the tone: the owner heard a listless opening at once, and
its pitch, its words' levels and its first sentence's level were outside.

| Check | Pass |
|---|---|
| resolution | 1080x1920 |
| video | H.264, yuv420p |
| frame rate | 23 to 60 fps |
| audio | AAC, 48 kHz |
| file size | under 300 MB |
| length | 3 s to 3 min (longer is not recommended to new viewers) |
| loudness | -14 LUFS integrated, within 1 LU, on the delivered file |
| true peak | at or under -1 dBTP, on the delivered file |
| alignment | every script word matched by the aligner (none interpolated) |
| voice pace | inside the reference parts' range (`brand.json` `rhythm.limits`, measured by `rhythm.py standard`): syllables a second within speech (pauses over 0.125 s taken out; up to 0.05 outside allowed, the alignment's own noise) and over the whole narration between their slowest and fastest, no sentence pause or section break shorter than their shortest; judged beside every earlier part with `voice.py pace-report` |
| narrator's tone | on the take, inside the reference parts' range on every measure, within `voice_tone.tolerance` (`brand.json` `voice_tone.limits`, measured by `voicestyle.py standard`): pitch median, spread and movement within sentences, the spread of the words' levels, brightness, and the hook's pitch movement and level against the take (`voicestyle.py report episodes/<id>`) |
| picture rhythm | on the delivered file, the picture band between the headline and the captions moving no more of the time than the busiest reference part, in no more separate movements per 10 s, with a median hold between movements no shorter than theirs (`rhythm.py report episodes/<id>`) |
| narration flaws | no stray sound on no word, no splice into sound, no click in a pause, silent first and last samples |
| transcript | word error rate at or under 3 percent against the script; read every listed difference by eye, because one wrong word is under 3 percent |
| facts | every fact in `episode.json` marked verified |
| fact log | every fact id has a row in `verification.md` |

## 2. Measured scans

| Gate | Command | Pass |
|---|---|---|
| orphans and safe zone | `ORPHANS=1 node scripts/stills.mjs <Comp> <dir> every:0.5` over the whole episode, and over every cover | "0 findings": no block whose last line holds one word ("ORPHAN"), no visible text outside `SAFE` ("UNSAFE"), no visible character the vendored face lacks ("GLYPH") |
| caption pages | `node --experimental-strip-types scripts/caption-pages.ts <id>` | every page read; none flagged; no phrase the eye reads as one unit split |
| music | `python pipeline/music.py check episodes/<id> <take>` on the take in use | `"passed": true` |
| sound-effect plan | the `sfx:` lines `build.py ... mix` prints | none |
| cover | `node scripts/covers.mjs` | "covers OK" |
| release text | `python pipeline/publish.py check <release>` | "text and cover OK" |

Run the orphan scan over the whole episode before every render, not only
the parts that changed: a fix in one scene moves labels in another. In
the scan the 3D globe is not drawn (`GlobeView` skips it when the
`orphans` prop is set), so a whole episode scans in minutes; the text is
laid out exactly as in the render. Its stills are for the probe, not for
looking at the picture.

## 3. The picture audit (`episodes/<id>/picture-audit.md`)

From `templates/episode/picture-audit.md`. For every sentence, the time,
its key words, what is on screen at that moment, and pass or fix, each
row checked on a still rendered at that word:

- every pointing word shows exactly its thing;
- every described change is seen happening;
- every named distance is drawn as a labelled line, on the number;
- every spoken number is on screen with what it measures;
- every "in fact" size comparison is at true size;
- the call to action is spoken and shown word for word;
- no tint left on a region the narration has moved on from;
- no paused frame shows a false number or position.

**Re-take the audit on the current timeline after any re-timing.** A
stale audit, with times from an earlier take and claims about pictures
that have since moved, reads as evidence and is not.

## 4. By eye, frame by frame

- **The contact sheet** (first frame, each segment, last frame) with the
  safe box drawn on.
- **Every scene change and camera move** in 0.03 to 0.1 s steps: no
  double exposure, no crossing movers, no pop, no flash, no empty caption
  band, no plate edge, no straight edge where a picture should continue.
- **Every map inset and card to its edges**: a flat map wider than 360°
  of longitude, or centred so that one side passes ±180°, shows a blank
  strip where its plate ends. An end card's small map, 880 px wide at 200
  px a radian, spanned 251° and showed one through two renders and two
  reviews; work out each view's span from its scale, do not trust a still
  that happened to look full.
- **The first frame complete** (title set, subject up) and **the last
  frame** a clean end card.
- **Key text** inside x 90 to 960 and y 250 to 1,230; no label collisions;
  nothing over a caption; no stray label under the end card.
- **Design, element by element**: does it look designed, and does it look
  like what it represents? A 3D thing drawn as a flat overlay fails even
  with no fault in it: a flat stroke standing for a shaft through a planet
  passed every gate and a review, and the owner rejected it at sight. So
  does the reverse: a place modelled as a 3D hole, where a dot sized for
  the view was wanted.
- **No answer before its word**: nothing on screen, or on the cover, gives
  the answer to the question being asked before the voice gives it.
- **No run of camera moves without a beat to read** between them. The
  picture-rhythm row measures it over the whole part; looking finds the
  run itself.
- **Spot-check the content**: a city on a map at its real position, a bar
  at its real length, a date at its real place on the ruler.
- **Each cover** at full size and in the 3:4 tile.
- **Listen** to the opening, each musical lift and the ending of the
  delivered file, at phone volume and on headphones, and to the whole of
  it once for pace and tone against the earlier parts: a part can pass
  every check and still sound rushed, or like another reading.

## What counts as evidence

- **Reasoning is not evidence.** A confident diagnosis stated before
  measuring has cost whole rounds. Measure the thing pointed at.
- **Closed-form arithmetic**: build a case whose right answer is known by
  hand and compare the output with it, not with another part of the same
  system.
- **Counterfactual runs**: undo the fix, re-run the check, see it fail. A
  check that passes before and after the fix proves nothing.
- **The real artefact**: read values back out of what ships.
- **A matrix, not one case**: every take, every episode touched, every
  cover.
- **Independent sources**: a fact is re-checked at its source or
  recomputed, never accepted because the research note says it.
- **Exit codes, not summary lines.**
- **A verdict computed under an old rule** is stale once the rule changes;
  re-derive it.
