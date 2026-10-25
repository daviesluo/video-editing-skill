# 05: Music and sound effects

The music is felt more than heard: it carries pace and warmth, never
fights the voice, never stops abruptly, and sounds like the same
composer every episode. Sound effects mark cuts and reveals, sparingly,
under the voice. Every sound has a licence record.

## The house sound: "Paper and Wood"

Felt upright piano (low register, sparse dyads and open fifths, never
the melody), pizzicato cello and viola (soft, short, warm), a quiet bowed
cello pedal at the lifts, in a dry chamber room. 88 to 100 BPM, one
tempo per episode, a major key with a Lydian colour, one chord every two
bars, pianissimo to mezzo piano.

It was chosen on measurement against a marimba pulse and cinematic
strings: of the three it left the most room for the voice (the least
energy in the 1 to 4 kHz speech-clarity band), had the fewest note onsets
per second and the steadiest loudness. Marimba beds fight speech and read
as corporate stock; swelling strings carry too much top end and range.

**Never**: vocals, choir or humming, drums, synthesisers, brass, mallets,
risers or impacts, swells, long reverb tails, fade-outs or cut endings,
and no artist or song names in prompts.

## One composed bed per episode

`episodes/<id>/music-plan.json` (from `templates/episode/music-plan.json`)
is a composition plan for Eleven Music:

- **Chunk boundaries sit on segment starts**, so the music lifts where
  the story turns. `python pipeline/music.py retime episodes/<id> <seg>
  <seg> ...` puts them back after any new take of the voice.
- **A continuous pulse from the very first beat**, and a single low note
  at its final level on the first beat: a bed that started sparse sat
  near silence under the hook for three seconds, then came in at once.
