# 15: Failure catalogue

Every rule in this skill is here because a finished, checked episode broke
it. Each row is a real failure from production, the rule it produced, and
where that rule is checked now. Read it before a review; add to it when a
new class of failure appears, in the same commit as the fix.

## Script and wording

| Failure | Rule | Check |
|---|---|---|
| a part's first 35 s, built on a chain of ideas (three dates at once, UTC, midnight sweeping west, the date line), confused the owner after passing the script edit and two reviews; the part was rewritten round one concrete case (two islands 120 km and a day apart) | one concrete thing per topic; count the ideas a viewer must hold before the answer | `01`; the review's comprehension pass |
| "Sliding due west keeps every place on its own latitude" passed everything and the owner could not follow it | plain physical words, the 12-year-old test | `03`; the comprehension pass |
| "the space station" on first mention; a viewer did not know which | every name in full the first time | cold read (`03`) |
| examples from 2001 and 2008 sounded dated when newer ones existed | examples as recent as primary sources allow | cold read; fact checker |
| "in a 1981 study" passed the script edit and two reviews; the owner asked at once for something newer | studies as recent as examples, each one's year in the research, an old one only with the reason nothing newer is as solid | cold read; fact checker |
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
| a 4 percent pitch-kept slow-down of that take was heard at once as slowed by hand | the voice is never slowed in post; speed comes from choosing the take | `voice.pace` refuses any slow-down |
| a paced take failed the tone gate that its unpaced take had passed (pitch movement 4.35 against 4.56, the same words): the pauses `voice.pace` lengthened were digital zero, and the pitch tracker then dropped most of the voiced frames of the short sentence after one | the silence put in is the pause's own room tone (its quietest 20 ms, never over -80 dB) | tone gate on the paced take |
| 0.1 s of room tone put into a comma's pause cut a hole in a breath that ran through it at -25 to -53 dB, and the narration check passed it (no splice recorded) | `voice.pace` lengthens only a pause that falls silent (quietest 20 ms under -60 dB) and moves the rest to the next silent pause | `qa.voice_flaws` hole check |
| a take slowed into the pace range by a `[slowly]` tag at the start of every section was heard at once as a different reading, "above all the first sentence, which sounds listless"; measured, its pitch median sat 2.3 Hz under the reference parts' lowest, its words' levels spread 3.6 dB against at most 3.28, and its opening line 0.4 dB under the take where theirs sat 0 to 1 dB over it | the reference parts are the standard for the narrator's tone as for the pace; no direction tag for speed; untagged seeds inside the tone first, then the slowest, then pauses for the overall pace | QA tone check; `voicestyle.py report` |
| the same take's speech rate read 0.1 syllables a second apart between two runs, because gaps of exactly 0.12 s fell either side of a 0.12 s pause line; a re-alignment of a paced take read it 0.05 to 0.07 faster with no word changed | a pause is a gap over 0.125 s; the speech limit allows 0.05 for the alignment's noise; `voice.pace` moves the word timings with its silence instead of re-aligning | selftest; `voice.pace_measure` |
| a part heard as rushed beside its four reference parts measured 5.22 syllables a second in speech, its picture moving 29 percent of the time in 2.81 movements per 10 s with a median hold of 2.03 s, every measure outside their range, where words a second had misled | the reference parts are the measured standard, in syllables for the voice and in movement for the picture | QA rhythm check; `rhythm.py report` |

## Music and sound

| Failure | Rule | Check |
|---|---|---|
| the bed sat near silence for 3 s under the hook, then came in at once | continuous pulse and a held low note from the first beat | hole test |
| the last chord was cut off under the last word, leaving a silent end card | a held final chord through the end card (`tail_s`, `end_fade_s`) | hold test |
| a section landed louder at a chunk seam | the same loudness and density in every chunk | seam test |
| the bed climbed from -34 to -26 dB over the episode and sat 12.3 LU under the follow line against the house's about 15 | measure voice against bed per section; a cue-keyed step (`music.steps`, ramped over 1 s) where the bed climbs | per-section LU table |
| the same effect sample twice running | several takes per effect, cycled | `mix.sfx_problems` |
| a drop stopped lifting: later changes let the first half creep 2 dB over the drive | the first half at least about 9 dB under the drive, measured on every mix | loudness by section |
| a bite cut at the aligner's word end lost the last syllable of "keyboard" | a bite ends where its sound falls into silence on the waveform | waveform at the cut |
| pictures and words taking turns on the hits made pages slow | the first words and the first picture together on the downbeat, pictures spread over the beat points | `pops.ts` list; the owner's ear |

