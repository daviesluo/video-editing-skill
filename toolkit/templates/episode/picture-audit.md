# {{ID}}: picture audit

What is on screen at each sentence's key words, checked on a still rendered
at that moment (video time, the audio lead included). Re-take the audit
after any re-timing: a stale audit is worse than none, because it reads as
evidence.

Taken <YYYY-MM-DD> on the take of seed <n> (<duration> s), at commit <hash>.

| Time | Words | On screen | Result |
|---|---|---|---|
| 0.0–2.0 | "<the hook>" | <title on screen from the first frame, complete; the subject already up> (still 0.00) | Pass |
| <t> | "<this curve>" | <the curve redraws on "this"> (still <t>) | Pass |

Pointing words ("this", "these", "that", "here", "it"): <each one, and
what it points at on screen at that word>.

Spoken numbers: <each one, and where it is on screen with what it
measures>.

Captions: <n> pages listed with `scripts/caption-pages.ts`; none strands a
word or a number.

Orphan and safe-zone scan every 0.5 s: <clean, or the hits and their fixes>.
