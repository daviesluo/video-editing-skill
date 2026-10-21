# 15: Failure catalogue

Every rule in this skill is here because a finished, checked episode broke
it. Each row is a real failure from production, the rule it produced, and
where that rule is checked now. Read it before a review; add to it when a
new class of failure appears, in the same commit as the fix.

## Script and wording

| Failure | Rule | Check |
|---|---|---|
| "the space station" on first mention; a viewer did not know which | every name in full the first time | cold read (`03`) |
| examples from 2001 and 2008 sounded dated when newer ones existed | examples as recent as primary sources allow | cold read; fact checker |
| "over 400 tonnes" hanging off the end of a sentence | complete sentences when heard ("which is over 400 tonnes") | cold read |
| "The biggest overlap: China on Argentina." | no colon shorthand where a listener needs the verb | cold read |
| a hook voiced as two questions because of a comma | the hook and teaser are one plain question; measure the take | transcript; `voice.py measure` |
| a bare "So" leading into the teaser felt unrelated | the line into the next part follows from what was shown | cold read |
| a teaser ("the same test on South America") that did not say the question | the teaser says the next question in full | cold read; release review |
| "the lower 48" | no jargon a general viewer must decode | cold read |
| "you almost certainly come out in the sea", for a statistic about land, not people | words say exactly what kind of number it is | fact checker |
| "by area" read as total area for a share | a share is called a share; units explained | fact checker |
| a reply naming a country never verified | every figure in any text block is in the log | fact checker; review |
| a ready reply said one country's far side was "mostly" another; most of it was sea, and only its land was mostly that country | reply text gets the same verification as on-screen facts | fact checker; review |
| a verification note was drafted with a claim not yet checked, and read as verified until a re-read | the check first, then the sentence | fact checker |
| a correction and a second example ran on as one list when heard | connectives carry the turns ("Actually,", "And", "However,"), each voiced with its line | cold read; listen |
| a teaser ("What if we drained the ocean?") sounded odd and promised nothing | the teaser states the next question in full with something concrete to look forward to; its fact verified | cold read; release review |
| the owner's wording read awkwardly in English | offered back with one or two natural phrasings that keep the meaning; the owner picks | before voicing |

## Voice

| Failure | Rule | Check |
|---|---|---|
| a re-voiced ending kept the "fo" of the next line's "Follow" | a short burst after a replaced line is dropped (`speech_span`) | `qa.voice_flaws` stray sound |
| a hiss of the replaced "So" stayed before the new line; the "T" of a replaced "Tokyo" stayed against the new one | cut only in true silence, never at aligned times (`silence_near`) | splice records checked silent on their old side |
| a whole-line re-voice left an old splice record inside the new line, and QA failed on it | records inside a replaced span are dropped | `record_splices` |
| a replacement started inside connected speech and silently dropped "plans to bring down the" | replace from a pause; a start inside speech is refused | `replace_words` raises |
| a take ended on a cut-off fragment, which clicked on the quiet end card | the take's ends are faded and checked silent | `mix.py`; `voice_flaws` |
| numbers read the American way by a British voice | readings per accent in `say` | digit-free transcript |
| a small recogniser passed a misread proper noun that a larger one caught | key words checked with the largest model; several seeds | voice QA |
| captions 70 to 250 ms late after pauses | re-time every take by forced alignment | `build.py realign` |
| "Spain" lit 0.2 s late; "65%" 0.13 s late | a hiss after a pause starts the word | `fricative_onsets` |
| a part at 2.54 words a second, sentence pauses down to 0.31 s, passed every check and two reviews and was heard as rushed | pace is a gate against the series' reference parts, its first approved ones; a fast take is replaced by a seed in their range and its pauses lengthened in their own silence, the words never slowed | QA rhythm check; `voice.py pace-report`; review brief |
| a 4 percent pitch-kept slow-down of that take was heard at once as slowed by hand | the voice is never slowed in post; a `[slowly]` tag at the start of each section slowed the model by about 4 percent | `voice.pace` refuses any slow-down |
| a part heard as rushed beside its four reference parts measured 5.22 syllables a second in speech, its picture moving 29 percent of the time in 2.81 movements per 10 s with a median hold of 0.8 s, every measure outside their range, where words a second had misled | the reference parts are the measured standard, in syllables for the voice and in movement for the picture | QA rhythm check; `rhythm.py report` |

