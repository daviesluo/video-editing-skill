---
name: video-editing
description: >-
  End-to-end production of short-form vertical explainer videos (Instagram
  Reels, TikTok, YouTube Shorts; 1080x1920, 30 to 75 seconds) to a
  post-ready standard: topic and series planning, research and data with
  provenance, fact verification, script, synthetic narration with exact
  word timing, a composed music bed and sound effects, animation in
  Remotion in a light, restrained house style, word-by-word captions,
  covers, rendering on standing helper sessions, automated QA gates, one
  exhaustive independent review by named sub-agents, the fix loop, release
  staging and the read-back after posting. Load it before choosing a
  topic, writing a script, a scene, a voice or music request, a render, a
  review or a release for any short explainer video, on any subject:
  maps and geography, business, history, literature, science. Works on
  Claude Code, Cursor, Codex or any tool with a shell.
---

# Short-form explainer videos, post-ready

Copyright 2026 Zheng Luo (Davies Luo). Licensed under the Apache
License 2.0, whose text is the LICENSE file beside this one. Keep this
line when you copy the file.

Version 1.0, October 2026. Copies of this file drift once they are
pasted into other repositories, so check this line against the
source, https://github.com/daviesluo/video-editing-skill, before
trusting a copy you did not install yourself.

This skill makes faceless explainer videos for vertical short-form
platforms: one everyday question per episode, answered with code-drawn
maps, charts, timelines, documents and type over a synthetic narrator,
in 30 to 75 seconds. The bar is the top of the market, dense (a new
verified fact or visual beat every 2 to 3 seconds) and exact. It must
look and sound like a high-budget production made by people.

**Post-ready** means the person who commissions the video, called the
owner below, finds nothing to fix. Not "close", not "one or two notes":
nothing. Everything here exists to make that true on the first showing.

`references/` holds one file per stage, with the depth this page leaves
out; `toolkit/` is a working copy of the pipeline and the studio, which a
new project starts from (`references/00-setup.md`). Read the reference
for a stage before doing that stage.

## The loop, and the rule that governs it

```
topic → research → script → voice → music → scenes → captions → cover
      → pre-render pass → render once → QA gates → exhaustive review
      → fix everything → re-render → gates → re-check … until a pass
      finds nothing → release → owner
```

- **Nothing reaches the owner before an independent, exhaustive review
  of the exact file being sent finds no blocker**, and every nit worth
  fixing has been fixed and confirmed on that file. A review of an earlier
  render does not count once anything has changed. A video the owner has
  to send back for a point a review could have caught is a failure of the
  process, not a new request.
