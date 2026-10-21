# A worked finding

One problem's whole life: how the reviewer reports it, how it is fixed,
how the fix is confirmed, and the rule it leaves behind. The episode is
part 5 of an explainer series; its teaser asks "Is Reno, Nevada, east or
west of Los Angeles?".

**The review row** (`review-8a4e84e.md`, written by "video reviewer - 1"
against the render whose SHA-256 it names):

```
### B2. 62.12 s: the caption "Nevada," stands alone on a page

The pages read "is Reno," / "Nevada," / "east or west" / "of Los Angeles?".
The keep "Reno, Nevada" cannot hold, because paginate always breaks a page
at a comma. This is the "Follow for part" / "2." class.

Fix (studio/src/kit/paginate.ts, in paginate): let a kept phrase run
across punctuation.
- Current line: if (!next || /[.,?!;:—]$/.test(w.text)) {
- New line:     if (!next || (/[.,?!;:—]$/.test(w.text) && !held.has(i + 1))) {
- The page then becomes "is Reno, Nevada," (638 px at 100 %).
- Only "Reno, Nevada" in parts 5 and 6 is affected; no other episode's
  keep spans punctuation. Re-list the pages of parts 4, 5 and 6 to confirm
  that nothing else moves.
```

Everything a fixer needs is in it: the time, what a viewer sees, the
cause, the file, the exact line before and after, the expected result
with its measurement, and what to check afterwards.

**The fix**, in one commit with its evidence (the listing gives timeline
seconds, without the video's 0.3 s lead-in):

```
$ node --experimental-strip-types scripts/caption-pages.ts 05-antipodes
 ...
 61.06   638px  is Reno, Nevada,
 62.40   467px  east or west
 63.46   606px  of Los Angeles?
```

The pages of parts 4 and 6 were listed before and after and compared:
only part 6's teaser page changed, the same way. The orphan and safe-zone
scan of the last eight seconds printed nothing.

**The re-check**, by the same reviewer, on the next render:

```
| B2: "Nevada," alone | Fixed: "is Reno, Nevada," is one page from 61.4 s
|                     | (still e/61.4.png); pages of 04 and 06 re-listed,
|                     | unchanged but for 06's teaser, which now reads the same way |
```

**The rule it left behind**, so no later episode can repeat it:

- `references/09-captions.md`: "A kept phrase runs across a comma ("Reno,
  Nevada," is one page; without the keep, "Nevada," stood alone)."
- `references/15-failure-catalogue.md`: the row "'Nevada,' alone, because a
  keep could not cross the comma", with its check, the caption pages.
- `bin/selftest_studio.ts`: two cases, one that the kept phrase holds
  across its comma and one that, without the keep, the comma still ends
  the phrase, so a later change to the pagination cannot quietly undo
  either.

That is the loop working: the finding was exact enough to fix without a
question, the fix was proved on the artefact, the same reviewer confirmed
it, and the class of problem became a rule and a test.

---

Copyright 2026 Zheng Luo (Davies Luo). Licensed under the Apache
License 2.0, whose text is the `LICENSE` file beside this one.
