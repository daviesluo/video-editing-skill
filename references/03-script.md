# 03: Script

The script is heard once, at speed, by someone who knows nothing about the
subject and is deciding every second whether to scroll on. Every sentence
must be understood on that one hearing. The script lives in
`episode.json` as segments with ids; scenes, sound and captions key off
those ids and their word numbers.

## Length

The narrator in the house style speaks about 2.3 to 2.4 words a second
over the whole narration, pauses included, which is enough to plan a
script's length. The pace itself is held to the series' reference parts
in syllables, not words, since a script of short words reads fast in
words alone (`04-voice.md`, "Pace, measured against the reference
parts").

| Length | Words |
|---|---|
| 30 s | 65 to 72 |
| 45 s | 100 to 108 |
| 60 s | 135 to 145 |
| 75 s | 170 to 180 |

Shorter holds more of the audience; go long only when the story carries
it. Write slightly under the target: scripts run long when voiced.

## Shape

1. **Hook** (0 to 1.5 s): the question, in full and in plain words, on
   screen from frame 1 and spoken in the first second and a half, over the
   strongest picture already up.
2. **Answer** by about 6 s.
3. **Two or three layers**, each a new verified fact on a new picture.
4. **Payoff**: the number, reveal or comparison worth sending to someone,
   on the story's own subject. A neat fact from beside the story stays
   out, however recent: a film about founders ended on its 2026 sequel's
   box office, and the owner cut it ("the sequel has nothing to do with
   startups, don't mention it"); it ends on what the founders did.
5. **The end line**, one breath (`cta` segment): "Enjoy stories like
   this? Follow for part N: <the next episode's hook, word for word>."
   The insights of a series' first six parts showed why: the
   retention curve fell from about a quarter of the viewers to about 5%
   on the very word "Enjoy", while the likes peaked on that question; a
   follow line followed by a ten-second teaser was watched by almost no
   one and counted against the average watch percentage of every view.
   So the question stays, the teaser rides in the same breath (the owner
   kept it in full: "the voice stays as before"), the promise ("a new
   one every day") and "Next, in part N" go, and the payoff sits as late
   as it can before it.

Segment ids are short words (`hook`, `newyork`, `payoff`, `cta`)
because cues read `newyork@7`.

## The script, read cold

Read the script as a first-time viewer who knows nothing, line by line,
before voicing and again before release. Every point below is one a
finished, checked episode failed:

- **Every name in full the first time**: "the International Space
  Station", not "the space station"; no jargon a general viewer must
  decode ("the lower 48" becomes "the United States without Alaska and
  Hawaii").
- **Examples and studies as recent as primary sources allow.** Examples
  from twenty years ago sound dated when newer ones exist, and so does a
  study: a part that said "in a 1981 study" passed the script edit and two
  reviews, and the owner asked at once whether there was nothing newer.
  Note the year of every example, study and figure in the research; an old
  one stays only when a search for a newer one found nothing as solid, and
  the research says so.
- **Complete sentences when heard.** No colon shorthand where a listener
  needs the verb: "The biggest overlap: China on Argentina." becomes "The
  biggest overlap is China on Argentina." No hanging fragment: "over 400
  tonnes" becomes "which is over 400 tonnes".
- **No ambiguous pointer.** Every "it", "this", "that", "here", "these"
  points at one thing, and that thing is on screen when the word is said
  (`08-animation.md`). Name the thing when two could be meant ("closer to
  Point Nemo", not "closer to it").
- **The hook and the teaser ask the question in full**, and are heard as
  one question: "Where would you come out, on the other side?" was voiced
  as two questions because of its comma.
- **The teaser gives something concrete to look forward to**, and may run
  a little longer for it: "What if we drained the ocean?" sounded odd and
  promised nothing; "Drain every ocean, and the longest mountain range on
  Earth appears. Where is it?" names the surprise and still asks
  (`01-topics-and-series.md`, "Open loops"). Its fact is verified and
  logged like any other.
- **Connectives carry the turns when heard.** On the page a new paragraph
  shows a turn; heard, only the words do. "Actually," leads into a claim
  wider than the last, "And" into a second example, "However," into the
  correction. Without them a correction runs on as one more item in a
  list. Each is voiced as part of its line (`04-voice.md`), and the line
  must still sound natural read aloud.
- **The next part's hook matches the teaser that promised it**, word for
  word.
- **The line into the teaser follows from what was just shown.** Never a
  bare "So"; "And you may wonder…" or a sentence that hands the last
  picture to the next question.
- **Plain physical words, never the technical description of a method.**
  Say what was done to the picture as a viewer would say it: "Europe only
  moved sideways, never up or down. It really is this far north", not
  "Sliding due west keeps every place on its own latitude", which the
  owner, who commissioned the part, could not follow. Test each sentence:
  could a 12-year-old repeat it back after one hearing? If not, rewrite
  it, and offer the owner the plain version.
- **Nothing a viewer could misread or have to replay.** If a sentence
  can be read two ways, rewrite it; do not rely on the picture to settle
  it.
- **The evidence is the strongest there is, and it is a fact, not a
  hint.** A line that backs a claim gives the hardest proof available, in
  this order: a primary figure (the company's own filing, a dataset), a
  dated first-hand account, then the rest; never an aside that only
  implies it. "Back then, many people started on the web at Yahoo. Even
  their own paper said so." (the founders' paper mentioning Yahoo in
  passing) was "very weak supporting evidence" to the owner; it became
  "65 million page views a day.", Yahoo's own figure from its annual report
  filed weeks before the pitch, shown as the filing with the number swept.
- **A kicker never claims "ever", "first" or "only" where a popular story
  contradicts it**, even an unsupported one: the viewer who knows it hears
  the payoff as wrong. Date the claim instead ("The first price Google
  named, in 2002?" for "The first price Google ever named to Yahoo?", which
  a widely repeated, unsourced "$1 million in 1997" would answer).
- **Wording the owner gives is used as given**, in the voice, the
  captions and the post text alike. Where it reads awkwardly in English,
  offer it back first with one or two natural phrasings that keep its
  meaning, and the owner picks: "almost all only in the state" became
  "almost all of it in the state alone".

## Numbers and spelling

- **Write numbers the way they should appear on screen** ("2,688
  kilometres", "87%", "800 km²"): captions show the script's own words.
- **Every number of three or more digits, every year, every decimal and
  every symbol goes in `say`**, keyed by accent, with the reading that
  matches the narrator: British "two thousand six hundred and
  eighty-eight", "two thousand and one", "eighty-seven per cent"; American
  "two thousand six hundred eighty-eight", "two thousand one",
  "eighty-seven percent". `voice.accent` picks the table. A machine reading
  in the wrong accent gives a synthetic voice away at once.
- **Spelling on screen follows the narrator**: British kilometres,
  centred, tonnes, South-East Asia; American kilometers, centered, tons.
  Mixed spelling reads as careless.
- Units a general viewer may not know are explained where they are the
  subject.

## Unslop

Pass the script and the post text through an unslop check before
voicing: the phrases that mark text as machine-written cost trust even
when every fact is right. Cut on sight:

- inflated openers and closers ("In a world where", "Let's dive in",
  "And that's not all", "The answer might surprise you");
- empty intensifiers and hedges ("truly", "incredibly", "it's important
  to note", "arguably");
- the "not X, but Y" reversal used as a tic, and triads of adjectives;
- rhetorical questions that the next sentence answers with "Well,";
- em dashes as a rhythm device (the house style uses none in text on
  screen or in posts);
- vague nouns where a number fits ("a huge area" becomes "1.7 times
  Russia").

## Other rules

- **One analogy per episode**, kept to the end; a second one muddles the
  first.
- **No politics, no taking sides on borders or disputes.** Debate
  perception or method, never sides.
- **The channel is never the one caught out.** A fault found in the data
  the series itself draws with is told as the wider world's ("map data
  that many maps are built on", "some maps count it as …"), never as "the
  map we use on this channel": the owner read that as the channel looking
  unprofessional. The source line still names the data.
- **A slide or scene that repeats an earlier finding says so** ("At the
  hot end, also a near tie").
- **Ask once when an instruction can be read two ways** ("no X" against
  "less X"), with what each reading would build. Guessing builds the
  wrong thing twice.
- **The script is final before voicing.** A later change re-voices only
  the changed sentence (`04-voice.md`), but every change still needs the
  cold read, `recue.py`, the music retime, the caption pages and the
  verification log again.