## Picture and animation

| Failure | Rule | Check |
|---|---|---|
| every dot outside the group lit flashed back to full for half a second at each handover between groups, because each group's dimming window ended where the next began | one held dim from the first group to the end card, the groups lit over it | dark-pixel count across each handover |
| a 200 km band drawn as a translucent stroke along the lines read as their casing, not as an area, and its round caps spilled past the map's outline | show an area by fading what lies outside it, clipped to the map's outline | still at phone size |
| text started on the first word of a sentence whose own words came 0.6 to 2.7 s later ("The United States…" for "about 81%") | a line starts on its own first word, and its sound with it | cue table against the timeline |
| the map faded out and the follow card faded in with four frames of empty page between, and a slide drawn under the end card's veil washed out and jumped back to colour | one move: the map slides into the card's window as it is clipped to it, drawn above the veil, and the card takes over on the same pixels | frames at 1/30 s through the handover |
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
| a veil dissolved in four frames, a flash; a plate's change to the sea's flat colour, driven by a zoom's scale, went in five frames at its fastest stretch | dissolves eased at both ends; a change tied to a zoom runs on an eased band of its log scale | frames |
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
| a close-up's detail texture, passed only while it was in use, swapped files mid-shot: the planet's world map showed over the close-up for two frames as the camera landed | a texture prop is passed on every frame (its strength may go to zero); textures load once | `useTexture` fails the render when its file changes; frames through every landing |
| a hook asked east or west while both cities' dots were on the map, so the answer showed before it was said | the picture never answers before the voice, nor does the cover | picture audit; cover look |
| an opening map started in close; the owner asked for it bigger, then a zoom in | open wide enough to place the story, then a designed move in | picture audit |
| a map under a white veil read as fog | diagrams sit on the clean page | review |
| a globe's half-turn ran 140° in 0.55 s beside its twin's 2.25 s, a whip pan, after its start was moved to wait for a cut and its end stayed on its word | a camera move is judged by its speed against its sibling moves; when its start moves, its end moves with it | pre-render pass; review frames |
| a planet meant to turn to glass stayed solid for a whole render part, the lines inside it never seen: its material was compiled once, solid, and not rebuilt; every still (each a fresh page) was right, so the stills, the audit and every gate passed | a 3D material whose transparency or other compiled state changes is keyed on that state, so it is rebuilt | a short sequence render through every change of 3D state, from a part's first frame; never stills alone |
| a tick of a shaft stayed on a planet's edge for half a second after its cut had shut | an element is drawn only while its scene is | pre-render search; frames |
| a country outline faded as `on × (1 − other)` came back at a quarter as both windows closed, and its straight border flashed across the frame on a posted part | what gives way is tied to the arrival of what replaces it, never to the whole window; every scene searched for the product | pre-render search; frames at 0.03 s |
| each change of scene was two short moves with a beat between, and the picture measured busier than the reference parts while each move looked right alone | a change of scene is one continuous move | QA rhythm check; `rhythm.py moves` |
| a chip said "The line moved" before the line moved; a "Lined up" label came before its slide | a label that names a change appears with the change | audit stills |
| a headline was written out a second before the voice reached its words; another said "too" where the voice said "the same way"; "Memory lines them up" named nothing | a headline says what the voice says, in its words, and starts on its own first word | audit stills; review |
| a detail plate ending at 55°N drew a hard seam across the top of a wide opening, on frame 0 | a detail plate fades out before its own edge | frames at full size |
| a card's flat map at 200 px a radian spanned about 250° and showed a blank strip past -180° through two renders and two reviews; a regional plate ending at the equator drew a hard edge across the top of a wide view for 52 s | a flat map view's span is worked out from its scale, across and up and down, and kept inside its plate | pre-render arithmetic; review |
| a relief grid still held a seabed high under a phantom island's footprint, and the part about that island showed it as a pale wedge where the voice said deep ocean | look at what a dataset draws under the subject; where it contradicts the primary measurement, correct it from that measurement and log the edit | `02`; review frames |
| a big map hidden under a veil, as a review asked, faded with the veil and crossed the card that replaced it for seven frames | the outgoing picture leaves on its own ramp, gone before the arrival; a fix is checked for the faults it can bring | re-check frames |
| a clip darkened from a beat partway through it stepped down a notch mid-shot, and the owner saw the page flicker | no step in brightness inside a shot | mean brightness per frame through every shot |
| a hall with a black screen, darkened under a line, read as "most of the screen is black" | footage under a line is a bright shot whose own dark area holds the line | stills; mean brightness |
| a speaker filled into the upright frame had his head under the player's top bar, and a word sat across his face | the box stops at the safe top; lines sit on the body | text scan; stills |
| an approved page was rebuilt by a later pass, four times, and the owner asked for each back | what the owner approved stays; findings against it go to the owner first | `13` |

