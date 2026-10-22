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

## Levels and ducking (`mix.py`)

- Voice levelled to -16 LUFS first.
- The bed 8 LU under the voice where nobody speaks; ducked 7 dB under
  speech, driven by the word alignment (pauses under 0.5 s bridged so it
  does not pump; down over 250 ms ending 80 ms before each word, back over
  750 ms); while the voice runs, 250 to 400 Hz dipped 3 dB and 1.5 to
  4 kHz dipped 4 dB. That puts the bed about 15 to 16 LU under the voice
  while it speaks; broadcast practice keeps commentary at least 10 LU over
  music, and listeners prefer more.
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
strongest, each with its strength, nudged onto its onset. A section then
starts on a beat, its words type in a group at a time on the strong
accents (kick, snare, clap), and pile pictures land on accents between;
after the drop, only on the strong ones, or they fall on a weak hit a
sixteenth before the kick. Measure the delivered file against both the
list and the audio itself. A fixed rate on the beat grid is not the same
thing: where the track's hits are syncopated, half the words fall between
them, and the owner heard it at once.

A statement or payoff line ("With just 146 employees.") is not typed: it
lands whole on its beat and stays whole for at least 0.9 s. Typed in
groups, one payoff was complete for six frames.

## Bites and the end

- Level each sound bite to its own integrated loudness (EBU R128 on the
  cut), not on its "voiced" samples: on a quiet clip those are only its
  peaks, and one bite came out 4 dB under the others.
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

## The bed is produced music

An owner who heard a generated take beside a reference reel's produced
track said the sound was still far worse, after the take had been cut to
the picture and levelled to the reference's profile. Where the reference's
bed is a produced track, so is ours: a licensed library track, or the
reference's own when it can be identified and licensed. Shortlist by
measurement against the reference (tempo, the quiet half, the drop, the
end), then the owner picks by ear.

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
