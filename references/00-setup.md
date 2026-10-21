# 00: Setup

How to make a machine able to run the whole pipeline, and how a project
built on this skill is laid out. Read once per machine; a fresh container
needs the commands again, because it keeps nothing.

## What the machine needs

| Need | Version tested | Why |
|---|---|---|
| Python | 3.12 | the pipeline (`toolkit/pipeline/`); 3.13 works for the pipeline itself, but some optional speech packages do not build on it |
| Node | 22.18 or newer | Remotion, and the studio's TypeScript run directly with type stripping |
| ffmpeg and ffprobe | any recent build with `rubberband` | decoding, loudness, mixing, muxing; `rubberband` slows a slightly short music bed without changing its pitch |
| Chrome Headless Shell | the one `npx remotion browser ensure` downloads | rendering; no system browser is used |
| An ElevenLabs key | a plan whose terms allow commercial use of voice, music and sound effects | voice, forced alignment, music, sound effects |
| 4 CPU cores, 15 GB RAM | | with no GPU, the example (54 s, a map plate and a 5 s globe beat) renders in about 9 minutes on 4 cores; an episode with a 3D globe on screen for most of 60 s took about 27 minutes |

There is usually no GPU in a cloud container. Every render passes
`--gl=swangle` (software WebGL); without it, anything drawn with WebGL
renders black or not at all.

## The commands

```sh
cp -r path/to/video-editing-skill/toolkit/. my-series/   # the project template
cd my-series && git init
sh setup.sh            # .venv, studio/node_modules, the headless browser, textures, .env
. .venv/bin/activate   # every python command below runs in it
$EDITOR brand.json     # series name, handle, avatar, palette, music licence
$EDITOR .env           # ELEVENLABS_API_KEY=... (gitignored)
python pipeline/scaffold.py episode 01-first-question "Why ...?"
```

`setup.sh` ends by running `pipeline/textures.py fetch`, which downloads
the public-domain sources of the globe and the map relief (NASA Earth
Observatory's GEBCO-based elevation and bathymetry, and Natural Earth's
10m land, lakes, glaciers, ice shelves and borders; about 65 MB), checks
or records each file's SHA-256 in `studio/public/textures/SOURCES.md`, and
builds the globe textures and the relief plates in
`studio/public/textures/`. The textures are not committed: they rebuild
exactly from the recorded sources. `SKIP_TEXTURES=1 sh setup.sh` leaves it
for later; `--width 8192` builds the globe for a close zoom, and
`--satellite` adds NASA's Blue Marble. A new plate is one row in `PLATES`
in `textures.py` and a projection in `studio/src/lib/projections.ts`.

**A new episode.** `scaffold.py episode` writes `episodes/<id>/` (spec,
music plan, research, verification log, picture audit) and the scene file
`studio/src/episodes/EpNN.tsx` from `templates/scene/EpNN.tsx`, and prints
the lines that register it: an import and an entry in `EPISODES` in
`studio/src/episodes/index.ts`, and an import and a `<Composition
id="EpNN" …>` in `studio/src/Root.tsx`. Add its cover to `COVERS` there
(`10-covers.md`). Build the scenes from the example's beats
(`studio/src/episodes/Example.tsx`). `build.py episodes/<id> voice` must
run before the composition can bundle: its length comes from the
timeline, which also carries the lead-in and tail that `build.py` copies
from `episode.json` (`audio_lead`, `tail`), so the render, the stills and
the covers all time the episode the same way.

Then, to prove the machine renders before any real work:

```sh
cd studio
node --experimental-strip-types scripts/caption-pages.ts 00-example
ORPHANS=1 node scripts/stills.mjs Example /tmp/scan every:0.5   # prints "0 findings"
node scripts/covers.mjs                                            # "covers OK"
```

The example episode (`episodes/00-example`, composition `Example`) has a
committed timeline with even word timings and no voice, so it renders with
no key. `build.py episodes/00-example voice` with `VOICE_PROVIDER=kokoro`
gives it a local test voice if the optional `kokoro` package is installed.
Without a key or `kokoro`, the example proves stills, covers and the
picture render (`build.py episodes/00-example render`), not the mix or
QA: `mix` stops and says there is no narration.

## Keys and secrets

A key never goes in the repository, in a chat, in a commit message or in
a log line. Two routes are supported by `pipeline/voice.py`:

