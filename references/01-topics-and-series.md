# 01: Topics and series planning

A series is a promise: the same kind of question, answered to the same
standard, often enough to be worth following. Topic choice decides more
of an episode's reach than anything done to it afterwards, so it is
researched, scored and approved before any production starts.

## One everyday question per episode

- **One question, asked the way a curious person would ask it.** "Why do
  flights curve on a map?", "Why did one month in 1752 have 19 days?",
  "Why are shipping containers all one size?" A question the viewer has
  half-wondered about beats a fact they never asked for, because the
  hook is then their own curiosity.
- **One concrete thing, not a chain of concepts.** The question and its
  answer must make sense with nothing explained first. Count the ideas a
  viewer must hold before the answer lands (time zones, then UTC, then
  midnight moving west, then the date line, then "where people live"):
  more than one or two and the opening is lost, however exact. "How many
  dates can it be on Earth at once? Three, for one hour a day" passed the
  research, the script edit and a full review, and the owner found its
  first 35 seconds very confusing; the same material, told as "two islands
  120 km apart are a whole day apart", needs one idea (a line between
  them) and shows it. Prefer the concrete case to the general count.
- **The answer must be shown, not just told.** Score how well the
  medium answers it: a map, a chart, a timeline, a document or a
  diagram that makes the answer visible. A topic whose answer is only
  talk over generic pictures fails this test.
- **Answer early, then go one layer deeper than the viewer expects,
  then pay off** with a number, a reveal or a comparison worth sending to
  someone. People share the payoff, not the premise.
- **Density.** A new verified fact or visual beat every 2 to 3 seconds.
  A topic that cannot carry that many checkable facts in 60 seconds is a
  slow one.

## Demand evidence, measured

Measure; do not guess what will travel.

- **Outlier ratio on YouTube.** Search the topic; for the top short and
  long results, take the uploading channel's median views over its latest
  40 uploads in the same tab (Shorts or Videos). Ratio = the video's views
  ÷ that median. A ratio of 5 or more across several channels means the
  topic, not the channel, carried the views. Caveats to state with the
  number: tab counts are rounded, medians are of recent uploads, very
  small channels give meaningless ratios, and most evidence is long-form.
- **Perennial interest.** Wikipedia pageviews of the topic's article over
  the last twelve months (Wikimedia REST API, user agents only), against
  comparators the series already knows.
- **Recent hits in the niche, each time topics are chosen.** Look at what
  has travelled lately in the same niche on Instagram Reels, TikTok and
  YouTube Shorts (the last few weeks; accounts of the series' size and a
  few above it): which questions, formats and openings carried the views.
  Use them for inspiration and as demand evidence, with the links and the
  counts the pages show, never as material to copy; a fact already viral
  this month scores lower on novelty (the owner of one series asked for
  this, 2026-10-28).
- **How to read them without a login** (worked 2026-10-28 from a cloud
  machine): Instagram's topic pages (`instagram.com/popular/<tag>/`, a
  dozen reels each) render in a headless browser; each reel's public
  embed (`/reel/<code>/embed/captioned/`) carries its owner, views, likes,
  comments and caption, and an account's embed (`/<account>/embed/`) its
  latest posts; a reel's date is in its shortcode (base64 to the media
  id; `(id >> 23) + 1314220021721` is milliseconds since 1970). Reddit
  refuses its pages and JSON to such machines but serves RSS:
  `/r/<sub>/top/.rss?t=month`, and `/r/todayilearned/search.rss?q=...
  &restrict_sr=1&sort=top&t=month` for stories people did not know.
  Keep the scripts in the project and the reading in a dated topic note.
- **What could not be measured is listed.** Short-video platforms rarely
  expose view counts to a script; say so rather than inventing a figure.

## Scoring

Each criterion 1 to 5; keep the table, with the evidence beside each
score, in the series' topic file.

| Code | Criterion |
|---|---|
| C | curiosity gap: would someone stop scrolling for this question? |
| M | how well the medium answers it (map, chart, timeline, document, diagram) |
| V | verifiability: primary sources, or computable by us from public data |
| S | shareability: "send this to the friend who…" |
| D | demand evidence, as measured above |
| Den | density: a new verified fact every 2 to 3 s across the length |
| F | fit with the series: the same family as the episodes so far, not a repeat |

**Fit is a gate, not a bonus.** In a growth phase a series that wanders
between themes loses the followers it has: a map series that drifts into
history told over a map, or a business series that drifts into celebrity
gossip, is two half-series. Write the series' test in one sentence ("the
map or globe itself is the explanation and the surprise") and check every
topic against it before work starts. Off-theme episodes are shelved, not
deleted, for a later phase.

**Risk flags** go in the table too: politics, disputed borders, living
people, health claims, a myth that the episode could accidentally repeat.

## The series plan

- **Order for momentum.** The strongest hooks and the closest family
  first; alternate visual types (globe and flat map, chart and document)
  so consecutive episodes do not look alike; no two similar stories back
  to back; check each pair for repetition.
- **The teaser chain.** Each episode ends on the next one's question. The
  teaser's wording is the next episode's hook, word for word, and the next
  episode's hook is then voiced in exactly those words: a viewer who
  followed for that question must hear it asked the same way.
- **The line into the teaser follows from what was just shown.** Never a
  bare "So" (it reads as a non sequitur); "And you may wonder…" or a
  sentence that hands the last picture to the next question.
- **Open loops.** The teaser names a concrete, answerable question, not a
  topic: "dig straight down into the Earth: where would you come out on
  the other side?", not "next time: antipodes". It states the question in
  full with something concrete to look forward to, and may be a little
  longer for it: "What if we drained the ocean?" sounded odd and promised
  nothing, where "Drain every ocean, and the longest mountain range on
  Earth appears. Where is it?" names the surprise and still asks. Being
  the next hook word for word, its fact is verified and logged before the
  episode that says it ships, like any other.
- **The end line.** Every episode ends its content with one line over
  the profile and the Follow tap: "Enjoy stories like this? Follow for
  part N: <the next hook, word for word>." The next part's title
  rises above the profile on the question's first word, where the
  episode's own picture was, and nothing moves into a header. Viewers
  leave the moment this line begins, so it is short and comes last.
- **Reserves.** Keep two ready topics, scored and researched, in case a
  planned one fails its fact check.

## Before production

Put the plan to the owner with: the question, the hook, the view (what
picture answers it), the score with evidence, the fit sentence, the
risks, and the teaser chain. Production starts on approval. When the
owner says "research it and decide", decide, apply it, and report what
was decided and why; do not hand the question back.