- **Measure, do not reason.** A gate runs on the real artefact (the
  delivered MP4, the rendered PNG, the staged folder). A fix is proved by a
  check that fails without it. A number from a sub-agent is a claim until
  recomputed. A measure that gates is made robust first (no threshold on
  its inputs' grid), and before a fault it reports is trusted, what it
  counted is listed.
- **Find everything, then render once.** Every check that can run on
  stills, on the timeline or on the audio runs before the first full
  render, and everything it finds is fixed in one round; a render that
  finds one fault, then another, then another is the back and forth this
  skill exists to end. The same holds for every fix round after a review.
- **The first parts the owner approves are the measured standard for the
  voice's pace and tone and for the picture's rhythm, enforced by QA.**
  They are listed in `brand.json`, measured by `rhythm.py standard`
  (syllables a second and the shortest pauses of the voice; how much of
  the time the picture moves, how often, and how long it holds still) and
  `voicestyle.py standard` (the narrator's pitch, its movement, the words'
  loudness, brightness and the opening line's energy), and every later
  part is kept inside their range. A part can pass every other check and
  two reviews and still be heard as rushed, or as another reading; this
  is the gate that catches it.
- **Every requirement the owner states becomes a written standard in the
  project, in the same turn**, and every episode and post is searched for
  the same class of problem and fixed too. A rule written down is a rule
  every later review checks. A fault that traces to a standard already
  given is said to be one, and the rule or check that let it through is
  fixed with it. A request the owner withdraws is reverted cleanly,
  proved unchanged, and said so.
- **Send each finished deliverable as soon as it passes**, on its own,
  with one line saying what was checked. Do the whole job without being
  asked twice; ask only when two readings of a request lead to genuinely
  different work, and then once, with what each reading would build.

## The pipeline

### 0. Set up: `references/00-setup.md`

Copy `toolkit/` into a new repository, run `sh setup.sh`, put the series
name, handle, avatar, palette and music licence in `brand.json` and the
key in `.env` (never in the repository or a chat). Prove the machine
renders with the example episode before any real work. Keep a ledger in
the project (what remains, machine setup, history) so a fresh session can
resume from the repository alone.

### 1. Topic and series: `references/01-topics-and-series.md`

- One everyday question per episode, whose answer the picture shows.
- Demand measured (YouTube outlier ratios, Wikipedia pageviews), scored
  on curiosity, medium, verifiability, shareability, demand, density and
  **fit with the series**, which is a gate: a series that wanders between
  themes in its growth phase loses the followers it has.
- Order for momentum, alternating visual types. Each episode's teaser is
  the next episode's hook, word for word. Approved by the owner before
  production.

### 2. Research, data and rights: `references/02-research-and-rights.md`

- Primary sources, or our own computation by a script from a named
  dataset with its version, URL, licence, download date and SHA-256;
  re-running the script reproduces every figure.
- `research.md` (the fact sheet: claims with exact quotes, numbers that
  disagree and which to use, rights, pitfalls) and `verification.md`
  (every fact said, shown or written, re-checked, as worded). QA fails on
  any fact not verified or not logged.
- Round only where the source rounds; one quantity, one value everywhere.
- A rights basis for every image, document, quote, logo, clip and track
  before it is used, with its credit line; when unsure, draw it instead.

### 3. Script: `references/03-script.md`

- Length planned at about 2.3 to 2.4 words a second: 70 for 30 s, 105
  for 45 s, 140 for 60 s. The pace itself is held to the reference parts
  in syllables (Voice, below).
- Hook (the question, in full, in the first 1.5 s, over a picture that
  catches the eye from frame 0 and moves within the first second: the
  first seconds decide the skip), answer by 6 s, two or
  three layers, a payoff worth sending, then one end line that asks for
  the follow and says the next part's hook in the same breath ("Enjoy
  stories like this? Follow for part N: <the next hook>"): viewers leave
  the moment a follow line begins, so no second sentence, no promise and
  no "Next, in part N" come after it.
- **Read cold** before voicing and before release: names in full the
  first time, recent examples, complete sentences when heard (no colon
  shorthand), no ambiguous "it", one plain question in the hook and the
  teaser, a teaser with something concrete to look forward to, the line
  into the teaser following from what was shown (never a bare "So"),
  connectives that carry each turn when heard ("Actually,", "And",
  "However,"). The owner's awkward wording is offered back with natural
  phrasings, and the owner picks.
- Numbers written as on screen, read through `say` in the narrator's
  accent; spelling in the narrator's variety; an unslop pass.

### 4. Voice: `references/04-voice.md`

- ElevenLabs, one request per episode (`build.py <ep> voice`), a fixed
  seed, then **forced alignment** (`build.py <ep> realign`) and the
  fricative-onset correction, because synthesis timings run up to 250 ms
  late.
- Choose among several seeds by measurement: the transcript reads as
  written, the pitch falls where a sentence ends, the length suits the
  cut (`voice.py measure`).
- A changed sentence is re-voiced alone (`voice.py replace`), from a
  pause, cut only in true silence, every splice recorded and checked.
  No stray sound, breath fragment or click, ever (`qa.voice_flaws`).
- **Pace and tone are gates, against the reference parts** (the rule
  above): the pace in syllables a second, within speech and overall, and
  the shortest sentence pause and section break, measured before the
  render and in QA and printed beside every earlier part (`voice.py
  pace-report`); the tone on the take (`voicestyle.py report`). The voice
  is never slowed in post, and never with a direction tag (both are
  heard: a `[slowly]` tag kept the pace and made the opening listless). A
  take is chosen from many untagged seeds: those inside the tone first,
  then the slowest of them, then its pauses lengthened in silence for the
  overall pace (`voice.py pace`, which moves the word timings with the
  silence, no re-alignment), and the music re-made.

### 5. Music and sound: `references/05-music-and-sound.md`

- One composed bed per episode in the house sound (felt piano, pizzicato
  strings, a quiet cello pedal), chunk boundaries on segment starts, a
  continuous pulse from the first beat, a held final chord through the end
  card (`tail_s`, `end_fade_s`).
- Two or more seeds, each through `music.py check` (holes, seams, the
  hold under the end card, clarity band, onsets, vocals); the best that
  passes is used and its licence recorded.
- Ducked under speech to about 15 LU below the voice; final -14 LUFS and
  -1 dBTP on the delivered file. Effects few, under the voice, never the
  same sample twice running.

### 6. Visual style and grammars: `references/06-visual-style.md`, `references/07-visual-grammars.md`

- Light, fresh and restrained, contrast carried by lightness; one face
  (Archivo, normal width), sentence case; small type at least 29 px with a
  tight halo; colour by role (accent the subject, cool the comparison,
  warn the misconception).
- **Every detail is designed**, nothing drawn the quick way: each element
  gets its own pass on shape, light, material, edges and motion; anything
  that stands for a 3D thing is built and lit in the 3D scene, never a
  flat stroke over the render, and only what is truly 3D is (a marked
  place is a dot sized for the view); a change of look is explored in a
  lab composition, reviewed over several rounds, and shown as two or three
  options on stills with a recommendation, the owner's pick made before
  rebuilding.
- A flat map view's span is worked out from its scale and kept inside its
  plate; a detail plate fades out before its own edge.
- No boxes, chips, rules, separators, arrows, glow or counting numbers;
  headlines revealed word by word from a mask; a light grain over every
  frame.
- The full 9:16 height; text inside the safe zone **measured on the real
  player** (x 90 to 960, y 250 to 1690, clear of the button column);
  badge close under the top bar; captions low.
- A grammar for each kind of content: maps and globes, charts and stat
  cards, timelines, archival photographs and documents, quotes and book
  text, companies and logos, science diagrams.

### 7. Animation: `references/08-animation.md`

- **The picture follows the words**: whatever the narration points at
  happens on screen on that word, and nothing answers a question before
  the voice does.
- An opening map framed wide enough to place the story, then a designed
  move in; after each camera move a beat to read before the next; a
  change of scene is one continuous move, not short stop-start moves; a
  camera move is judged by its speed against its sibling moves.
- A headline says what the voice says, in its words, and starts on its
  own first word; a label that names a change appears with the change;
  an end-card title is broken into lines by meaning, no word alone.
- Reveals lead their word by about 0.2 s with the enter ease; camera moves
  use the move ease; nothing moves without a reason.
- The picture no busier than the reference parts (the rule above): no more
  of the time moving, no more movements per 10 s, no shorter median hold
  (`rhythm.py report`); four camera moves in 3 s and a half-turn in
  0.55 s are the kind of thing it catches.
- Every time is a word cue (`seg@k`), never a second; `recue.py` after any
  wording change.
- A line and its label come and go together; nothing over the captions;
  scenes sequenced, not cross-dissolved, when they collide; an element
  drawn only while its scene is; what gives way tied to the arrival of
  what replaces it, never to the whole window; the first frame
  complete.

### 8. Captions: `references/09-captions.md`

- Word by word in place, the spoken word in the accent, timed from the
  forced alignment.
- Pages of up to three words on one line, never a word alone inside a
  phrase, a number kept with its next word, kept phrases whole even across
  a comma, set at 92 to 80 percent rather than strand a word. List every
  page and read it (`caption-pages.ts`).

### 9. Cover: `references/10-covers.md`

- A frozen, bare frame of the episode with the badge and title; the
  design surface is the 3:4 grid tile (y 240 to 1680).
- Measured and checked (`covers.mjs`, `covercheck.py`): title inside the
  tile and the safe band, subject clear under it and balanced in the space
  below. Then looked at, at full size: nothing caught mid-fade.

### 10. Render: `references/11-render.md`

- **The pre-render pass, then one render.** Before the first full render:
  the cold read, the take's pace and tone, caption pages, stills at every
  audit word and through every scene change, the text scan, covers, every
  camera move and scene change listed from the code against the rhythm
  standard, the code searched for the known fault classes, the music and
  release checks. Everything found is fixed together. A quick
  low-resolution preview is a first look at the rhythm, not its gate (one
  read a median hold of 4.1 s where the full render read 2.92 s).
- Then the render: H.264, CRF 16, yuv420p, `--gl=swangle`, concurrency 1
  or 2, muted picture muxed with the mix.
- Parallel renders go, where the platform has remote sessions, to two
  standing helper sessions, **"video render helper - 1" and "video render
  helper - 2"**, reused by message for every
  render, briefed with the full commit hash, pushing `final.mp4` to an
  orphan branch `render/<NN>-<short hash>` and reporting its SHA-256.
- One episode can be split across both helpers (`RENDER_FRAMES=a-b`):
  each brief names the full hash, the part's frame range and the frame
  count expected, each part comes back with its SHA-256, and `build.py
  <ep> join` checks that the parts meet and add up to the composition
  before joining without re-encoding. Every seam is compared with stills
  of the frames either side. A part is kept from an earlier commit only
  when the change provably leaves its frames as they were (a moved end
  time once almost left eight frames out of step at a seam), and a kept
  part is compared with fresh stills of the new commit every 0.5 s.
- An interrupt sent to a helper by mistake is followed at once by a
  message: its background render survives, and nothing reports it.
- Only the music changed: remux the new mix under the rendered picture.

### 11. QA gates: `references/12-qa-gates.md`

All of these, on the delivered file, every time:

- `build.py <ep> qa`, sixteen checks: spec, every rendered frame
  delivered, loudness (-14 LUFS ±1) and
  true peak (≤ -1 dBTP), every word aligned, the voice and picture at the
  reference parts' rhythm and the narrator at their tone, no narration
  flaws, transcript word error rate ≤ 3 percent with every difference
  read, every fact verified and logged;
- the orphan and safe-zone scan every 0.5 s over the whole episode and
  every cover prints nothing; for a film cut from footage, every face
  measured against the player's crops (`facecrop.py`) passes;
- the picture audit, re-taken on this timeline, every row checked on a
  still at its word;
- the caption pages listed and read;
- the music check, the cover check, the release check;
- the contact sheet and every scene change read frame by frame; the
  opening, each lift and the end listened to.

### 12. Exhaustive review and the fix loop: `references/13-review-and-agents.md`

- The render goes to **"video reviewer - 1"** (or "- 2") with the
  exhaustive brief: one pass over every category (the script read cold,
  every audit row at its word, every frame (its samples offset half a
  step from the main session's own scan), type and layout, captions
  against the voice, sound and music measured, facts, cues against the
  timeline, release text, cover, the voice's pace and tone and the
  picture's rhythm against the reference parts, and
  design quality: "does this look designed, and does it look like what it
  represents?", judged even where nothing is a fault, and strength: the
  weakest shot, line and bite of each section and what would replace
  it), then a second pass asking **"what would the owner still
  notice?"**, which walks every note the owner has given on the series
- Every problem with its time, evidence and exact fix (file, element,
  value, wording); blockers, nits, and "leave as is" with reasons; a "could
  not check" list that must be empty (listening aside, which a person does
  before sending).
- Fix everything, re-render, and send it back to the same reviewer, who
  confirms each fix and looks at what each fix touched. Repeat until a pass
  finds nothing. A fix the reviewer proposes is worked out on the timeline
  before it is used.
- Review early: when the owner wants to publish by a time, the review
  starts early enough for its fix round to fit. No finding ships for lack
  of time.

### 13. Release, posting and read-back: `references/14-release-and-publishing.md`

- Stage before review: `publish.py stage <release> <commit>` copies the
  masters in, records the commit and SHA-256, writes the text files from
  `post.md`, and `check` lints them: apostrophes ’, no tells, no mention of
  how it was made, three to five researched hashtags with their check
  table, a question ending the caption, a Sources line, a pinned comment
  that invites a follow, an audio name of at most 50 characters, the
  platform's AI label as the owner decides (stated in the settings), the
  cover design.
- The owner gets one pack: the posting guide, the video, the cover, and
  the text in the message. Post from the original file, never a draft.
- After posting, read the live post back and compare it with the release
  folder, then record it (`publish.py done`). Performance notes after a
  day or two feed the next topic.

### The failure catalogue: `references/15-failure-catalogue.md`

Every rule above, with the real failure that produced it and where it is
checked now. Read it before a review.

## Sub-agents

Recurring jobs go to named agents, reused by message so their context is
not rebuilt each time; a new one only for a wholly new task.

| Name | Job | Tier |
|---|---|---|
| video researcher | topics, fact sheets, data with provenance | the main session's model, high effort |
| video fact checker | every claim re-verified independently | the same model, high effort |
| video script editor | the cold read, unslop, readings | the same model, high effort |
| video designer | style frames, scenes, covers with exact values | the same model, high effort |
| video reviewer - 1, video reviewer - 2 | the exhaustive review and re-checks | the same model, high effort |
| video release writer | post text, hashtags with their checks, replies | the same model, high effort |
| video chores | listing, counting, frames, file moves | the same model, low effort |
| video render helper - N (standing remote sessions, `11-render.md`) | render a frame range at a named commit, push it, report its hash and frame count; nothing else | a smaller, cheaper model at low effort (the owner, 2026-10-23): they only run commands, and every part they return is checked here by its SHA-256, its frame count and stills at its seams |

Every agent runs on the main session's own model, never a smaller one:
high effort for anything that changes what ships, low effort only for
chores. The render helpers are the one exception to the model: a
smaller one at low effort. An agent opened before a rule changed finishes the task in hand;
new work goes to an agent opened under the rule. At most three at a time.
A usage limit stops them all mid-task: record what was running in the
ledger and resume each by message once it resets. While the owner waits
to publish, everything goes into that deliverable, other reports are
filed until it ships, and the owner hears promptly when a background step
finishes. Agents write reports to files, never message the
owner, never post and never push to the main branch on their own. The
briefs and the report format are in `references/13-review-and-agents.md`.

## The project's own layer

This skill leaves the series' own values to the project: its name and
account, voice, palette, measured safe zone, helper sessions, music
licence, and the owner's own decisions and posting habits. Keep them in
one file beside this skill (for example `SERIES.md` next to `SKILL.md`),
with where each came from, and read it with this skill. Where the two
differ, the project file wins for its own series; a rule that would hold
for any series belongs here instead.

## Where things live

| Path | What |
|---|---|
| `brand.json` | series name, handle, avatar, palette, safe zone, layout, cover tile, release limits, music licence |
| `episodes/<NN-slug>/` | `episode.json` (segments, cues, facts, readings, caption keeps, voice and music records), `music-plan.json`, `research.md`, `verification.md`, `picture-audit.md`, `analysis/`, `out/` |
| `studio/src/episodes/EpNN.tsx` | the episode's scenes |
| `studio/src/kit/` | captions, type, bars, map view, globe view, printed sheet, cut-away 3D object, document, quote, timeline, logo, probes, follow beat |
| `studio/src/lib/` | eases, cues, geography, projections, plates, the globe's geometry |
| `studio/public/episodes/<id>/` | the committed take, timeline and music |
| `studio/public/textures/` | the globe textures and map plates, built by `textures.py fetch` and not committed; `SOURCES.md` records where each source came from |
| `covers/` | covers and their measured layouts |
| `releases/to-post/`, `releases/posted/` | release folders |
| `pipeline/` | the Python steps |

## Commands

Run from the project root with the pipeline's environment active
(`. .venv/bin/activate`, which `setup.sh` creates), or write
`.venv/bin/python` for `python`.

```sh
python pipeline/textures.py fetch                            # globe textures and map plates, once
python pipeline/scaffold.py episode 07-slug "Why ...?"      # new episode files and its scene file
python pipeline/build.py episodes/07-slug voice             # one request, the whole narration
python pipeline/voice.py replace episodes/07-slug <seg> <first> <last> [seed]   # re-voice one phrase
python pipeline/voice.py add-line episodes/07-slug <seg> [seed]                  # voice an added line
python pipeline/rhythm.py standard                          # measure the reference parts into brand.json
python pipeline/rhythm.py report episodes/07-slug           # voice and picture against them
python pipeline/rhythm.py moves episodes/07-slug            # every movement and hold it counted, with its word
python pipeline/voicestyle.py standard                      # the reference parts' tone into brand.json
python pipeline/voicestyle.py report episodes/07-slug [take.wav]   # a take's tone against them
python pipeline/voice.py pace-report episodes/07-slug       # pace beside every earlier part
python pipeline/voice.py pace episodes/07-slug              # short pauses to the reference parts' pauses
python pipeline/build.py episodes/07-slug realign           # forced alignment
python pipeline/build.py episodes/07-slug captions          # keeps into the timeline
python pipeline/music.py retime|make|check|use episodes/07-slug ...
python pipeline/recue.py episodes/07-slug studio/src/episodes/Ep07.tsx <seg> "<old text>" --apply
cd studio && node --experimental-strip-types scripts/caption-pages.ts 07-slug
cd studio && ORPHANS=1 node scripts/stills.mjs Ep07 /tmp/scan every:0.5
cd studio && node scripts/covers.mjs
python pipeline/build.py episodes/07-slug mix|render|mux|qa|remux
RENDER_FRAMES=0-1012 python pipeline/build.py episodes/07-slug render   # one part
python pipeline/build.py episodes/07-slug join              # the parts, checked to meet and to add up
python pipeline/scaffold.py release 09-reel-slug 07-slug
python pipeline/publish.py stage|text|check|done|when ...
```

## Disclosure

The narration and music are synthetic. Each platform's AI label is the
owner's call, made on that platform's current policy, read and dated in
the release, and stated in its settings ("AI label: on" or "off"). Read
in October 2026: TikTok's AI-generated content label exempts generic
text-to-speech that is no real person's voice; Meta asks for its label on
"photorealistic video or realistic-sounding audio that was digitally
created or altered"; YouTube's "altered or synthetic content" lists
AI-generated music. Put the policy in front of the owner once; then
follow the decision on every post (one owner chose off on Instagram and
TikTok, 2026-10-23). Text on screen
and in the caption never says how the video was made. A generated
reconstruction, if one is ever used, is marked "AI reconstruction" on
screen and always labelled.
