# 03: Script

The script is heard once, at speed, by someone who knows nothing about the
subject and is deciding every second whether to scroll on. Every sentence
must be understood on that one hearing. The script lives in
`episode.json` as segments with ids; scenes, sound and captions key off
those ids and their word numbers.

## Length

The narrator in the house style speaks about 2.5 words a second
including pauses.

| Length | Words |
|---|---|
| 30 s | 70 to 80 |
| 45 s | 105 to 115 |
| 60 s | 140 to 150 |
| 75 s | 175 to 185 |

Shorter holds more of the audience; go long only when the story carries
it. Write slightly under the target: scripts run long when voiced.

## Shape

1. **Hook** (0 to 1.5 s): the question, in full and in plain words, on
   screen from frame 1 and spoken in the first second and a half, over the
   strongest picture already up.
2. **Answer** by about 6 s.
3. **Two or three layers**, each a new verified fact on a new picture.
4. **Payoff**: the number, reveal or comparison worth sending to someone.
5. **Follow beat**: "Enjoy stories like this? Follow for a new one every
   day." (`cta` segment; the promise must be one the series keeps).
6. **Teaser**: "Next, in part N: <the next episode's hook, word for
   word>" (`next` segment).

Segment ids are short words (`hook`, `newyork`, `payoff`, `cta`, `next`)
because cues read `newyork@7`.

## The script, read cold

Read the script as a first-time viewer who knows nothing, line by line,
before voicing and again before release. Every point below is one a
finished, checked episode failed:

- **Every name in full the first time**: "the International Space
  Station", not "the space station"; no jargon a general viewer must
  decode ("the lower 48" becomes "the United States without Alaska and
  Hawaii").
- **Examples as recent as primary sources allow.** Examples from twenty
  years ago sound dated when newer ones exist.
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
- **The next part's hook matches the teaser that promised it**, word for
  word.
- **The line into the teaser follows from what was just shown.** Never a
  bare "So"; "And you may wonder…" or a sentence that hands the last
  picture to the next question.
- **Nothing a viewer could misread or have to replay.** If a sentence
  can be read two ways, rewrite it; do not rely on the picture to settle
  it.
- **Wording the owner gives is used as given**, in the voice, the
  captions and the post text alike.

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
- **A slide or scene that repeats an earlier finding says so** ("At the
  hot end, also a near tie").
- **Ask once when an instruction can be read two ways** ("no X" against
  "less X"), with what each reading would build. Guessing builds the
  wrong thing twice.
- **The script is final before voicing.** A later change re-voices only
  the changed sentence (`04-voice.md`), but every change still needs the
  cold read, `recue.py`, the music retime, the caption pages and the
  verification log again.
