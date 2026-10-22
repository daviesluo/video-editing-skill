# 04: Voice

The narration is the spine of the episode: captions, cues, sound and the
music's sections all hang off its word timings. It must sound like one
calm, confident documentary narrator reading a script they understand,
with no stray sound anywhere, and every word timed to its voiced onset.

## Choosing the narrator

- The most human-sounding voice available, chosen by the owner by ear
  from three or four candidates: `pipeline/audition.py <dir>
  <voice_id>:<label> ...` renders the same passage in each, loudness
  matched, so the choice is about the voice. Use a passage with a number,
  a name and a question in it.
- The same voice in every episode of a series. Record the voice id, its
  library name and the accent in `episode.json` (`voice`).
- Library voices may need a paid plan; generate only on a plan whose
  terms allow commercial use, and log it.

## Settings

| Field | Value | Why |
|---|---|---|
| `model` | `eleven_v4` | the most natural delivery available; takes no `style`, `speed` or SSML |
| `stability` | 0.5 ("natural") | lower drifts in character, higher reads flat |
| `similarity_boost` | 0.75 | |
| `seed` | fixed per take | a take can be reproduced, and seeds can be compared |
| `format` | `mp3_44100_192` | converted to 48 kHz WAV on arrival |
| `language_code` | `en` | |

