# Sound-effect takes

`pipeline/sfxgen.py` writes several takes of each effect here
(`whoosh-1.wav`, `whoosh-2.wav`, ...), 48 kHz mono, trimmed and normalised.
`mix.py` cycles through them, so a repeated cue never plays the same sample
twice in a row, and falls back to the synthesised effects in `sfx.py` when
an effect has no take. Keep only takes whose licence allows commercial use,
and log where each came from.