- `ELEVENLABS_API_KEY` in the environment or in `.env` (gitignored; copy
  `.env.example`). In a cloud session, put it in the environment's secrets,
  not in a file.
- A relay that holds the key server-side and forwards a short allowlist of
  calls (`ELEVENLABS_PROXY_URL` and `ELEVENLABS_PROXY_TOKEN`), for a
  container that must never see the key itself. The relay stores only a
  hash of its token.

## Project layout

| Path | What |
|---|---|
| `brand.json` | the one file a series edits: name, handle, promise line, avatar, palette, safe zone, layout, cover tile, release limits, music licence. The studio and every check read it |
| `pipeline/` | `build.py` (steps), `voice.py`, `mix.py`, `music.py`, `sfx.py`, `sfxgen.py`, `qa.py`, `covercheck.py`, `publish.py`, `recue.py`, `scaffold.py`, `audition.py`, `fontwidths.py`, `textures.py` (with `globetex.py` and `reproject.py`) |
| `pipeline/sfx-lib/` | sound-effect takes, several per effect (`sfxgen.py` makes them) |
| `studio/` | the Remotion project: `src/brand/` (tokens, font, cover, avatar), `src/kit/` (captions, type, bars, map view, globe view, printed sheet, cut-away 3D object, document, quote, timeline, logo, probes, follow beat), `src/lib/` (eases, cues, geography, projections, plates, the globe's geometry, sizes for the view), `src/episodes/` (one file per episode), `src/lab/` (lab compositions for exploring a design, such as `CutAwayLab`), `scripts/` (stills, covers, caption pages, design variants, plate grids) |
| `studio/public/textures/` | the globe textures and relief plates, built by `textures.py fetch`, gitignored; `SOURCES.md` (committed) records each source's URL, licence and SHA-256 |
| `studio/public/episodes/<id>/` | `timeline.json` and `music.mp3` (committed); `voice.wav` (committed with `git add -f` only for the shipping take) |
| `episodes/<NN-slug>/` | `episode.json`, `music-plan.json`, `research.md`, `verification.md`, `picture-audit.md`, `analysis/` (scripts that compute figures), `out/` (gitignored renders, mix, QA) |
| `covers/` | `cover-NN.png` and its measured layout `cover-NN.json` |
| `releases/to-post/<release>/` | what will be posted, exactly, at full quality |
| `releases/posted/<date>-<release>/` | the same folder once live, with its link |
| `templates/` | what `scaffold.py` copies for a new episode (with its scene file) or release |

Keep the root grouped and readable: a new kind of file goes into one of
these folders, never loose at the root, because a root that grows by
accretion stops telling a newcomer where anything is.

## Installing the skill itself

The skill is `SKILL.md` and `references/`. Tools find it through a pointer
at the path they scan (`.claude/skills/video-editing/SKILL.md` for Claude
Code, `.agents/skills/video-editing/SKILL.md` for Cursor, Codex and tools
that read `AGENTS.md`). The repository's README has the install table.

## Keeping the work alive across sessions

A production runs for days and outlives any one session. Keep a ledger in
the project: what remains, the machine setup as runnable commands, and a
newest-first history of what was done and why, committed with the work.
A fresh session then resumes from the repository alone. The render
helpers and sub-agents in this skill report into the same record.

## Housekeeping that bit before

- `stills.mjs` and `covers.mjs` delete their bundle (about 100 MB each in
  the temporary folder) when they finish; a day of stills left behind
  filled a disk. A render leaves its own bundle (`/tmp/remotion-*`), and
  frame dumps and per-review stills run to hundreds of megabytes: delete
  them when their report is written, and check `df -h` before a render,
  because a full disk stops a render part-way.
- `pkill -f <pattern>` matches the shell running it when the command line
  contains the pattern, and kills it. Kill by process id.
- Check exit codes, not summary lines: a run once printed "passed" and
  exited 1.
- Vendor every asset the render needs (fonts, images, data) under
  `studio/public/` and pin every package version: a render must never
  fetch anything, or two renders of one commit can differ. Textures too
  large to commit are built from sources whose SHA-256 is recorded.
- While a render or any background job writes into the tree, stage only
  the paths the commit is about: `git add -A` once swept a half-written
  file into an unrelated commit.
- Times in the ledger come from `date -u`, never from memory; estimated
  times were later read as evidence.
- A refactor of shared kit is proved by rendering the same frames before
  and after it and comparing pixels (a maximum difference of 0).
