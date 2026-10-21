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
| 4 CPU cores, 15 GB RAM | | a 60 s episode with a 3D globe renders in about 27 minutes on 4 cores with no GPU; flat scenes take a few minutes |

There is usually no GPU in a cloud container. Every render passes
`--gl=swangle` (software WebGL); without it, anything drawn with WebGL
renders black or not at all.

## The commands

```sh
cp -r path/to/video-editing-skill/toolkit/. my-series/   # the project template
cd my-series && git init
sh setup.sh            # .venv, studio/node_modules, the headless browser, .env
$EDITOR brand.json     # series name, handle, avatar, palette, music licence
$EDITOR .env           # ELEVENLABS_API_KEY=... (gitignored)
.venv/bin/python pipeline/scaffold.py episode 01-first-question "Why ...?"
```

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
| `pipeline/` | `build.py` (steps), `voice.py`, `mix.py`, `music.py`, `sfx.py`, `sfxgen.py`, `qa.py`, `covercheck.py`, `publish.py`, `recue.py`, `scaffold.py`, `audition.py`, `fontwidths.py` |
| `pipeline/sfx-lib/` | sound-effect takes, several per effect (`sfxgen.py` makes them) |
| `studio/` | the Remotion project: `src/brand/` (tokens, font, cover, avatar), `src/kit/` (captions, type, bars, probes, follow beat), `src/lib/` (eases, cues, geography), `src/episodes/` (one file per episode), `scripts/` (stills, covers, caption pages) |
| `studio/public/episodes/<id>/` | `timeline.json` and `music.mp3` (committed); `voice.wav` (committed with `git add -f` only for the shipping take) |
| `episodes/<NN-slug>/` | `episode.json`, `music-plan.json`, `research.md`, `verification.md`, `picture-audit.md`, `analysis/` (scripts that compute figures), `out/` (gitignored renders, mix, QA) |
| `covers/` | `cover-NN.png` and its measured layout `cover-NN.json` |
| `releases/to-post/<release>/` | what will be posted, exactly, at full quality |
| `releases/posted/<date>-<release>/` | the same folder once live, with its link |
| `templates/` | what `scaffold.py` copies for a new episode or release |

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
  filled a disk.
- `pkill -f <pattern>` matches the shell running it when the command line
  contains the pattern, and kills it. Kill by process id.
- Check exit codes, not summary lines: a run once printed "passed" and
  exited 1.
- Vendor every asset the render needs (fonts, images, data) under
  `studio/public/` and pin every package version: a render must never
  fetch anything, or two renders of one commit can differ.
