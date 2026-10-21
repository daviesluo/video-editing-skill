# video-editing

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0-brightgreen.svg)](#version)
[![Self-test](https://img.shields.io/badge/self--test-67%20cases-brightgreen.svg)](#install-and-invoke)
[![Tools](https://img.shields.io/badge/runs%20on-Claude%20Code%2C%20Cursor%2C%20Codex-lightgrey.svg)](#requirements)

An agent skill that makes short-form vertical explainer videos (Instagram
Reels, TikTok, YouTube Shorts; 1080x1920, 30 to 75 seconds) end to end,
to a standard where the person who commissioned the video finds nothing
to fix: topic, research with provenance, fact verification, script,
synthetic narration timed to the word, a composed music bed, animation in
Remotion, captions, cover, render, QA gates, one exhaustive independent
review, the fix loop, release staging and the read-back after posting.
It ships with the working pipeline and studio a project starts from.

## The problem

An AI session can produce a plausible explainer in an afternoon. The gap
between plausible and post-ready is where the time goes: captions a
quarter of a second late, a breath fragment left at a splice, a label
over a caption for six frames, a number that was rounded the wrong way, a
music bed that stops dead under the last word, a badge hidden under the
platform's top bar, an apostrophe that arrives as the wrong quote mark.
Each is small; together they make a video look made by a machine, and a
reviewer who has to point them out one round at a time stops trusting
the pipeline. This skill writes down every one of those failures as a
rule with a check, and puts a single exhaustive review between the render
and the person who has to approve it.

## How it works

![The owner sits at the top: they commission the series, approve each
release, and see nothing before a review of that exact file finds nothing.
The first row, MAKE, runs left to right through eight stages: topic (one
question), research (primary sources), script (read cold), voice
(force-aligned), music (a composed bed), scenes (which follow the words),
captions (word by word) and cover (designed for the 3:4 grid tile); every
fact is verified and logged, and every time is a word cue, never a second.
From the cover an arrow drops into the second row, PROVE, which runs right
to left: render (stills first, then the video, on the two standing helper
sessions "video render helper - 1" and "- 2"), then the QA gates
(loudness, alignment, stray sounds, facts, the orphan and safe-zone scan,
the picture audit), then the exhaustive review (every category in one
pass, with exact fixes, by "video reviewer - 1" or "- 2"). A red loop runs
from the review back to the render: anything found is fixed, re-rendered
and re-checked by the same reviewer. Only when a pass finds nothing does a
green arrow lead down to the third row: release staged (text and cover
checked, hash recorded), the owner approves and posts from the original
file with the AI label on, and the live post is read back and compared
with the folder. Under all three rows sits the project repository, where
every step leaves its record: episode.json, research.md, verification.md,
picture-audit.md, the committed take and timeline, covers, release folders
and a ledger. At the bottom, the named sub-agents reused by message:
video researcher, fact checker, script editor, designer and release
writer at the strongest model and high effort, the two reviewers likewise,
and video chores at low effort, at most three at a time.](pipeline.svg)

**The loop.** Make, prove, ship. Nothing reaches the owner until an
independent review of the exact file being sent, by SHA-256, finds no
blocker and every nit worth fixing is fixed on that file. A review of an
earlier render does not count once anything has changed.

**The house style.** Light, fresh and restrained, contrast carried by
lightness; one typeface in sentence case; no boxes, chips, arrows, glow or
counting numbers; the full 9:16 height with text kept out of the area the
platform's interface covers, measured on the real player; every detail
designed, and anything that stands for a 3D thing built in the 3D scene.
The style is fixed and the content is not: the skill gives a visual
grammar and rights rules for maps and globes, charts, timelines, archival
photographs and documents, quotes and book text, companies and logos, and
science diagrams.

**The checks.** Thirteen automated gates on the delivered file
(loudness, true peak, alignment, stray sounds and clicks in the
narration, transcript against script, facts verified and logged, the
spec), a scan of every on-screen text every half second for orphan words
and the safe zone, a picture audit that checks what is on screen at every
key word, caption pages listed and read, a music check (holes, seams, the
held ending), a cover check in the grid tile, and a release text lint.

**The review.** A named sub-agent reviews every category in one pass
(the script read cold, every audit row at its word, every frame, type and
layout, captions against the voice, sound measured, facts, release text,
cover, design quality), then asks what the owner would still notice, and
reports every problem with its exact fix and an empty "could not check"
list. The same reviewer confirms the fixes.

## What is in here

| File | What it is |
|---|---|
| `SKILL.md` | The skill, and the file a session reads first: the definition of post-ready, the pipeline in fourteen stages, the sub-agent roster, where things live, the commands. |
| `references/` | One file per stage, with the depth: setup, topics, research and rights, script, voice, music and sound, visual style, visual grammars by genre, animation, captions, covers, render, QA gates, review and sub-agents (with every brief), release and posting (with the posting guide), and the failure catalogue. |
| `toolkit/` | The project template: `pipeline/` (build, voice with re-voicing and alignment, mix, music, sound effects, QA, cover check, release staging, cue moving, scaffolding), `studio/` (the Remotion project: tokens, captions, kinetic type, bars, the orphan and cover probes, the follow beat, a small example episode), `templates/` (episode, research, verification, picture audit, music plan, release text), `brand.json`, `setup.sh`, pinned `requirements.txt` and `package.json`. |
| `.claude/skills/video-editing/SKILL.md`, `.agents/skills/video-editing/SKILL.md` | Two identical pointers carrying `SKILL.md`'s own front matter, which make the skill load on every tool that scans either path, from one copy of the skill. |
| `EXAMPLE.md` | One finding's whole life: the review row, the fix, the re-check, the rule it left behind. |
| `bin/selftest.sh` | Checks the package (pointers, references, links), its hygiene (no address, key, session id or model identifier, plus an optional private deny-list), that the toolkit builds, and the pipeline's and studio's pure functions on cases with known answers. Prints its own counts. |
| `pipeline.svg` | The diagram above. |
| `LICENSE`, `NOTICE`, `CITATION.cff` | Apache 2.0, the notice that travels with it, and how to cite it. |

## Install and invoke

Clone this repository and open it with your tool: the two pointers sit at
the paths the tools scan, and both name the same `SKILL.md`.

| Tool | Path it scans | Invoke |
|---|---|---|
| Claude Code | `.claude/skills/video-editing/SKILL.md` | `/video-editing` |
| Cursor | `.agents/skills/video-editing/SKILL.md` | `$video-editing` |
| Codex and other `AGENTS.md` tools | the same `.agents` path | `/video-editing` |
| A tool that scans neither path | one line in `AGENTS.md` naming `SKILL.md` | the model reads the file |
| Anything else with a shell | none | paste `SKILL.md` in as the session's briefing |

**To use it in a project of your own,** copy this folder in at a path the
tool does not scan, add one pointer at the path it does scan (copy one of
the two shipped ones and fix its relative path), and delete the two that
came with the folder. Then start the project from the toolkit:

```sh
cp -r path/to/video-editing-skill/toolkit/. my-series/
cd my-series && sh setup.sh
$EDITOR brand.json .env
```

`references/00-setup.md` has the rest, including how to prove the
machine renders with the example episode before any real work.

Check the package on your machine:

```sh
sh bin/selftest.sh
```

It finishes in about ten seconds. The pipeline tests need numpy, soundfile
and Pillow (`pip install -r toolkit/requirements.txt`, or point `PYTHON`
at a Python that has them); the studio tests need Node 22.18 or newer;
the type-check needs `npm ci` in `toolkit/studio`. A step whose tools are
missing is reported as skipped, never as passed.

## Using it

1. Plan the series with the owner: scored topics, the teaser chain.
2. For each episode, follow `SKILL.md`'s stages in order, reading each
   stage's reference first, and hand recurring work to the named
   sub-agents.
3. Render on the standing helper sessions, run every gate, send the render
   to a reviewer, fix everything it finds, and repeat until a pass finds
   nothing.
4. Stage the release, send the owner one pack, and read the live post back
   once it is up.

## What it does not do

It does not post anything. Every post is made by the owner, from a staged
folder, after approval; any automation that runs an account is held to
the same rule. It does not choose a voice or a look for the owner: it
renders the options and measures them. It does not replace legal advice
on rights; it keeps a record of every element's basis and avoids anything
whose basis is unclear.

## Requirements

A shell and git; Python 3.12 with the packages in
`toolkit/requirements.txt`; Node 22.18 or newer; ffmpeg with the
rubberband filter; Remotion's headless browser (`npx remotion browser
ensure`); an ElevenLabs key on a plan whose terms allow commercial use of
voice, music and sound effects. No GPU: renders use software WebGL. Four
cores render a 60 s episode with a 3D globe in about half an hour, and
flat scenes in a few minutes.

## Version

**1.0, October 2026. First release.**

WHAT IS IN IT. The skill in fourteen stages with a reference for each, the
exhaustive review brief and its report format, the briefs for every named
sub-agent and the render helpers, the posting guide, a failure catalogue
of every rule's origin, the working toolkit with a small example episode,
and a self-test that exercises the package and the toolkit's pure
functions.

WHERE IT HAS RUN. Written from the production of a series of 50 to 70
second explainers, posted as they were finished, where every rule here was
paid for by a render that broke it. The numbers quoted (the safe zone,
the timing errors, the music thresholds) were measured there.

Licensed under the Apache License 2.0, whose text is the `LICENSE` file
in this folder. Copyright 2026 The video-editing-skill authors.