- **The same loudness and density in every chunk** ("the same loudness
  and density as the previous section", in each chunk's styles).
- **A held final chord through the end card.** The last chunk asks for "a
  held final chord… that keeps sounding softly under the last spoken
  question and through the end card, fading only in the last second",
  `tail_s` (3 to 4 s) makes the plan run that far past the narration, and
  `music.end_fade_s` 1.0 in `episode.json` makes the mixer fade only the
  last second. A bed that decayed under the last word left a silent end
  card.

Then:

```sh
python pipeline/music.py make  episodes/<id> 101     # and 102, 103 ...
python pipeline/music.py check episodes/<id> episodes/<id>/out/music/take-music_v2_5-101.mp3
python pipeline/music.py use   episodes/<id> <the best take that passed>
```

`use` copies the take to `studio/public/episodes/<id>/music.mp3`
(committed) and records model, seed, song id, generation time and the
licence (from `brand.json`) in `episode.json`. Output is 128 kbps MP3 on
plans without high-quality downloads, which is inaudible under a voice.

## The checks a take must pass (`music.py check`)

Measured after the mixer's own clean-up and levelling, which is what the
viewer hears:

| Check | Pass | The failure it exists for |
|---|---|---|
| length | within 0.6 s of the plan | a bed that ends before the video |
| loudness range | at most 9 LU | swells that fight the voice |
| 1 to 4 kHz share | at most -20 dB | a bed in the voice's clarity band |
| onsets | at most 4 a second | a busy pulse that competes with speech |
| seams | short-term loudness changes at most 4 LU across each chunk boundary | a section that lands louder |
| holes | the quietest 3 s of the body at most 10 dB under its median | near-silence under the hook (one take scored -13.9) |
| hold | under the last words and the end card, at most 12 dB under the median | the chord cut off under the last word |
| ending | the last 1.5 s decays by over 6 dB, no click | a cut ending |
| vocals | a recogniser with voice-activity detection finds no speech | a hummed or sung line |

Make two seeds at least; takes of one plan differ a lot. Then listen to
the opening, each lift and the ending of the mix; measurement finds the
failures above, not taste.

Once the owner has settled a style, every episode still gets two takes
in it (A1 and A2, two seeds of its own plan), and the one that fits that
episode is used, chosen on the bed as the mixer lays it: the least
energy at 250 to 1000 Hz under the words, the drive of the open and of
the stretches the story pushes, how its sections follow the story's
turns. Never by nearness to an earlier episode's take (the owner: "it
needn't match the last one, go with what fits this episode best"). Check
what the take actually plays: two takes of one plan both ran a steady
groove through the two drum drops it asked for, so the stops were made in
the mix.

## Levels and ducking (`mix.py`)

- Voice levelled to -16 LUFS first.
- The bed 8 LU under the voice where nobody speaks; ducked 7 dB under
  speech, driven by the word alignment (pauses under 0.5 s bridged so it
  does not pump; down over 250 ms ending 80 ms before each word, back over
  750 ms); while the voice runs, 250 to 400 Hz dipped 3 dB and 1.5 to
  4 kHz dipped 4 dB. That puts the bed about 15 to 16 LU under the voice
  while it speaks; broadcast practice keeps commentary at least 10 LU over
  music, and listeners prefer more. Measure it section by section: a
  composed bed can climb (one rose from -34 to -26 dB and sat 12.3 LU under
  the follow line); `music.steps` ([{"cue", "db"}] in episode.json) sets
  the bed lower from a cue, ramped over 1 s and held.
- The bed is high-passed at 110 Hz, low-passed at 14.5 kHz and levelled
  at 2:1 with slow attack and release, so sections step rather than jump.
- A bed made for a slightly shorter narration is slowed (pitch kept) to
  fit, up to 5 percent; more needs a new composition.
- Final: -14 LUFS integrated and true peak at or under -1 dBTP, measured
  on the delivered AAC file. The mix is limited 3 dB under full scale
  before linear normalisation, or a punchy voice settles a dB or two low.

## Sound effects

- **Few, under the voice, on meaning**: a whoosh on a camera move, a tick
  on a label, a pop on a marker landing, a low thud on the payoff. One
  effect every 1.5 s or more densely reads as a template, and
  `mix.sfx_problems` says so.
- **Never the same sample back to back.** `pipeline/sfxgen.py` generates
  several takes of each effect into `pipeline/sfx-lib/`, and the mixer
  cycles through them; the synthesised effects in `sfx.py` are the
  fallback.
- **Cues are word cues** in `episode.json` (`{"cue": "payoff@1", "offset":
  -0.2, "name": "thud", "gain_db": -14}`), so they move with the words.
- Prompts for generated effects stay soft, close, dry and short; keep the
  plan and date of every generated take.

## Matching a reference's sound

When a video imitates a reference reel, its sound is measured before any
music is requested: a spectrogram of each section, the loudness every
0.5 s, the tempo from the onsets, which picture changes land on the
music's own accents, and what sounds come from the clips themselves. One
reference's quiet first half carried a crisp sixteenth-note pulse (ticking
hats and a plucked figure) at -22 dBFS, the drop added 11 dB on one
downbeat, the pictures cut in on the music's accents with no effects of
their own, and the end was one low hit with a two-second tail. A first
draft against it had a sustained pad with nothing above 4 kHz, bites as
loud as the drive, a 4 dB lift and a pop on every picture, and the owner
heard at once that it was far worse. Measure the take too: the tempo the
plan asked for is not the tempo it came back at (one asked-for lift was
3 s late and the beat 2 percent off), so time the edit from the take.

## Picture on the drums