Pace with punctuation and sentence length, not with settings, then
measure the take ("Pace, measured against the reference parts" below).
Direction tags are stripped from captions and alignment automatically; at
most one or two such as `[curious]` in a script, and never one to change
the speed: a tag changes how the narrator sounds, and the tone is held to
the reference parts as the pace is ("Tone, measured against the reference
parts" below).

## One request per episode

`build.py episodes/<id> voice` sends the whole narration in one request to
`/with-timestamps`, which returns the audio and per-character timings of
the text as sent. One request keeps the prosody whole: separate requests
per sentence sound like separate readings. The take goes to
`studio/public/episodes/<id>/voice.wav` and its timeline to
`timeline.json`; commit both (`git add -f voice.wav` for the shipping
take only), so a re-render never needs a new request.

## Re-time every take by forced alignment

Synthesis timings run 150 to 250 ms late on words after a pause.
`build.py episodes/<id> realign` sends the finished audio and the text as
spoken to forced alignment, which lands within about 85 ms of the voiced
onsets, and rewrites the timeline (the audio is unchanged). Then
`voice.fricative_onsets` corrects the one case forced alignment gets
wrong: a word that starts with a hiss after a pause ("Spain", "So",
"65%" read "sixty-five") is placed at its next sound, up to 0.2 s late; its
start is moved back over the hiss. A hiss that runs on unbroken from a
word ending in a hiss or burst ("straight south") stays with that word.
Spot-check disputed words on a spectrogram.

## Pace, measured against the reference parts

A take can pass every check and two exhaustive reviews and still be
rushed, and the owner hears it at once. So the pace is not a target
chosen in advance: the series' first approved parts are the standard,
listed in `brand.json` (`rhythm.reference`), and every later take is
measured the same way and kept inside their range. `python
pipeline/rhythm.py standard` measures them and writes the limits
(`rhythm.limits`) and their typical pauses (`rhythm.pauses`) back into
`brand.json`; run it again whenever the owner adds a part to the
standard. `build.py render` prints the take against them before
the render is spent, and QA gates it (`12-qa-gates.md`, "voice pace").

- **Syllables, not words.** Words a second mislead when one script is full
  of short words ("Dig straight down into the Earth"), which reads fast
  in words and not in syllables. `voice.pace_measure` counts
  syllables, numbers as they are read through `say`, on the forced
  alignment, which is the same for every episode.
- **Within speech and overall.** The rate within speech (every pause over
  0.125 s taken out) is the narrator's speed; the rate over the whole
  narration, first word to last, adds the pauses. On one series' four
  reference parts these were 4.86 to 5.13 syllables a second in speech
  and 3.58 to 3.81 overall; a part heard as rushed ran 5.22 in speech.
  The line is 0.125 s, not 0.12, because forced alignment places words
  in 20 ms steps: gaps of exactly 0.12 s fell either side of a 0.12 line
  by rounding, and the same take read 0.1 syllables a second apart from
  one run to the next. Two alignments of the same words still differ by
  up to about 0.05 in speech, so a take that close outside the range is
  not faster or slower than it by anything the measure can tell, and the
  check allows it.
- **The pauses.** No sentence pause and no section break shorter than the
  reference parts' shortest (0.40 s at a sentence end on those parts).
  Their typical pauses were about 0.5 s at a sentence end (the median)
  and 0.6 s at a section break.
- **Beside every earlier part.** `python pipeline/voice.py pace-report
  episodes/<id>` prints the episode beside every other one, the reference
  parts marked. A take faster than every reference part is fast, whatever
  else it passes.

The words themselves are never slowed. A 4 percent slow-down with the
pitch kept was tried on a rushed take, and the owner heard it at once as
"obviously slowed down by hand, very unnatural". Speed is a property of the
take, so it is chosen, not processed:

- **Choose the take: tone first, then the slowest.** Generate the whole
  narration, with no direction tag for speed, on many seeds (one part took
  twenty, which ran 5.20 to 5.45 syllables a second in speech). Keep the
  takes whose tone is inside the reference parts on every measure (below),
  and of those the one that speaks slowest and reads best (one part's
  slowest in tone ran 5.16, against a reference range of 4.86 to 5.13:
  inside the measurement's noise). Nothing else slowed the model:
  `[calmly]`, a higher stability, the `speed` setting, requesting each
  section separately and one `[slowly]` tag at the very start made no
  difference, and an earlier part's narration passed as `previous_text`
  made the voice faster (5.41 to 5.54). A `[slowly]` tag at the start of
  every section did slow it by about 4 percent, and the owner heard at
  once that the narrator had changed: "why do the tone and style feel
  different from the earlier parts, above all the first sentence, which
  sounds listless?". It is not used. Check again on a new model, by the
  same measures, before relying on any of this.
- **Then the pauses, for the overall pace.** `python pipeline/voice.py pace
  episodes/<id>` (`voice.pace`) lengthens each short pause in its own
  silence, a sentence end and a section break up to the reference parts'
  typical pauses (`rhythm.pauses`) and a comma's pause by 0.1 s; pass
  longer pauses to `voice.pace(public_dir, 1.0, sentence, section, comma)`
  where the rate over the whole narration is still fast (the part above
  needed 0.66 s at a sentence end and 0.84 s at a section break to reach
  the reference range overall). No word is cut and none is stretched.
  The word timings, the segments and the take's splice records move with
  the silence put in before them, so the paced take is not re-aligned: a
  forced alignment of a paced take placed the same words' ends differently
  and read 0.05 to 0.07 syllables a second faster with no word changed.
  Then `pace-report` again, `recue.py` for any wording that changed, and
  the music re-made, since every segment now starts later. A slightly
  longer episode is fine; a rushed one is not. The silence put in is
  digital zero, below the take's own floor of about -85 dB; under the bed
  (-20 to -37 dB in every pause) it is not heard, so a review notes it
  and leaves it.

## Tone, measured against the reference parts

The reference parts are the standard for how the narrator sounds as well
as for how fast they speak. A take can keep their pace, pass every other
check and still be heard at once as another reading; the owner put it as
"the tone and style of the earlier parts' voice are one of the quantified
standards too". `python pipeline/voicestyle.py standard` measures the
reference parts' takes (`rhythm.reference`) and writes their range into
`brand.json` (`voice_tone.limits`); `voicestyle.py report episodes/<id>
[voice.wav]` measures one take, a seed being tried included (its
`timeline.json` beside it), and QA gates the shipping take (`12-qa-gates.md`,
"narrator's tone"). On the take and its word timings:

- **Pitch**: the median, its spread over the take (10th to 90th
  percentile, in semitones) and its movement within sentences (the mean
  of each sentence's standard deviation, in semitones): how lively the
  intonation is.
- **Loudness**: how much the words vary in level (the standard deviation
  of each word's level, dB).
- **Brightness**: the median spectral centroid of voiced speech; a
  breathy, low-energy read is darker.
- **The hook**: the first sentence's pitch movement and its level against
  the whole take's, where a listless opening shows first.

The take slowed by a `[slowly]` tag at every section measured outside on
three of these where the untagged takes were inside: its pitch median
128.6 Hz against the reference parts' 130.9 to 141.1, its words' levels
spread 3.6 dB against 2.94 to 3.28, and its opening line 0.4 dB under the
take where theirs sat 0 to 1.04 dB over it. Each measure may sit a little
outside the range before it counts (`voice_tone.tolerance`: four parts are
a small sample and the pitch tracker moves a reading a little), set so that
the take the owner heard as listless fails and the untagged ones pass.
`voice_tone.pitch_hz` is the pitch tracker's range: it must hold the
narrator's voice with room either side (60 to 320 Hz for a low male
voice; raise both for a higher one, then re-measure the standard).

## Choosing among seeds, by measurement

A take can sound different on every seed. Generate three to six, then
keep the one that measures best, not the one that happened first:

- **The transcript reads as written.** A recogniser hears the take; a
  question meant as one must be heard as one ("Where would you come out
  on the other side?", not "…come out? On the other side?").
- **Pitch does what the sentence needs.** `python pipeline/voice.py
  measure <wav> <start> <end>` prints the pitch at the start and end and
  the slope over the last 0.4 s: a statement or a whole question falls at
  its end; a rise mid-line is a second question.
- **Length suits the cut.** A hook spoken too fast is lost; "Where … side?"
  needed at least 1.6 s.
- **Key words are clear.** Check proper nouns and numbers with the
  largest recogniser the machine can hold: a small model once passed a
  misread name that a larger one caught. `build.py qa` and `voice.py
  measure` use `medium.en` by default; set `QA_WHISPER_MODEL=large-v3`
  (or `qa.model` in `episode.json`) where the machine holds it. Coined names go in
  `qa.hotwords`, and a person still listens to them.

## Changing a finished take

Never re-take a whole approved narration for one changed sentence: the
new take changes every timing and every delivery around it.

- **`python pipeline/voice.py replace episodes/<id> <seg> <first> <last>
  [seed]`** (`voice.replace_words`) re-voices one changed phrase, words
  `first` to `last` of the segment, after the new wording is in `episode.json`:
  only that phrase is synthesised, with the narration before and after as
  context, trimmed to its sound, matched in loudness to the segment, and
  spliced in with 15 ms ramps. The extra length comes out of the pause
  after it. Then `realign`, `recue.py`, the music retime and the caption
  pages.
- **Replace whole sentences, from a pause.** A start inside connected
  speech is refused, because the nearest silence can be words earlier and
  the cut would silently drop them; this once dropped "plans to bring
  down the" from a line.
- **Cuts are made only in true silence** (`silence_near`: 30 ms of frames
  over 55 dB under the take's peak), never at the aligned times: an
  aligned start can be 0.1 s after a word's "S" or "T" begins, and a cut
  there once kept the hiss of a replaced "So" and the "T" of a replaced
  "Tokyo".
- **A short burst after the new line is dropped** (`speech_span`): given
  the next line as context, the model can start voicing it, and a
  re-voiced ending once kept the "fo" of the "Follow" that came next.
- **Every splice is recorded** in the timeline (time, and which side is
  old audio), and QA fails a splice whose old side is not silent. Records
  inside a span that a later re-voice replaced are dropped.
- **A connective is voiced with its line.** A turn word added later
  ("Actually,", "And", "However,") is never spliced onto the old take:
  re-voice the whole line from the pause before it, so the word is read
  as part of the sentence, and listen that it sounds natural.
- **`python pipeline/voice.py add-line episodes/<id> <seg> [seed]`**
  (`voice.add_line`) appends a new last
  segment (a call to action added after approval) the same way, placed
  after a pause.
- Pass a seed to try several seeds of a replacement; copy `voice.wav`
  and `timeline.json` aside first and keep the best by the measures above.

## The take's QA

`build.py episodes/<id> qa` runs `qa.voice_flaws` on every take, and it
must print nothing:

- no sound within 40 dB of the take's peak that belongs to no word;
- no splice whose old side holds sound;
- no sample jump over 0.01 inside a pause (a click);
- the first and last samples silent and the last 50 ms empty (a take that
  ended on a cut-off fragment clicked on the quiet end card; `mix.py` also
  fades both ends over 10 ms).

The take must also keep the reference parts' pace and tone (above; QA's
"voice and picture at the reference parts' rhythm" and "narrator's tone at
the reference parts'"). And the transcript must match the script (word error rate at or under 3
percent, every difference read by eye, digits forbidden in a check of the
`say` readings). Before calling a voice fix done, run every check over
every take, not only the spot that was reported.

## Test voice

`VOICE_PROVIDER=kokoro` gives a local voice with word timings, for
pipeline tests with no key. It never ships.
