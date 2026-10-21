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
      → stills → render → QA gates → exhaustive review → fix → re-render
      → gates → re-check … until a pass finds nothing → release → owner
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
  recomputed.
- **Every requirement the owner states becomes a written standard in the
  project, in the same turn**, and every episode and post is searched for
  the same class of problem and fixed too. A rule written down is a rule
  every later review checks.
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

- About 2.5 words a second: 75 for 30 s, 110 for 45 s, 145 for 60 s.
- Hook (the question, in full, in the first 1.5 s), answer by 6 s, two or
  three layers, a payoff worth sending, the follow beat, the teaser.
- **Read cold** before voicing and before release: names in full the
  first time, recent examples, complete sentences when heard (no colon
  shorthand), no ambiguous "it", one plain question in the hook and the
  teaser, the line into the teaser following from what was shown (never a
  bare "So").
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
  flat stroke over the render; a change of look is shown as two or three
  options on stills and one picked before rebuilding.
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
  happens on screen on that word.
- Reveals lead their word by about 0.2 s with the enter ease; camera moves
  use the move ease; nothing moves without a reason.
- Every time is a word cue (`seg@k`), never a second; `recue.py` after any
  wording change.
- A line and its label come and go together; nothing over the captions;
  scenes sequenced, not cross-dissolved, when they collide; the first
  frame complete.

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

- Stills first (`stills.mjs`), then the render: H.264, CRF 16, yuv420p,
  `--gl=swangle`, concurrency 1 or 2, muted picture muxed with the mix.
- Parallel renders go, where the platform has remote sessions, to two
  standing helper sessions, **"video render helper - 1" and "video render
  helper - 2"**, reused by message for every
  render, briefed with the full commit hash, pushing `final.mp4` to an
  orphan branch `render/<NN>-<short hash>` and reporting its SHA-256.
- Only the music changed: remux the new mix under the rendered picture.

### 11. QA gates: `references/12-qa-gates.md`

All of these, on the delivered file, every time:

- `build.py <ep> qa`: spec, loudness (-14 LUFS ±1) and true peak (≤ -1
  dBTP), every word aligned, no narration flaws, transcript word error rate
  ≤ 3 percent with every difference read, every fact verified and logged;
- the orphan and safe-zone scan every 0.5 s over the whole episode and
  every cover prints nothing;
- the picture audit, re-taken on this timeline, every row checked on a
  still at its word;
- the caption pages listed and read;
- the music check, the cover check, the release check;
- the contact sheet and every scene change read frame by frame; the
  opening, each lift and the end listened to.

### 12. Exhaustive review and the fix loop: `references/13-review-and-agents.md`

- The render goes to **"video reviewer - 1"** (or "- 2") with the
  exhaustive brief: one pass over every category (the script read cold,
  every audit row at its word, every frame, type and layout, captions
  against the voice, sound and music measured, facts, cues against the
  timeline, release text, cover, and design quality: "does this look
  designed, and does it look like what it represents?"), then a second
  pass asking **"what would the owner still notice?"**
- Every problem with its time, evidence and exact fix (file, element,
  value, wording); blockers, nits, and "leave as is" with reasons; a "could
  not check" list that must be empty (listening aside, which a person does
  before sending).
- Fix everything, re-render, and send it back to the same reviewer, who
  confirms each fix and looks at what each fix touched. Repeat until a pass
  finds nothing.

### 13. Release, posting and read-back: `references/14-release-and-publishing.md`

- Stage before review: `publish.py stage <release> <commit>` copies the
  masters in, records the commit and SHA-256, writes the text files from
  `post.md`, and `check` lints them: apostrophes ’, no tells, no mention of
  how it was made, three to five researched hashtags with their check
  table, a question ending the caption, a Sources line, a pinned comment
  that invites a follow, an audio name of at most 50 characters, the AI
  label on, the cover design.
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

Every agent runs on the main session's own model, never a smaller one:
high effort for anything that changes what ships, low effort only for
chores. An agent opened before a rule changed finishes the task in hand;
new work goes to an agent opened under the rule. At most three at a time. Agents write reports to files, never message the
owner, never post and never push to the main branch on their own. The
briefs and the report format are in `references/13-review-and-agents.md`.

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
python pipeline/build.py episodes/07-slug realign           # forced alignment
python pipeline/build.py episodes/07-slug captions          # keeps into the timeline
python pipeline/music.py retime|make|check|use episodes/07-slug ...
python pipeline/recue.py episodes/07-slug studio/src/episodes/Ep07.tsx <seg> "<old text>" --apply
cd studio && node --experimental-strip-types scripts/caption-pages.ts 07-slug
cd studio && ORPHANS=1 node scripts/stills.mjs Ep07 /tmp/scan every:0.5
cd studio && node scripts/covers.mjs
python pipeline/build.py episodes/07-slug mix|render|mux|qa|remux
python pipeline/scaffold.py release 09-reel-slug 07-slug
python pipeline/publish.py stage|text|check|done|when ...
```

## Disclosure

The narration and music are synthetic. Each platform's disclosure is
answered from its current policy, read and dated in the release: on
Instagram the "AI label" is on; YouTube's "altered or synthetic content"
lists AI-generated music, so it is answered Yes; TikTok's AI-generated
content label exempts generic text-to-speech that is no real person's
voice, so it follows the owner's reading of that policy. Text on screen
and in the caption never says how the video was made. A generated
reconstruction, if one is ever used, is marked "AI reconstruction" on
screen and always labelled.