When pictures and words arrive to music rather than to a voice, each one
lands on a drum accent of the mix as heard. A hat that ticks every
sixteenth puts some hit near every moment, so "near an onset" proves
nothing: read the final music stem on its sixteenth-note grid (the phase
where its beats sum loudest), sum the onsets of the low, middle and high
bands at every grid point, average each of the sixteen positions over two
bars, and keep the positions at least about a third as strong as the
strongest, each with its strength, nudged onto its onset. Keep two sets:
the beat points (accents of about half the strongest or more, on the
eighth-note grid) for pictures and line pieces, and the lighter hits (a
third or more) for line pieces only; never a ghost note between them. A
section then opens on its downbeat with its first words and its first
picture together; its pictures spread evenly over the beat points up to
a beat before its end, so the page holds complete to be read; further
pieces of the line take the free light hits, and extra pictures pair up
on the last points. Where the music has one hit a beat (before a drop),
a four-beat line holds three pictures one to a hit, or more in pairs.
Taking turns (never a word and a picture on one hit) made the pages slow,
and the owner lifted it: "pictures and words may pop together". A script
lists every pop against the points and fails any more than a frame off;
measure the delivered file against both the list and the audio itself. A
fixed rate on the beat grid is not the same thing: where the track's hits
are syncopated, half the words fall between them, and the owner heard it
at once. A section the owner approved off the grid (a closing sequence)
keeps its approved times.

A statement or payoff line ("With just 146 employees.") is not typed: it
lands whole on its beat and stays whole for at least 0.9 s. Typed in
groups, one payoff was complete for six frames.

## Bites and the end

- Level each sound bite to its own integrated loudness (EBU R128 on the
  cut), not on its "voiced" samples: on a quiet clip those are only its
  peaks, and one bite came out 4 dB under the others.
- End a bite where its last word's sound has fallen into silence on the
  waveform (about -55 dB), not at the aligner's word end: one bite cut at
  the aligned end lost the last syllable of "keyboard".
- **Sound joins are designed, never cut dead.** The owner heard a cut
  whose bed stopped dead under three bites (2 s under -50 dBFS in all) and
  whose film line switched its room on and off, and said "the sound joins
  are not good enough". Now: the bed runs on under every real voice at
  its low end (under 300 Hz, a few dB down), slid into over a third of a
  second on an equal-power curve and back whole on the cut away, and
  under a bare question too; each bite comes in and goes out on its own
  room (a fifth to a third of a second of the room before its first word
  and after its last, faded on equal-power curves), and where a stray
  word sits right against the first one, the room is taken from just
  before it and laid under the cut; a join inside a bite falls in the
  room's quiet. Gate: no 50 ms stretch of the mix under -50 dBFS before
  its last second, and every bite's edge read on its 10 ms levels.
- Check the bed's band balance and its loudness through a phone speaker
  (a 300 Hz high-pass) against the reference's: one generated bed carried
  almost all its weight under 150 Hz and played 4 dB quieter on a phone
  than the reference at the same integrated loudness.
- Limit at four times the sample rate, so the true peak holds: a brighter
  mix passed -1 dBTP through a plain limiter.
- A reel loops: the sound fades to silence over its last half second, and
  the picture and the sound are the same whole number of frames. One end
  chopped a hit's tail at -25 dBFS straight into the opening laugh, and a
  mux with `-shortest` dropped three frames of picture.

## A bleep

