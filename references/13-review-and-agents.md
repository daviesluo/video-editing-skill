# 13: Independent review, sub-agents and the fix loop

The gates find what can be measured. A review finds what a person would
notice. Nothing reaches the owner until an independent, exhaustive review
of the exact file being sent finds no blocker, and every nit worth fixing
is fixed and confirmed on that file.

## The loop

1. Build, then run every gate in `12-qa-gates.md` on the render.
2. Send the render to a reviewer with the exhaustive brief below.
3. Reproduce each blocker on the artefact before fixing it; fix every
   blocker and every nit not marked "leave as is"; answer in writing any
   finding you disagree with, with the reason.
4. Re-render, re-run every gate, and send the new render back **to the
   same reviewer** for a re-check.
5. Repeat until a pass finds nothing the owner would comment on. Only
   then send it to the owner, with one line saying what was checked.

**No rework.** A video the owner has to send back for a point a review
could have caught is a failure of this process, not a new request. A
review of an earlier render does not count once anything has changed.

**When the owner raises something new**: fix it where it was pointed at;
write the general rule into the project's standards in the same turn;
search every episode and post for the same class of problem and fix those
too. A rule written down is a rule every later review checks.

**When the owner brings another reviewer's report**, take it seriously:
apply what you agree with, disagree in writing with the reason when you
do not, and say which findings you took.

**Taste is not a bug report.** One attempt at a look the owner dislikes
is fair; if the second misses, stop and agree the target first.

## Sub-agents with standing names

Give each recurring job to a named agent and send follow-up work back to
the same one by message, so its context (the episode, the earlier
findings, the files it read) is reused instead of rebuilt. Open a new
agent only for a wholly new task, or when the old one's context is
exhausted, and then brief it from the old one's report file.

| Name | Job | When | Tier |
|---|---|---|---|
| video researcher | topic research and the fact sheet: demand evidence, primary sources, data downloads with provenance, analysis scripts | before a topic is approved; before a script | strongest model, high effort |
| video fact checker | re-verifies every claim at its source or by re-running the computation, independently of the researcher | after the script is drafted; after any wording change | strongest, high |
| video script editor | the cold read, the unslop pass, readings, spelling, the teaser chain | before voicing; before release | strongest, high |
| video designer | style frames, scene designs, covers, layout fixes proposed with exact values | before a scene is built; on any change of look | strongest, high |
| video reviewer - 1, video reviewer - 2 | the exhaustive review of a render; re-checks of its fixes | after every render that might ship | strongest, high |
| video release writer | caption, pinned comment, replies, platform text, hashtag research with its check table | once the script is final; again after any change | strongest, high |
| video chores | listing, counting, extracting frames, file moves, mechanical checks | whenever the answer is mechanical | low effort |

- **Two reviewers** so two episodes can be reviewed at once; each episode
  keeps its reviewer for its re-checks.
- **Set the model and the effort explicitly on every call**: the strongest
  model available at high effort for anything that changes what ships
  (research, fact checks, design, review, release text); low effort for
  chores. A cheap review that misses a blocker costs a full render.
- **At most three agents at a time**, a resumed one included: more
  overlap their file changes and their reports go unread.
- **A sub-agent's number is a claim until recomputed.** Recompute the
  numbers a decision rests on, and say which ones you checked.