## Music and sound

| Failure | Rule | Check |
|---|---|---|
| the bed sat near silence for 3 s under the hook, then came in at once | continuous pulse and a held low note from the first beat | hole test |
| the last chord was cut off under the last word, leaving a silent end card | a held final chord through the end card (`tail_s`, `end_fade_s`) | hold test |
| a section landed louder at a chunk seam | the same loudness and density in every chunk | seam test |
| the same effect sample twice running | several takes per effect, cycled | `mix.sfx_problems` |

## Picture and animation

| Failure | Rule | Check |
|---|---|---|
| the title still rising on frame 1 | the first frame is complete; reveals that must read at once start at -1.0 s | still at 0.0 |
| a line swept through a caption during a camera move | nothing over captions; lines under the caption-clear mask | review frames |
| "Equator" showed without its line, and stayed after the lines had gone | a line and its label come and go together; masks in frame units | audit; review |
| a label meant for "Montana" pointed into the next sentence after "km²" became one word | cues are words; `recue.py` after any wording change; stale cues refused | `cueAt` raises |
| "this curve" said while nothing redrew | pointing words show their thing on the word | picture audit |
| "Blame this map" said over a close-up | pull back to the whole map when the narration points at it | picture audit |
| a reveal on the word looked late | reveals start 0.2 s ahead with the enter ease | audit stills at word starts |
| a shape slid to compare sizes arrived on its side | rotate on the sphere, `upright` | still |
| a map faded in over a card for 0.1 s | scenes sequenced, not cross-dissolved, when they collide | frames at 0.03 to 0.1 s |
| a profile rose into a still-shrinking picture | two moving things never cross | frames |
| a veil dissolved in four frames, a flash | dissolves eased at both ends | frames |
| the caption band empty for a frame at every page change | a page's first word shows at once | frames |
| a plate's edge slid into frame for five frames during a pull-back | the wider plate is always drawn under the detail plate | edge scan of frames |
| a region left tinted while the narration named another | a tint means "this is what the sentence is about" | audit |
| a sun slid from the 21st to the 10th, false on every frame before it landed | no paused frame shows a false position or number | frames |
| a share counted down, and a cover froze it mid-count | no counting numbers | cover look; frames |
| a line ended in empty sea | what a line reaches is marked and named | audit |
| island names on a circle's rim; a label across its own line | labels beside what they name, never on a line | review |
| bars with an empty track looked like big boxes for small values | a bar is as long as its value | review |
| a speckle of red dots read as a rash | data texture chosen from finished style frames | owner's pick |
| a light palette that looked washed out, then a relief skin that looked too vivid | contrast by lightness, restrained colour, from a ladder of stills | style frames |
| a shaft through the globe drawn as a flat red line over the 3D render: no depth, looked strange, rejected | every detail is designed; a 3D thing is built in the 3D scene (a lit tube with a real opening and a cut-away interior); a change of look shown as 2 or 3 options on stills first | review: "does it look designed, and like what it represents?" |
| a whole layer moved down to make room, leaving a straight edge | move pictures by camera offset, never by moving a layer | stills |
| four camera moves in 3 s, each on its word, felt rushed | no run of moves without a beat to read; the picture no busier than the reference parts | QA rhythm check (`rhythm.py report`); frames; review |
| a redesign's first rounds had flat "petals", a hairline shaft, a ring that read as a button and a see-through planet with a grey core | explore in a lab composition, review your own options over several rounds, show two or three | `variants.mjs`; own review |
| a cut-away shut while the camera turned: its face swept the planet as a band, the page showed through the wedge, a sliver of shaft through the seam; its label floated on after it shut | the cut fixed to the object, turned off square, shut before the camera turns, its labels gone first; radii from a cited model, logged | frames at 0.03 s through each turn |
| a hole modelled on the planet ballooned in the close-ups over its labels and line; the owner wanted "a dot of the right size" | a marked place is a dot sized for the view; 3D only for what is truly 3D | close-up stills |
| a hook asked east or west while both cities' dots were on the map, so the answer showed before it was said | the picture never answers before the voice, nor does the cover | picture audit; cover look |
| an opening map started in close; the owner asked for it bigger, then a zoom in | open wide enough to place the story, then a designed move in | picture audit |
| a map under a white veil read as fog | diagrams sit on the clean page | review |