| four long globe turns peaked at 4,400 to 5,250 px/s, two to three times the accepted half-turn; the biggest change of the part (the sea dropping from 3,682 to 6,000 m) ran during one of them and was not seen | long turns fly out and back, each peak computed and kept near the accepted turn; a described change runs after the landing | `08`, a per-frame camera model |
| a turn needed 1.5 s between two named places the voice said 0.9 s apart, so "France" never reached full strength and "Asia" was labelled after its word | widen the pause between the two words in its own silence (`voice.widen`), never speed the picture | stills at each word |
| the "ridge" line drawn from a plate model's ridge and transform classes also drew the Caribbean, the Azores to Gibraltar line and the Scotia arc, which are not the ridge, and piled up on the globe's outline and under the captions | a line that names one feature is filtered to that feature (connectivity, length, the source's own classes read with care), faded towards the limb and masked out of the caption band | stills at its words; a plot of the exported line |
| one line carried two names in two scenes ("Mid-Atlantic Ridge", then "Mid-ocean ridge") and each label sat 200 px off it | one name per feature, the voice's; a label starts 20 to 40 px beside its line | stills |
| a drained sea floor read as a flat sheet with the continents laid on it as lit cut-outs: the live relief lit the land only, so the old coast drew a step | anything revealed on a globe is lit from the same height field as the land beside it | 1:1 crops at the coast |
| the line "Most of the rest is a rough estimate from satellites" had nothing in the picture for nine seconds | a payoff's point is shown with its data, not only written | picture audit |


## Type and layout

| Failure | Rule | Check |
|---|---|---|
| a series badge sat under the platform's top bar | the safe zone is measured on the real player | `UNSAFE` scan |
| an end card's title set in forced lines left "appear." alone in its middle line; the probe tested only each block's last line | no line of one word anywhere in a block | the orphan probe flags any one-word line |
| then the badge sat 65 px under the bar, a gap that read as loose | the badge's type starts about 34 px under the bar | measured on a screenshot |
| a 72 px title ran 12 px past x 960 | key text inside the safe box, to the pixel | `UNSAFE` scan |
| a caption page "compass bearings" wrapped to two one-word lines | pages measured with the font's own widths | `paginate`; orphan scan |
| "The Julian / calendar" ended a headline on one word, and the probe missed it | the probe measures word-by-word headlines on their masks | `ORPHAN` scan |
| "Follow for part" then "2." | no word alone on a page; a number keeps its next word | caption pages |
| "Nevada," alone, because a keep could not cross the comma | a kept phrase runs across punctuation | caption pages |
| an end card's title left to wrap put "longest" alone on a line | titles broken by hand where the phrases break, no word alone | `ORPHAN` scan; by eye |
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
| a cover printed "Where are \| the cracks?" (a "\|" inside an accent not split), froze mid-reveal so the dots half-answered its question, and its dots vanished at grid size | "\|" split in every span; a question cover freezes before its answer, a statement cover on the finished picture; look at the 240 px tile | `covercheck` prints-markup rule; by eye in the tile |
| a group of cut-out faces with one face hidden, one the audience would not know, and heights rising one way | two rows, staggered, every face whole and known | the cover at full size and in the tile |

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
| background removal of eleven photos in one process grew past 14 GB and was killed after the first | one image per process | the memory killer's log |
| raw downloads (1.9 GB) sat under the studio's `public/`, which Remotion copies into every bundle; a render and a scan at once filled the disk | only the cut clips the episode uses live in `public/`; the sources stay outside it | `du -sh public` |
| a render failed on a full disk, its error hidden by an output filter, and the previous video was muxed and nearly sent | delete the old output before rendering, check the render's exit status, never filter its output in a way that hides an error, and look at the new file's frames before sending | the exit status; the new file's time and frames |
| an episode stopped mounting the component that held the orphan probe; every scan printed nothing and was reported as "0 findings" while six texts sat outside the safe box | the probe logs that it ran on every still, and a still without that line fails the scan ("NO-PROBE"); a check is trusted only once it is known to be able to fail | `stills.mjs` |
| a reframed photo's bottom edge ran across the tops of the last line's letters for 2.3 s; the text scan only reads text, so it passed | the probe compares dark page type with every layer marked `data-picture` ("CLASH"); a new check is first run where the fault is known to be | `stills.mjs` |
| a one-frame cover composition always showed frame 0 | a cover composition is as long as its episode | `coverMetadata` |
| `pkill -f` killed its own shell | kill by process id | |
| a run printed "passed" and exited 1 | read exit codes | |
| a stale picture audit with first-take times read as evidence | re-take the audit after any re-timing | review |
| flat point-in-polygon tests found false land bands | repair antimeridian rings before computing | analysis script |
| two values for one quantity across screen and caption | one quantity, one value | fact log |
| two helpers' parts failed: the asset branch was listed by searching the code for file names and missed paths the code builds | the branch's list comes from the episode's own media list, diffed with the branch before every brief | `assets.ts` against `git ls-tree` |
| a render waited on one helper while the other sat idle | split it across both (`RENDER_FRAMES`), each part briefed with its range and frame count and checked by its SHA-256, `join` after the counts are checked to meet and add up to the composition, every seam compared with stills | `build.py join` |
| a usage limit stopped every agent mid-task | record what was running in the ledger; resume each by message once the limit resets | ledger |
| work on another episode competed with the one the owner was waiting to post | everything into the waiting deliverable; other reports filed until it ships; the owner told when a background step finishes | ledger |
| render bundles in the temporary folder and per-review frame dumps filled the disk, which stops renders | delete dumps and stills when their report is written; `df -h` before a render | `df -h` |
| a review found problems in rounds, back and forth | one exhaustive pass with exact fixes and an empty "could not check" list | review brief |
| one part went through five partial re-renders, each finding the next fault in the picture's rhythm, all of them in the code before the first render | every check that runs on stills, timeline or audio runs before the first full render, every fault fixed together, then one render | pre-render pass (`11`) |
| a fix moved a slide's end into the next part, which would have left eight frames of a kept part out of step at the seam | a part is kept only when the change provably leaves its frames as they were; every seam checked against stills | seam check; the commit diff |
| a quarter-size preview read a median hold of 4.1 s where the full render read 2.92 s | a preview is a first look; the rhythm gate runs on the delivered file | `rhythm.py report` |
| one-frame blips split long holds and the median hold read 1.55 s where the eye saw 1.7 s; a faint slow-starting shape read as a short hold | a change under 0.2 s counts as still; before trusting a fault, list what the measure counted | `rhythm.py moves`; selftest |
| a part was posted with a whip pan, a shaft's tick and, found once live, a flashing border, because there was no time left to fix them | no finding ships for lack of time; a deadline moves the review earlier | review planning |
| a reviewer's proposed end time was said to clear a card's arrival and did not | a proposed fix is worked out on the timeline before it is used | re-check |
| a request the owner then withdrew ("forget I said it") had a trial in the tree | revert it cleanly, prove the tree unchanged, commit nothing of it, and say so | `git diff` empty |
| an interrupt sent to a render helper by mistake left its render running with nobody to push it | follow a mistaken interrupt with a message at once | helper's reply |
| the mux's `-shortest` with a stream copy cut the last one to four frames of four parts | the mix is padded or trimmed to the picture's length, and QA counts the delivered frames against the render's | `build.py mux`; QA "every rendered frame delivered" |
| a stray `rm -f /dev/null` was typed into a loop | re-read every compound command; never remove a path built from a variable without `${VAR:?}` | by eye |
| the retention curves of parts 4 to 6 fell from a quarter of the viewers to about 5% on "Enjoy maps like this?", and the 10 s of follow line and teaser after it were watched by almost no one | one end line, the follow and the next hook in the same breath, no promise and no "Next, in part N"; the payoff just before it | cold read; the `cta` segment's length on the timeline; the retention curve after posting |
| a blocky 2007 interview cleaned with Real-ESRGAN came out waxy and drawn, and the owner read it as AI-made | archive footage is shown as it survives, never upscaled or restored | 07 "Old footage as it survives"; by eye on stills |
| two interview bites held their picture to the next word's cut, three to seven frames after the speaker stopped, and the owner sent them back twice | a bite's source ends where its last word fades and its picture leaves on that frame; what follows takes over in the pause | 08 "No dead length"; stills on the frames either side of each bite's end |
| a crop set to clear a news band still cut the sign: the band covered the letters' feet in the source, and the crop was judged on a reduced still | the mark's foot found row by row on the source frame; a mark the source's own band covers comes from another shot | 07 "A logo that is the subject is shown whole"; a full-size still of the edge |
| a founder on the chosen cover was looking down and read as eyes closed | every cover face has its eyes open; the frame picked at 0.1 s steps | 10 "Every face has its eyes open" |
| a Follow button was added under the handle with its own width, radius and spacing, and the owner asked for the whole page to be designed | the end card is one lockup: edges flush, the mark's corners, equal spaces on the ink; options shown in motion with sound | 08 "A call to follow is one designed lockup" |
| a bite's picture was cut where its speaker stopped, but the bed still came back on the narrator's next word: the new picture played over 0.23 s of silence | after a bite the bed returns on the cut away from it | 05 "The music fits the cut" |
| two bites trimmed by 0.17 s moved the bed 60 ms and the hook's beat-led cuts fell off their beats | a beat window wide enough to outlast the clock's small moves (0.27 s), re-derived after any clock change | 05 "The music fits the cut"; 08 "A change to the clock" |
| widening the beat window moved five cuts and two caption pages left before their last word | list every time a rule change moves and check its dependents; the caption sync script | 08; 09 "In sync, by measurement" |
| an earlier film's bite subtitles, set by ear, ran up to 0.1 s late and 0.24 s early; found only when the owner asked | subtitle lines timed from forced alignment and the waveform; a sync rule set on one film measured on all of them the same day | 09 "In sync, by measurement" |
| a correspondent was named by our credit and by the channel's own lower third at once | no credit of our own where the broadcaster's caption names the speaker | 07 "A broadcaster's caption" |
| white captions on near-white web pages read as nothing | captions moved to the black or the shot's dark area | 09 "Captions on light footage" |
| four white documents cut in from the black page were the film's hardest jolts | white pages at about 0.9 brightness on a dark film | 07 "Documents" |
| a re-alignment after a late re-voice moved five earlier words by 0.02 s | the words before a re-voiced phrase keep the rendered times | 04 |
| the bed stopped on the beat tracker's beats, 30 to 50 ms after the hits' attacks: every stop chopped the next hit, a pop the owner heard after "He walked away." | cut at the attack found on the take, 4 ms before it, with a fade; a stab rings out | 05 "The music fits the cut" |