- **Agents write their report to a file** (the scratchpad, or the
  episode's folder for a review worth keeping) and reply with a short
  summary and the path.
- **Agents never send anything to the owner, never push to the main
  branch on their own, and never post.**

The render helpers are separate standing sessions, not sub-agents; see
`11-render.md`.

## Brief templates

Fill every `<...>`. Always give paths, commit hashes and the exact file;
an agent left to find things wastes its context.

### video researcher

```text
You are "video researcher" for <repository>. Research the topic "<the question>"
for a <length> s vertical explainer (house rules: references/01-topics-and-series.md
and references/02-research-and-rights.md in the skill).

Produce episodes/<id>/research.md from templates/episode/research.md:
- demand evidence (YouTube outlier ratios with channel medians, Wikipedia
  pageviews, what could not be measured);
- the score table (C M V S D Den F) with evidence beside each score, and the
  series fit sentence checked;
- the claim table: every claim the script could use, each from a primary
  source with its exact quote, URL and date accessed, or computed by a
  script in episodes/<id>/analysis/ from a named dataset (data file table with
  version, URL, licence, download date, SHA-256);
- numbers that disagree, and which to use with what wording;
- rights for every non-drawn element; pitfalls; not verified or dropped;
- a draft script of <n> words in the shape of references/03-script.md, every
  factual sentence mapped to a claim id.
Report: the path, the three strongest facts, every claim you could not
verify at a primary source, and every figure you computed with its command.
```

### video fact checker

```text
You are "video fact checker" for <repository>. Independently verify every fact
said, shown or written for episode <id> at commit <hash>: the narration in
episodes/<id>/episode.json, every text on screen in studio/src/episodes/EpNN.tsx,
and every block of releases/to-post/<release>/post.md. Do not trust
research.md: read each source yourself, re-run each analysis script.
For each fact: the wording used, the source's exact quote or the recomputed
value, and Confirmed, Reword (with the exact new wording) or Remove. Check
rounding, units, "share" against "area", dates and calendars, and that one
quantity has one value everywhere.
Write the result into episodes/<id>/verification.md (template:
templates/episode/verification.md) and report every Reword and Remove.
```

### video script editor

```text
You are "video script editor" for <repository>. Read the script of episode <id>
(episodes/<id>/episode.json, segments) cold, as a first-time viewer who knows
nothing, line by line, against references/03-script.md:
names in full the first time; examples as recent as sources allow; complete
sentences when heard (no colon shorthand, no hanging fragment); no ambiguous
pointer; the hook and the teaser each one plain question; the teaser equal
word for word to the next episode's hook (<next hook>); the line into the
teaser following from what was shown (never a bare "So"); spelling and `say`
readings in the narrator's accent (<accent>); the unslop list; word count for
<length> s.
Report each problem as: segment id, the current words, the exact new words,
and why. Then a second pass: what would the owner still notice?
```

### video designer

```text
You are "video designer" for <repository>. Design <the scene, the cover or the
look> for episode <id> in the house style (references/06-visual-style.md and
references/07-visual-grammars.md; tokens in brand.json and
studio/src/brand/tokens.ts). Render stills with studio/scripts/stills.mjs at
<times> and look at them. For a change of look, make two or three finished
style frames, each designed to a named top-tier reference shown beside it.
Report: the stills' paths, and for each proposal the exact values (file,
component, prop, value; cue words for every reveal), and how it keeps the
safe zone, the caption band and the cover tile clear.
```

### video release writer

```text
You are "video release writer" for <repository>. Write the text for release
<release> (episode <id>) in releases/to-post/<release>/post.md from
templates/release/post.md, by references/14-release-and-publishing.md:
the caption (hook line complete in two lines, the explanation with figures,
one open question only the viewer can answer, a Sources line, three to five
hashtags), the pinned comment (the next part's question in full and the
reason to follow), the series-link comment, ready replies, TikTok and
YouTube blocks, the settings with the audio name (at most 50 characters).
Use only facts already in episodes/<id>/verification.md. Research each
hashtag on its public page and fill the Hashtag checks table. Write
apostrophes as ’. Run python pipeline/publish.py check <release> and report
its output.
```

### video reviewer: the exhaustive review

```text
You are "video reviewer - <1|2>" for <repository>. Review the render of
episode <id> at commit <full hash>: <path to final.mp4>, SHA-256 <hash>.
Check the hash first. This review must find every problem in one pass and
say exactly how to fix each one; a second round of findings that this pass
could have caught is a failure of this review.

Read first: the skill's references 03 (script), 06 to 10 (style, grammars,
animation, captions, covers) and 12 (gates), episodes/<id>/episode.json,
studio/src/episodes/EpNN.tsx, episodes/<id>/verification.md,
episodes/<id>/picture-audit.md, releases/to-post/<release>/post.md, and
<earlier review report, if any>.

Pass one, every category, in this order:
1. The script, read cold: every line as a first-time viewer hears it
   (references/03-script.md, "The script, read cold"), and the QA transcript.
2. Every audit row at its word: render or extract a still at the exact start
   of each key word and check what the row claims.
3. Every frame: extract all frames; contact sheets every 0.5 s with the safe
   box drawn; every scene change and camera move in 0.03 to 0.1 s steps.
4. Type and layout: run ORPHANS=1 stills every 0.5 s; labels on lines or
   coasts, text over subjects, collisions, anything over the captions, key
   text outside x 90 to 960 / y 250 to 1,230, stray labels under end cards.
5. Captions against the voice: list the pages; at every phrase start compare
   the caption with the voiced onset (spectrogram for disputed words).
6. Sound, measured: splice records, pauses for clicks, the bed's level over
   time, the hole test, the level under the last words and the end card,
   loudness and true peak of the delivered file; say what you could not hear.
7. Facts: every number on screen and in every text block against
   verification.md; one quantity, one value.
8. Code against the timeline: every cue in EpNN.tsx and episode.json points
   at the word it is meant for.
9. Release text: every block of post.md, the audio name, the hashtag table;
   run publish.py check.
10. The cover, at full size and in the 3:4 tile; covercheck.
11. Design quality, element by element, as well as faults: for every
    element ask "does this look designed?" (its shape, light, material,
    edges and motion chosen, nothing left at a default or drawn the quick
    way) and "does it look like what it represents?" (a 3D thing built and
    lit in the 3D scene, never a flat stroke over the render). An element
    that fails either question is a blocker, with a proposed design and,
    for a change of look, two or three options to show as stills.
Pass two: what would the owner still notice? Watch it once more as the owner
would, and add anything that a viewer would see, hear or misread.

Report in the format below to <path>/review-<short hash>.md. For every
problem: the time (video seconds), what is wrong, the evidence (a still or a
measurement, with its path), and the exact fix: file, element, value, new
wording, and what to check after. Classify each as a blocker (it must change
before the owner sees it), a nit (fix it), or "leave as is" (with the reason).
List everything you could not check; that list must be empty for the
episode to pass, except listening by ear, which you then name precisely
(times) for a person to do. Do not edit any file.
```

### The review report format

```text
# <Episode>: exhaustive review of the <short hash> render

Verdict: <ready, or not ready: N blockers>.

The render: path, SHA-256 (matches or not), duration, spec, QA result.

How it was checked: one line per category above, with what was sampled.

## A. Blockers
### B1. <time>: <what is wrong, in one line>
- What, and the evidence (paths).
- Cause, if known.
- Fix: file, element, value or wording, exactly; what to check afterwards.

## B. Nits: fix all of these except those marked "leave as is"
### N1. ...

## C. Checked and passing
One line per category, with the measurements.

## D. Earlier findings
| Earlier item | Status (fixed, not fixed, now Bn/Nn) |

## E. Cue indices confirmed against the timeline

## F. What I could not check
(Empty, or precisely what a person must do, with times.)

## Summary
The blockers in one line each, then the nits worth fixing.
```

### Re-check brief (to the same reviewer)

```text
Re-check: the fixes for your review of <old hash> are in the render at
<new hash>, <path>, SHA-256 <hash>. Confirm each of your findings is fixed on
this render (cite the still or measurement), then look at everything each fix
touched: the neighbouring scenes, every cue that moved, the caption pages,
the music around any change, the cover. Report new problems in the same
format. Do not re-review untouched parts unless a fix was broad; say which
parts you re-reviewed and why.
```