A word the story needs heard but not said in full (the owner, on a prop
that reads "I'm CEO, Bitch.": "add it to the voice, but put a beep after
'bi'; design it carefully") is voiced in full and bleeped in the mix:

- the take keeps the whole word, so the transcript check still hears it,
  and the mix replaces the rest of it with the beep;
- the beep is the broadcast one, a 1 kHz sine, from the end of the first
  syllable's vowel through the last consonant, read on the waveform (the
  vowel's fall, the stop's closure, the fricative's high band), not on the
  aligner's times; it ends before the next word's onset;
- its edges are short raised cosines (6 ms in, 10 ms out) and the voice
  is faded out and back in under it on equal-power curves, so neither
  edge clicks and nothing of the hidden consonants is heard;
- it sits about 2 dB under the first syllable's vowel: as loud as the
  word it hides, no louder;
- its times are guarded in the mix script (an assertion that the word is
  still where they were read), since a re-voice moves them;
- the caption shows what is heard (`09-captions.md`, "A bleeped word").

## The music fits the cut

An owner heard a narrated reel's bed as not "fitting perfectly" though
it ran under every word at the right level (2026-10-24). The bed and the
picture are cut together, not laid one over the other:

- a stop and a return fall on the bed's own grid: the bed stops at the
  end of a bar or a beat (never mid-note) and comes back on a downbeat,
  and the word it comes back on is placed there or the return is moved
  to the beat nearest the word;
- the cut itself is made at the hit's attack, not at a beat tracker's
  beat, which sits 30 to 50 ms after it: a stop on the tracker's beat kept
  the first 30 to 50 ms of the next hit and cut it off, a pop on the
  silence after "He walked away." that the owner heard ("there's a burst
  in the sound"), and a return there lost its hit's attack. Find the
  attack on the take (the sharpest rise of its level in the 80 ms before
  the beat), end 4 ms before it with a 25 ms fade, start 4 ms before it,
  and let a hit meant to land on a word ring out instead of chopping it;
  splice two places of the take where the first now ends, crossfaded,
  never with a gap;
- the cuts that no word cues, the cards and the chart's arrivals land on
  the bed's beats (listed by the mix, in video seconds);
- after a real voice's bite, the bed comes back on the cut away from it
  (the frame the speaker falls silent), and the narrator's next word
  lands inside the bar: held for the word, the new picture played over
  0.23 s of digital silence and the film's biggest return landed on
  nothing;
- a cut led by the bed's beats looks for one in a window wide enough to
  outlast small moves of the clock: with 0.22 s before the word, the
  hook's two cuts lost their beats when two bites were trimmed and the bed
  moved 60 ms; 0.27 s (about a third of a beat at 152 BPM) held them;
- the bed's sections answer the story's: a breakdown under a quote, the
  full groove on a turn, the biggest section on the payoff, a last hit on
  the last word, each measured where it lands;
- the bed's level and energy are read section by section under the voice,
  not only as one integrated number.

## The bed under a reference reel

A generated take cut to the picture and levelled to the reference's
profile was still heard as far worse than the reference's produced track.
So a produced track is tried first: the reference's own when it can be
identified and licensed, or a library shortlist measured against the
reference (tempo, the quiet half, the drop, the end). The owner picks by
ear, and may turn all of them down: one owner rejected an identification
that was not the reference's song and a library shortlist, and chose a
generated take built like the reference instead. What made that take
work:

- the request describes the genre and its production (swung hats,
  drum-machine claps, a rolling bassline, sidechain pumping, a loud
  master) with no brand or product names, which the service refuses, at
  its best bitrate;
- the structure is built in the mix, as a DJ would, because the service
  lands its groove within about 15 s whatever the plan says: the take's
  own intro, then its groove with the kick and bass held back by a
  high-pass falling from about 1.6 kHz to 250 Hz, the last beat before
  the drop left out, and the whole groove landing on the drop;
- the first half stays at least about 9 dB under the drive, measured on
  every mix: when later changes let it creep to 2 dB over, the drop no
  longer lifted;
- its tonal balance is matched to the reference's drive by third-octave
  gains (within 6 dB, flat above about 9 kHz, where a platform copy is
  only its codec);
- the owner hears full-length previews of the film's own soundtrack, and
  the take the owner liked stays: new takes were "worse than the previous
  video's", so the liked take's mix is improved instead.

## Never, and the licence record

- Never the platform's in-app music baked into an upload (it is licensed
  for that platform's own use, and a claim follows the file elsewhere),
  meme, film or television samples, or audio from anywhere without a
  licence that covers the use. Ready-made effects from a library whose
  licence allows commercial use without attribution (Mixkit's free
  licence, Freesound's CC0 sounds) are welcome; not every effect has to be
  generated.
- Every bed and effect has a record: service, model or library, seed or
  clip id, plan and terms version with date, and what use the terms allow.
  Generate only on a plan whose terms allow commercial use, and while on
  it: output usually stays under the terms in force when it was made.