## Type and layout

| Failure | Rule | Check |
|---|---|---|
| a series badge sat under the platform's top bar | the safe zone is measured on the real player | `UNSAFE` scan |
| then the badge sat 65 px under the bar, a gap that read as loose | the badge's type starts about 34 px under the bar | measured on a screenshot |
| a 72 px title ran 12 px past x 960 | key text inside the safe box, to the pixel | `UNSAFE` scan |
| a caption page "compass bearings" wrapped to two one-word lines | pages measured with the font's own widths | `paginate`; orphan scan |
| "The Julian / calendar" ended a headline on one word, and the probe missed it | the probe measures word-by-word headlines on their masks | `ORPHAN` scan |
| "Follow for part" then "2." | no word alone on a page; a number keeps its next word | caption pages |
| "Nevada," alone, because a keep could not cross the comma | a kept phrase runs across punctuation | caption pages |
| a bar's "100", set inside a thin bar, rode over its top edge, white on the page | a bar's number is sized to the bar and centred on it, inside only where there is no room beside it | `barNumber` self-test; stills |
| a name with a letter the face lacked (Łódź) would fall back to another face | the full font is vendored; every visible character is checked against it | `GLYPH` scan |

## Covers

| Failure | Rule | Check |
|---|---|---|
| shapes bunched under the title with an empty bottom in the grid tile | the subject centred in the tile's space under the title | `covercheck` balance |
| a circle's top 26 px under the title | the subject starts at least 32 px under the title | `covercheck` |
| a cover froze island names mid-fade | look at every cover at full size after any re-timing | by eye |
| a mask that did not move with the cover's picture hid a city's dot and cut a line short | masks move with the picture | cover look |
| a level line left out of the measured subject | zero-height boxes count | `CoverProbe` |

## Release and posting

| Failure | Rule | Check |
|---|---|---|
| straight apostrophes arrived as ‘ in two live captions | write ’; refuse ' and ‘ | `publish.py check` |
| an audio name of 51 characters, refused, settable only once | at most 50 | `publish.py check` |
| a caption line saying how the video was made | the label does the disclosure, never the caption | `publish.py check` |
| a release reached review unstaged, so its checks never ran | stage before review | review checks the folder |
| a draft upload was recompressed to 40 percent of its size | post from the original file at highest quality | posting guide |
| a linked-video feature was announced for removal soon after launch | series carried by pinned comments, not a feature | posting guide |
| a hashtag that looked right belonged to a skincare brand | every tag checked on its public page | hashtag table |

## Tooling and process

| Failure | Rule | Check |
|---|---|---|
| stills bundles (100 MB each) filled the disk | scripts delete their bundle | `stills.mjs` |
| a one-frame cover composition always showed frame 0 | a cover composition is as long as its episode | `coverMetadata` |
| `pkill -f` killed its own shell | kill by process id | |
| a run printed "passed" and exited 1 | read exit codes | |
| a stale picture audit with first-take times read as evidence | re-take the audit after any re-timing | review |
| flat point-in-polygon tests found false land bands | repair antimeridian rings before computing | analysis script |
| two values for one quantity across screen and caption | one quantity, one value | fact log |
| a render waited on one helper while the other sat idle | split it across both (`RENDER_FRAMES`), `join` after the frame counts are checked, frames either side of the seam looked at | `build.py join` |
| a usage limit stopped every agent mid-task | record what was running in the ledger; resume each by message once the limit resets | ledger |
| work on another episode competed with the one the owner was waiting to post | everything into the waiting deliverable; other reports filed until it ships; the owner told when a background step finishes | ledger |
| render bundles in the temporary folder and per-review frame dumps filled the disk, which stops renders | delete dumps and stills when their report is written; `df -h` before a render | `df -h` |
| a review found problems in rounds, back and forth | one exhaustive pass with exact fixes and an empty "could not check" list | review brief |
