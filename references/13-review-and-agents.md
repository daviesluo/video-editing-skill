# 13: Independent review, sub-agents and the fix loop

The gates find what can be measured. A review finds what a person would
notice. Nothing reaches the owner until an independent, exhaustive review
of the exact file being sent finds no blocker, and every nit worth fixing
is fixed and confirmed on that file.

## The loop

1. Build, run the pre-render pass (`11-render.md`, "Before the full
   render") until it finds nothing, render once, then run every gate in
   `12-qa-gates.md` on the render.
2. Send the render to a reviewer with the exhaustive brief below.
3. Reproduce each blocker on the artefact before fixing it; fix every
   blocker and every nit not marked "leave as is"; answer in writing any
   finding you disagree with, with the reason. A fix the reviewer proposes
   is a claim like any number: work it out on the timeline before using it
   (one proposed end time was said to clear a card's arrival and did not),
   and check that it brings no fault of another class (a map hidden under
   a veil, as asked, faded with the veil and crossed the card that came
   in). Fix every finding of a round together, then render once.
4. Re-render, re-run every gate, and send the new render back **to the
   same reviewer** for a re-check.
5. Repeat until a pass finds nothing the owner would comment on. Only
   then send it to the owner, with one line saying what was checked.

**No rework.** A video the owner has to send back for a point a review
could have caught is a failure of this process, not a new request. A
review of an earlier render does not count once anything has changed.
Nor is a finding shipped because time ran out: a blocker or a nit worth
fixing that survives to release is the same failure. One part went out
the night it was due with a whip pan, a tick of a shaft left on a
planet's edge and, found only once it was live, a border line flashing
across the frame; the owner's answer was that problems like these must
never appear again. When the owner wants to publish by a time, the review
starts early enough for its fix round, re-render and re-check to fit
before it; a deadline moves the review earlier, never the bar lower.

**When the owner is waiting to publish**, everything goes into that one
deliverable until it ships. Other work may run (a review of another
episode), but its reports are filed, not acted on, until then. Tell the
owner promptly when a background step finishes (a render, a review),
even when the next step has already started.

**When the owner raises something new**: fix it where it was pointed at;
write the general rule into the project's standards in the same turn;
search every episode and post for the same class of problem and fix those
too. A rule written down is a rule every later review checks. When the
fault traces to a standard the owner had already given, say so plainly,
and fix the rule or the check that let it through as well as the episode:
a standard that did not catch its own case is not yet written well
enough.

**What the owner approved stays.** A later pass that rebuilds the film
does not reach into a section the owner has approved: an owner asked four
times for approved pages back ("why change it, the earlier version was
good"). An approved section is restored from the commit the owner saw,
rect for rect; a reviewer's finding against it, or a new rule it seems to
break, goes to the owner as a proposal with stills before anything is
rebuilt, and only faults (a flash, a cut word, a wrong fact) are fixed
unasked.

**When the owner withdraws a request** ("forget I said it, render as
before"), undo it cleanly: revert the trial, prove the tree is back where
it was (the files' hashes, or `git diff` against the commit before the
trial, empty), commit nothing of it, and say so in one line. A later
finding that touches what the owner asked for and withdrew goes back to
the owner to decide, rather than being fixed unasked.

**When the owner brings another reviewer's report**, take it seriously:
apply what you agree with, disagree in writing with the reason when you
do not, and say which findings you took.

**When the owner says it is still wrong**, answer with a new measurement
of the thing pointed at, not a defence of the old result. Layout words are
literal: "delete" means gone, not hidden, and "split into two lines" means
each item on its own line; where an instruction can be read two ways, the
reading that moves things apart is the intended one. Fix what was pointed
at and its class of problem, and nothing the owner did not point at. "Go
with your recommendations" still means every recommendation is researched
and verified before it is used.

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
| video researcher | topic research and the fact sheet: demand evidence, primary sources, data downloads with provenance, analysis scripts | before a topic is approved; before a script | the main session's model, high effort |
| video fact checker | re-verifies every claim at its source or by re-running the computation, independently of the researcher | after the script is drafted, and again once the release text exists (a first pass run before it left the ready replies unchecked, and two of them were wrong); after any wording change | the same model, high effort |
| video script editor | the cold read, the unslop pass, readings, spelling, the teaser chain | before voicing; before release | the same model, high effort |
| video designer | style frames, scene designs, covers, layout fixes proposed with exact values | before a scene is built; on any change of look | the same model, high effort |
| video reviewer - 1, video reviewer - 2 | the exhaustive review of a render; re-checks of its fixes | after every render that might ship | the same model, high effort |
| video release writer | caption, pinned comment, replies, platform text, hashtag research with its check table | once the script is final; again after any change | the same model, high effort |
| video chores | listing, counting, extracting frames, file moves, mechanical checks | whenever the answer is mechanical | the same model, low effort |

- **Two reviewers** so two episodes can be reviewed at once; each episode
  keeps its reviewer for its re-checks.
- **Set the model and the effort explicitly on every call**: the main
  session's own model (the strongest available) for every agent, at high
  effort for anything that changes what ships (research, fact checks,
  design, review, release text) and at low effort for chores. Never a
  smaller model: a cheap review that misses a blocker costs a full
  render. An agent opened before a rule changed finishes the task in
  hand; new work goes to an agent opened under the rule, briefed from the
  earlier agent's report file.
- **At most three agents at a time**, a resumed one included: more
  overlap their file changes and their reports go unread.
- **A usage limit stops every agent mid-task**, and the render helpers
  with them. Record in the ledger what each was doing when it stopped;
  once the limit resets, resume each by message with its task, rather
  than spawning new ones that would rebuild their context.
- **A sub-agent's number is a claim until recomputed.** Recompute the
  numbers a decision rests on, and say which ones you checked.
- **Agents write their report to a file** (the scratchpad, or the
  episode's folder for a review worth keeping) and reply with a short
  summary and the path. Frame dumps and stills made for a review are
  deleted once the report is written: they run to hundreds of megabytes.
- **Never poll from the main session.** Waiting on a render, a helper or
  a long check goes to a background script that wakes the session only
  when there is a result, or to the chores agent; quiet wake-ups that find
  nothing spend the budget the reviews need.
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
names in full the first time; every example, study and figure as recent as
sources allow (its year noted; an old one only with the research's reason
that nothing newer is as solid); complete
sentences when heard (no colon shorthand, no hanging fragment); no ambiguous
pointer; the hook and the teaser each one plain question; the end line one
breath, "Follow for part N:" then the next episode's hook word for word
(<next hook>), nothing after it; the line into the
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
Check the hash first, then that the render is still current: list the
commits after <full hash> (`git log --stat <hash>..HEAD`) and confirm none
touches studio/src/episodes/EpNN.tsx, the shared kit and lib, brand.json,
or this episode's timeline, voice, music or episode.json; and that the
staged video.mp4 and cover.png match the render and covers/cover-NN.png
(SHA-256 and pixels). This review must find every problem in one pass and
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
   Rhythm against the reference parts: run `voice.py pace-report
   episodes/<id>` and `rhythm.py report episodes/<id>` and compare
   syllables a second (within speech and overall), the shortest sentence
   pause and section break, and the picture's moving share, movements per
   10 s and median hold with the reference parts; a part outside their
   range is a blocker even when every other check passes (one at 5.22
   syllables a second in speech, its picture moving 29 percent of the time
   in 2.81 movements per 10 s, did, and was heard as rushed). The tone
   too: run `voicestyle.py report episodes/<id>`, and listen to the
   opening beside a reference part's; a take outside their tone is a
   blocker (one slowed by a direction tag opened listless, and the owner
   heard it at once).
2. Every audit row at its word: render or extract a still at the exact start
   of each key word and check what the row claims.
3. Every frame: extract all frames; contact sheets every 0.5 s with the safe
   box drawn; every scene change and camera move in 0.03 to 0.1 s steps;
   each camera move's speed against its sibling moves (a half-turn four
   times faster than its twin is a whip pan); any scene change made of
   several short moves, or any run of camera moves with no beat to read
   between them; anything that shows the answer to the question being
   asked before the voice gives it, in the episode or on the cover; any
   element left after its scene, or brought back by a fade; every plate
   edge and every flat map view's span worked out from its scale.
4. Type and layout: run ORPHANS=1 stills every 0.5 s; labels on lines or
   coasts, text over subjects, collisions, anything over the captions, key
   text outside x 90 to 960 / y 250 to 1,230, stray labels under end cards.
5. Captions against the voice: list the pages; at every phrase start compare
   the caption with the voiced onset (spectrogram for disputed words; pass:
   within 0.1 s).
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
    for a change of look, two or three options to show as stills. The
    case to measure yourself against: a flat 2D stroke standing for a 3D
    shaft through a planet passed every gate and this review, and the owner
    rejected it at sight. Judge what each element is, not only whether it
    has a fault; and the reverse too: a modelled hole where a place
    wanted a dot sized for the view.
Pass two: what would the owner still notice? Watch it once more as the owner
would, and add anything that a viewer would see, hear or misread.
Then a comprehension pass: watch it as a first-time viewer with no
background, and write in one plain sentence what that viewer has
understood after each section. Any section where that sentence cannot be
written, or a line that needs a second hearing, is a blocker: the owner
found a part's first 35 seconds confusing, and one of its lines
("Sliding due west keeps every place on its own latitude") impossible to
follow, after they had passed the script edit and two full reviews.

Report in the format below to <path>/review-<short hash>.md. For every
problem: the time (video seconds), what is wrong, the evidence (a still or a
measurement, with its path), and the exact fix: file, element, value, new
wording, and what to check after. Classify each as a blocker (it must change
before the owner sees it), a nit (fix it), or "leave as is" (with the reason).
List everything you could not check. Only listening by ear may appear,
named precisely (the times) for a person to do; the episode passes only
when the main session has had that listen done and recorded it in the
review file, so the list is empty when the episode ships. Do not edit any
file.
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
