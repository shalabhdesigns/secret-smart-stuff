# GTA 6 learnings: what works, with numbers

Owner, 20 Nov 2026: learn only from our GTA videos; no generic, repeated observations; every finding must change
the next videos; identifying patterns and improving is Claude's job, not the owner's.

## How this file works (Claude's daily run follows it)
1. Refresh the numbers: `git show origin/state:state/live.db > /tmp/live.db && python3 scripts/gta_learn.py /tmp/live.db`
   (fills "Numbers" below; GTA videos only; no API cost).
2. Judge every **running experiment** whose videos have 24 h numbers: compare its videos with the control
   (same days, other videos) on IG views 24h first, then YT views 24h, IG avg watch seconds and IG skip rate.
   Write the result with the numbers and a decision: **adopt** (becomes a rule below), **drop**, or **extend**
   (not enough videos yet; say how many more).
3. Start 1-2 new experiments for tomorrow: one clear change, a hypothesis with a number, which of tomorrow's
   5 videos get it (set `experiment="E<n>"` in their scripts) and which don't. Never more than 2 at once.
4. Apply every adopted rule to tomorrow's scripts.
5. Rules: a learning without a number, or one that changed nothing, is deleted, not repeated. Never compare with
   the old product videos. Small samples (n < 3 per side) are "extend", not "adopt".

## What the numbers say so far (27 Nov 07:20 UTC, 48 of 53 GTA videos with 24 h numbers)
(F1-F4 deleted 21 Nov; F5 deleted 24 Nov: E3 tested it and is now rule R7.)

- F6 Full analysis (21 Nov 04:18 UTC, all 23 GTA videos; IG + YT live counts; table in the owner report):
  - Version decides most: story + real logo (7 videos, 19-21 Nov) median 1,471 IG views vs 346 (old format, 11)
    and 382 (story without logo, 4). Watch time 19-28 s vs 9-16 s; skip 21-33 % vs 27-44 %. Every IG share
    (13 of 14) and most saves came from the logo videos.
  - Cover picture: a clear Lucia/Jason face (Lucia 1,583; cast 1,267; masked Lucia covers 1,4xx) beats faceless
    covers. The one logo video with a dark car cover (PC v3) got 739, half the others. Faceless covers before the
    logo were mostly 135-350.
  - Topic: characters, records (biggest launches 1,389; review scores 1,471), real world / practical (Tokyo
    1,647; real places 1,470; India price 1,531) and "does it affect me" tech (PS5 1,357) win. Events (NBA 198),
    launch timing (184), timelines (192) and trailer trivia (135) lose. Same as F3, now on 23 videos.
  - Shares and saves come from practical / real-world facts (Tokyo 4+4, real places 4+2, India 3).
  - Comments: ~0 on Instagram everywhere. YouTube: PC v3 got 13 (PC vs console argument) - a side-taking
    question gets comments; a neutral one does not.
  - YouTube: either ~1.0-1.2k or under 400. All 4 videos at 23:00 UTC were under 210 (E3 moves that slot).
    In the logo era every non-23:00 video reached ~1.1k except leak-war (381).
  - Followers: IG 8 total from ~25k views (E2 tests a follow line). YT subscribers 15 -> 49.
  - Length: the 50-65 s story videos hold 19-28 s average watch; E1 still tests 40 s.

- F7 Instagram reach is mostly decided in the first ~6 hours, but not always (21 Nov; corrected 22 Nov):
  real places 1,452 at 5.7 h -> 1,470 at 26 h (99 %); Florida videos 1,271 at 6.7 h -> 1,280 at 41 h. But PC v3 went
  467 at 3.7 h -> 739 at 11 h -> 1,219 at 24 h (+65 % after 11 h).
  Change (22 Nov): judge experiments on 24 h Instagram numbers; a 6 h number is only a preview, never a verdict.
- F8 News made a script wrong before it went out (21 Nov): tonight's "19 million? Here's the catch" video said
  "Take-Two hasn't confirmed a single sales number"; Rockstar published official numbers on 20 Nov ($3.79B day one,
  32.5M copies pre-release). Change: every daily run re-checks the facts of that day's not-yet-public videos
  against the newest news; tonight's 23:00 UTC slot gets a remake with the official numbers.

- F9 Face covers vs no face, 21 Nov batch (IG views, ages 5-17 h): the 3 videos with a big Lucia/Jason face on the
  cover got 1,650 (story length, Lucia in prison orange, 11 h), 1,485 (2021 first look, Lucia close-up, 5 h) and
  1,396 (official sales, Jason at the marina, 8 h). The 2 covers made before R3 without one got 152 (stream record,
  wide jet-ski shot, 17 h) and 340 (Dexter, a masked stranger, 14 h; skip 47 %, watch 12 s). 4-10x. Topic also
  differs (a viewer-count record is event-like; F6), so both count.
  Change: R3 tightened (big face of Lucia or Jason only; no wide shots, no strangers, no masks hiding the face);
  R2 adds viewer/stream-count records to the "avoid" list.
- F10 A huge official number with a famous comparison gets shared (22 Nov): official sales ($3.79B day one, beats
  Avengers: Endgame) got 14 IG shares in 8 h - the most ever (old best 4: Tokyo, real places) - and 29.4 s watch.
  Watch time also jumped on the newest videos: 29.1-30.5 s (story length, official sales, 2021 first look) vs
  19-28 s before. Change: R5 widened: each batch has 1 video built on one big hard number set against something
  everyone knows (23 Nov: critics 99 vs players 5.6 vs Zelda; map about 2x GTA 5).
- F11 YouTube slots (22 Nov): 23:00 UTC stayed weak - official sales 188 YT at 8 h vs 1,396 IG; the replaced 19M
  video 221. 02:00 is mixed: Trailer 2 284 at 24 h (22 % of IG) vs real places 1,040 (71 %) and 2021 first look 912
  at 5 h. 20:00: story length 1,199 YT at 11 h. Change: none yet (E3 already moved 23:00 to 12:00); if 02:00 stays
  under 40 % on 22-24 Nov, test moving it too.
- F12 Every one of the 5 morning scripts on 22 Nov was held by the script check (5 of 5; then 2 + 3 more holds on the
  remakes), mostly for one wording each: the E2 follow line "a new GTA 6 secret every day" (unsourced promise, all
  5), a hedge dropped ("seems quite as big"), "Florida rapper", "Bigfoot is real". Change: follow line is now
  "Follow for more GTA 6 secrets/facts/tips" (no promise); keep every hedge word of the source; describe in-game
  things as in-game ("players have spotted Bigfoot in the game").

- F13 Characters + a relationship question win YouTube and shares (23 Nov): "Is dating Lucia cheating?" got 1,891
  YouTube views (140 % of its 1,347 IG views; the best YT result of any GTA video) and 6 IG shares (2nd best after
  official sales' 14). Console-best: 1,434 IG, 980 YT, 4 shares, 28.2 s watch. Change: each batch keeps >= 1 character
  video with a question that splits viewers on the character (24 Nov: Jason's Army past, "pushed by money or wired
  that way?").
- F14 Lists of small secrets hold viewers worst (23 Nov): weird-secrets 13.5 s average watch, 39 % skip; Kodak radio
  (posters to find) 12.8 s, 36.5 % - vs 22-28 s and 22-32 % for the other three 22 Nov videos. Reach was still
  1,223-1,426. Change: a secret video tells ONE secret as a story with a payoff (24 Nov: Mount Chiliad), never a
  list; how-to steps stay at 3 short beats (24 Nov: Xbox glitch).
- F15 Face covers keep working (23 Nov): all 5 face covers of 22 Nov reached 1,223-1,602 IG views; no video with a
  face cover has fallen under 1,200 IG views (faceless/masked covers: 152, 340). R3 holds.
- F16 Wrong shot descriptions cause most holds after rendering (23 Nov): 4 of 5 remakes rendered today were held by
  the final check for a picture that showed something else - all traced to wrong descriptions (00961 "Lucia" = her
  back; 00920 "dancing" = a scuffle; 00000 = the age-rating card; v_7f4ce4e75d = a stranger; 07899 "a man" = Jason).
  Each costs a ~$0.07 render. Change: 7 descriptions fixed from frames, 00000 marked avoid; a shot not seen in a
  rendered video is previewed with `shotframes` before use. And 10 of 10 morning scripts on 22-23 Nov were held by the
  paid script check for one word stronger than the source; gta_scripts.py now flags (free) absolute words and years
  that no fact claim contains.

- F17 Lucia wins biggest (24 Nov): "Lucia's actress was in GTA 5" got 2,252 IG views at 12 h - the best GTA video
  ever (old best 1,658) - with 30.9 s watch, 21 % skip, 13 saves and 1,632 YouTube views at 12 h. "Is dating Lucia
  cheating?" holds the best YouTube result (1,891 at 24 h; 2,267 now). The other 23 Nov videos: 1,315-1,694 IG.
  Change: E4 tests Lucia's name in the title + a Lucia face cover (25 Nov: lucia-liberty).
- F18 Step-by-step unlock videos get saved (24 Nov): Kodak radio ("how to unlock it") got 48 IG saves; every other
  GTA video got 0-13. Saves are a strong Instagram signal. Change: the practical slot (R5) is a how-to with clear
  steps whenever the news gives one (24 Nov Xbox 60 fps; 25 Nov money glitch).
- F19 YouTube looked slow for the 23 Nov 14:00/17:00/20:00 videos at 4-10 h (map 52, online mode 28, Zelda 106 YT
  vs 1,315-1,694 IG) while the 12:00 video had 1,632 at 12 h. Preview only (F7): judged at 24 h tomorrow. If 2 days
  in a row the non-12:00 videos stay under 30 % of their IG views on YouTube at 24 h, test 4 uploads a day instead
  of 5 (YouTube may be splitting one day's audience across too many uploads).
- F20 Followers are stuck (24 Nov): Instagram 10 followers on 22, 23 and 24 Nov after ~14,000 views (0 per 1,000);
  YouTube subscribers 49 (21 Nov) -> 58 (24 Nov). Views grow, follows don't. The follow line (E2) did not help.
  Change: nothing yet; the next follower test needs a reason to follow (a series), planned once E4 ends.

- F21 Every 24 Nov video beat the 23 Nov batch on Instagram (25 Nov): Cheetah 1,838, Chiliad 1,813, Jason's Army
  1,705, Xbox glitch 1,578 IG views at 3-11 h vs a 23 Nov median of 1,456 at 24 h. Lucia's actress ended at 2,259 at
  24 h (best ever; 1,856 on YouTube = 82 %). Change: the 26 Nov batch keeps the same mix (1 Lucia, 1 big official
  number, how-tos, 1 secret told as one story).
- F22 "Where to find it / how to do it" videos get saved (25 Nov): Kodak radio 48 saves, egg tower 25, Lucia's
  actress 13, Chiliad 11; all other 23-24 Nov videos 0-6. Shares fell to 0-2 a video on 24 Nov (14 on official
  sales). Change: 3 of 5 videos on 26 Nov are step-by-step how-tos (Lucia's magazine looks, car tools, keeping your
  cash) and 1 is a find-it secret with 3 numbered steps (Mario-style caps); steps go in numbered callouts.
- F23 YouTube at 24 h, 23 Nov non-12:00 videos: map 62 (4 % of IG), online mode 616 (36 %), Zelda 459 (34 %), egg
  tower 319 (25 %); 12:00 Lucia actress 1,856 (82 %). YouTube day totals at 24 h fell from 5,807 (22 Nov) to 3,312
  (23 Nov). 24 Nov preview: the 12:00 video (Xbox) had only 101 at 19 h, so the slot alone is not the reason.
  F19's trigger (2 days in a row under 30 %) is not met (2 of 4 were 34-36 %). Change: none yet; judge the 24 Nov
  batch at 24 h tomorrow; if its non-12:00 median is under 30 %, test 4 uploads a day (E5).
- F24 Wrong shot facts caused today's only remake (25 Nov): lucia-liberty opened on extended_look_09026 (2.7 s), the
  5 s hook ran on into a stranger in glasses for 2.5 s, and its cover (08816) was too dark to see Lucia. Remade for
  $0.06 before upload. extended_look_10196 has opened 8 GTA videos and was a cover on 21 and 25 Nov. Change: 15
  shots previewed with shotframes today and their descriptions corrected (2 "Jason/Lucia" shots are strangers);
  the 26 Nov batch opens on 5 different shots, none of them 10196.

- F25 YouTube views often come after 24 h (26 Nov): Jason's Army 267 YT at 24 h -> 1,012 now; online mode 616 -> 970;
  map 62 -> 246; dating Lucia 1,891 -> 2,702. Instagram stays flat after 24 h (+0-1 %). F19/F23 trigger checked on the
  24 Nov batch: non-12:00 videos got 16 % (Army), 62 % (Cheetah), 77 % (Chiliad), 24 % (outsold) of their IG views on
  YouTube at 24 h - median 43 %, over the 30 % bar. Change: no "4 uploads a day" test (5 a day stays); YouTube numbers
  in experiments are read at 48 h, not 24 h.
- F26 The 3 best Instagram videos all hook on an older GTA (26 Nov): Lucia's actress was in GTA 5 2,259; the real
  Cheetah (a classic GTA car) 1,868; GTA 5's Mount Chiliad mystery 1,836 - vs 1,262-1,708 for the other 10 videos of
  23-24 Nov at 24 h (median 1,457). Saves too: Chiliad 11, Lucia's actress 13. Change: E5 tests it (27 Nov: GTA 6
  cut GTA 5's tennis; GTA 4's Niko in GTA 6).
- F27 Two of five 26 Nov covers showed no face (26 Nov): extended_look_10330 at f 0.2 = a basketball hoop with
  Jason's face under the logo; trailer_1_00604 at f 0.8 = a car interior. Both were "25 Nov preview" entries. A third
  try, extended_look_02968 at f 0.2, was too dark. Fixed before upload with launch_trailer_00119 (Jason on the
  phone, bright) and launch_trailer_00263 (Lucia at a red convertible). Change: 10330 and 00604 removed from `faces`;
  the face list is now used up for the week (27 Nov covers reuse 21-23 Nov shots), so the next run previews new
  face shots with `shotframes` (or a still from the catalogue) before picking covers.

- F28 Sales-number videos have worn out (27 Nov): official sales (21 Nov) 1,407 IG and 14 shares; then analyst and
  platform numbers fell each time: outsold consoles 1,423 (25 Nov), 44.9M analyst 957 IG / 135 YT, Sony's PlayStation
  record 213 IG / 49 YT at ~17 h (the lowest of any logo-era video; same day: 1,475-1,644 IG). It had a face cover
  (Jason on the phone), so the topic, not the cover, failed. Change: no sales / launch-number videos (analyst,
  Sony, "outsold") until Rockstar or Take-Two publish a new number; R5's "big number" slot is dropped; R2 tightened.
- F29 Lucia never flops, but her name does not add a lift (27 Nov, E4 dropped): Lucia from Liberty City 1,599 IG and
  Lucia's magazine looks 1,644 IG were +5 % and +11 % over their days (bar +25 %). But they are steady: the 5 Lucia
  videos since 23 Nov got 1,599-2,259 IG, and the best YouTube share of IG (77-108 %; magazine looks 1,783 YT).
  Change: each batch keeps >= 2 Jason/Lucia character videos (28 Nov: ages, four heroes, break-up); Lucia's name in
  the title is no longer required.
- F30 Step videos are saved but not watched (27 Nov): Mario caps (3 steps to find) 11.7 s average watch and 31 %
  skip, but 21 saves; magazine looks 17.7 s, 31 saves; money glitch 26.1 s, 17 saves; car tools 26.2 s, 8 saves. The
  ones that tell a story around the steps (a catch, a "why") hold about twice as long. Change: a how-to has at most 3
  numbered steps and then a catch or a pro move as its payoff (28 Nov snap gun: the alarm catch + the back-door move).
- F31 The `faces` list was used up; official character stills are a new pool (27 Nov): only 3 unused face shots
  were left for 22-28 Nov, all dark or masked. `shotframes` now previews catalogue stills too: 15 previewed, 9 put a
  big face above the logo (Jason_Duval_01/02/07/08/15, Lucia_Caminos_06/07/09/12); wide Jason-and-Lucia stills put
  both faces under the logo (unusable); Jason_Duval_07's eyes sat under the logo. Today's lucia-svu and pc-port
  covers were moved to stills (the old ones repeated 22-23 Nov pictures; lucia-svu's face sat under the logo). A
  cover can now be `{"image": "imgN", "zone": "lower"}` for a still in the video. Change: E6 tests still covers.

## Adopted rules (proven on our GTA numbers)
- R1 (20 Nov): real GTA VI logo on the cover and first screen + story format (F1).
- R2 (20 Nov): favour character, "does this affect me" (price/console/storage) and record topics; avoid event and
  trailer-trivia topics (F3). Re-check when 10 more videos have numbers.
  Confirmed 21 Nov on 23 videos (F6): every daily batch has >= 3 of 5 from characters / records / real-world
  practical / "does it affect me"; at most 1 news/drama; no events, timelines or trailer trivia.
  22 Nov (F9): viewer/stream-count records count as events (stream record 152 IG views): avoid.
  Tightened 27 Nov (F28): sales / launch-number records (analyst estimates, platform records, "outsold") are out
  until an official new number (213-957 IG for the last two). Characters stay first (F29).
- R3 (21 Nov): cover picture = a clear Lucia or Jason face (or masked Lucia) from `faces` in
  `assets/official/attention_shots.json`; no faceless covers (cars, buildings, scenery, crowds). Never the same
  face shot two days running (F6).
  Re-checked 21 Nov 07:12 UTC: holds (faceless PC v3 739 vs face covers 1,267-1,647). The `faces` list now has
  16 checked shots (5 added 21 Nov), enough to rotate a full week without a repeat.
  Tightened 22 Nov (F9): the face must be big and clear (close or medium shot of Lucia or Jason); covers with a
  wide shot or a masked stranger got 152 and 340 vs 1,396-1,650 with a face.
  Re-checked 23 Nov (F15): holds (22 Nov face covers 1,223-1,602). 4 new checked face shots (19 in total; one wrong
  entry removed: trailer_2_00961 shows Lucia's back).
  Re-checked 25 Nov: holds (24 Nov face covers 1,578-1,838 IG). Tightened: a face shot is previewed with
  `shotframes` before its first use as a cover (25 Nov: 08816 at f 0.5 was too dark; 2 listed "Jason" shots were
  strangers). 4 new checked face shots; 08816 removed.
  Re-checked 24 Nov: holds (23 Nov face covers 1,315-2,252 IG). Tightened: the face must be lit and sit in the top
  ~40 % of the cover (the logo sits in the middle); 2 of 24 Nov's covers were fixed before going out (a dark face
  half under the logo; the back of Lucia's head at f 0.2). 9 new checked face shots (28 in total).
  Re-checked 26 Nov: holds (24 Nov face covers 1,423-1,868 IG at 24 h). Tightened (F27): every cover is looked at
  after rendering; a "preview" entry is not proof (2 of 5 failed). 2 entries removed (26 in the list).
  Re-checked 27 Nov: holds (26 Nov face covers 1,475-1,644 IG; the 213 was the topic, F28). Widened (F31): an
  official Jason/Lucia still with the face above the logo may be the cover (previewed with `shotframes`).
- R4 (21 Nov): the last beat asks a side-taking question that splits viewers ("PS5 or PC - which side are you
  on?"), never a neutral "what do you think?" (F6: 13 YT comments on the PC vs console video vs ~0 elsewhere).
- R5 (21 Nov): at least 1 of 5 daily videos is a practical / real-world fact viewers save or send (price in
  rupees/dollars, size, where places are in real life, what console you need) - these get all the shares (F6).
  Widened 22 Nov (F10): plus 1 video on one big hard number set against something famous (14 shares in 8 h).
  Dropped 27 Nov (F28): the "big number" video (957 and 213 IG for the last two).
  Tightened 25 Nov (F22): the practical videos are step-by-step how-tos with numbered callouts whenever the
  sources give steps (saves: how-to/find-it 11-48 vs 0-6 for the rest).
  Re-checked 26 Nov: holds (money glitch how-to 17 saves at 8 h vs 0-3 for the other 25 Nov videos).
  Re-checked 27 Nov: holds (26 Nov how-tos 8-31 saves vs 0 for the record video). Tightened (F30): max 3 steps, then
  a catch or pro move.
- R6 (23 Nov, F14): a secret video is ONE secret told as a story, never a list of finds (lists: 12.8-13.5 s
  watch vs 22-28 s).
  Re-checked 25 Nov: holds (one-secret Chiliad 26.0 s watch, 1,813 IG; egg tower 15.9 s, 25 saves).
- R7 (24 Nov, E3): no 23:00 UTC slot; slots 12:00, 14:00, 17:00, 20:00, 02:00 UTC. The 12:00 videos got 68-75 % of
  their IG views on YouTube (n=3) vs 5-36 % at 23:00 (n=7).
  Re-checked 26 Nov: 4 of 5 12:00 videos 68-82 %; the Xbox glitch (24 Nov) got 10 % at 24 h (304 now; F25). Holds.
- Length (24 Nov, E1 dropped): story videos stay 110-170 words (50-65 s); 40 s versions got no more views (+1 %)
  and fewer watch seconds (median 17.7 s vs 26.2 s).

## Experiments log
<!-- 27 Nov: E4 DROPPED (+5 %, +11 %; bar +25 %). E5 extended (its first videos publish today). New: E6 (still covers). 28 Nov batch: E5 test = ages (12:00), four-heroes (14:00); E6 test = all five 28 Nov + 27 Nov lucia-svu, pc-port; E6 control = 27 Nov cut-tennis, black-friday, niko-cameo + the 26 Nov batch (clip-frame face covers). -->
<!-- 26 Nov: E4 extended (no 24 h numbers; preview below). New: E5 (older-GTA hook). 27 Nov batch: E4 test = lucia-svu (12:00); E5 test = cut-tennis (14:00), niko-cameo (20:00); E5 control = black-friday (17:00), pc-port (02:00). -->
<!-- 25 Nov: E4 not judged yet (its first video, lucia-liberty, publishes 25 Nov 12:00 UTC; remade this morning: the opening shot ran on into a stranger). No new experiment: no per-video follower number exists to test F20 fairly, and E5 (4 uploads a day) waits for the 24 Nov YouTube numbers (F23). 26 Nov batch: E4 test = lucia-looks (12:00); control = ps-record, steal-cars, mario-caps, lose-cash. -->
<!-- 24 Nov: E1 dropped, E3 adopted (R7). New: E4 (Lucia). 25 Nov batch: E4 test = lucia-liberty (12:00); control = money-glitch, jason-landlord, 44-million, fortnite-drop. -->
<!-- 23 Nov: E2 dropped (numbers below). E1 and E3 extended. No new experiment: 2 running. 24 Nov batch: E1 short = xbox-60fps (12:00), real-cheetah (17:00); long = jason-army, chiliad-secret, outsold-consoles; E3: xbox-60fps at 12:00 UTC. -->
<!-- 22 Nov: E1-E3 not judged yet - their first videos publish tonight (22 Nov batch, all 5 remade this morning after the script check). No new experiment: 3 are running (the max is 2; none is added until one ends). 23 Nov batch: E1 test = map-size (14:00), zelda-score (20:00); control = lucia-actor, online-when, egg-tower; E2: all five; E3: lucia-actor at 12:00 UTC. -->
<!-- 21 Nov: E1-E3 not judged yet - their first videos are the 22 Nov batch (E1 test: kodak-radio, true-fat-jason; control: console-best, dating-lucia, weird-secrets; E2: all five; E3: console-best at 12:00 UTC). No new experiment: 3 are running. -->
<!-- newest first: E<n> | started | change | hypothesis | videos (test / control) | result with numbers | decision -->
- E6 | from 27 Nov | cover = an official Jason/Lucia character still (big, sharp face above the logo) instead of a
  trailer frame | still-cover videos get >= 10 % more IG views at 24 h than clip-frame face covers | test: 27 Nov
  lucia-svu, pc-port; 28 Nov ages, four-heroes, snap-gun, break-up, patch-fix | control: 27 Nov cut-tennis,
  black-friday, niko-cameo; 26 Nov batch excluding ps-record (topic flop, F28) | result: pending | decision: pending
  (judge on 29 Nov with n=7 vs 7; adopt if the median gap is >= 10 % and no still cover is under 1,200 IG)
- E5 | from 27 Nov | the video's hook is a link to an older GTA (a GTA 4/5 character, place, activity or mystery in
  GTA 6) | E5 videos get >= 15 % more IG views at 24 h than the same day's non-E5, non-E4 videos (F26: 1,836-2,259 vs
  median 1,457) | test: 27 Nov cut-tennis, niko-cameo; control: black-friday, pc-port | result: pending | decision:
  pending (2 more test videos on 28 Nov; adopt at n=4 if the median gap is >= 15 %)
  27 Nov: no numbers yet (test videos publish 27 Nov 14:00 and 20:00 UTC) -> EXTEND. 28 Nov test: ages (Lucia's
  licence from GTA 4's Liberty City), four-heroes (GTA 5's three); control: snap-gun, break-up, patch-fix.
- E4 | from 25 Nov | Lucia's name in the title + a clear Lucia face on the cover, 1 video a day | the Lucia video gets
  >= 25 % more IG views at 24 h than the median of the same day's other 4 videos (F17: Lucia actress 2,252 vs
  1,315-1,694) | test: 25 Nov lucia-liberty (then 1 a day on 26-27 Nov); control: the same day's other videos |
  result: pending | decision: pending (adopt at n=3 if all 3 beat their day by >= 25 %)
  25 Nov: no 24 h numbers yet (first test video publishes 25 Nov 12:00 UTC) -> EXTEND. 26 Nov test: lucia-looks
  (Lucia in the title, Lucia prison-orange face cover); 27 Nov: one more, then judge on 28 Nov.
  26 Nov: still no 24 h numbers. Preview: lucia-liberty 1,592 IG at 10 h vs same-day Jason's landlord 1,797 at 5 h
  and money glitch 1,533 at 8 h - not ahead so far. -> EXTEND. 27 Nov test: lucia-svu (Lucia's actress on Law &
  Order); judge all 3 on 28 Nov.
  27 Nov (judged a day early: adopting needs all 3 at +25 % and 2 of 2 already missed): lucia-liberty 1,599 IG vs
  the 25 Nov median 1,518 (+5 %); lucia-looks 1,644 vs the 26 Nov median 1,489 (+11 %; ps-record 213, steal-cars
  1,536, mario-caps 1,475, lose-cash 1,489). Watch 22.2 / 17.7 s vs 21-39 s. -> DROP. Kept (F29): Lucia videos are
  steady (never under 1,599) and win YouTube (1,234 / 1,783 YT), so characters stay first in R2.
- E3 | from 22 Nov | slots 12:00, 14:00, 17:00, 20:00, 02:00 UTC (the 23:00 slot moves to 12:00 = 17:30 IST; config
  gta_slots) | the 12:00 video gets >= 50 % of its Instagram views on YouTube at 24 h, like the other slots, while the
  23:00 videos got 5-36 % | 22-24 Nov 12:00 videos vs 19-21 Nov 23:00 videos, same metric | result: pending |
  decision: pending (if adopted, keep 23:00 out; if not, go back)
  23 Nov: 12:00 videos so far: India price 1,147 YT / 1,532 IG (75 %), console-best 980 / 1,434 (68 %) vs 23:00
  videos 5-36 %. n=2 -> EXTEND 2 more days (lucia-actor 23 Nov, xbox-60fps 24 Nov), then adopt if >= 50 % holds.
  24 Nov: lucia-actor (12:00, 23 Nov) 1,632 YT / 2,252 IG = 72 % at 12 h. n=3, all >= 68 % vs 5-36 % at 23:00 ->
  ADOPTED (rule R7). gta_slots unchanged.
- E2 | from 22 Nov scripts | every video's last beat ends with a follow line after the comment question, e.g.
  "Follow for more GTA 6 secrets." (22 Nov: "every day" dropped, the script check called it an unsourced promise) | Instagram followers per 1,000 Reel views rise from ~0.1 (19-21 Nov)
  to 1+ | all videos 22-24 Nov vs 19-21 Nov (account-level: daily follower and subscriber gain per 1,000 views) |
  result (23 Nov): IG followers 9 -> 10 on 22 Nov from 7,327 views = 0.14 per 1,000 (19-21 Nov: 0.15-0.31); the
  line was also behind 5 of 10 script-check holds on 22 Nov | decision: DROP (no lift). Follow lines removed from the
  24 Nov scripts; the last line is the side-taking question.
- E1 | from 22 Nov scripts | length: 2 of the 5 daily videos 100-115 words (~40 s), 3 at 140-165 words (~55 s);
  alternate which slots get the short ones each day | the short ones get >= 20 % more Instagram views at 24 h with
  a lower skip rate | test = short ones, control = long ones, same days | result: pending | decision: pending
  23 Nov (22 Nov videos, most not yet 24 h): short Kodak 1,426 / fat Jason 1,602 IG (median 1,514) vs long 1,434 /
  1,347 / 1,223 (median 1,347): +12 %, under the +20 % bar; skip short 36.5 / 28.0 % vs long 21.6-39 %. n=2 vs 3
  -> EXTEND (23 + 24 Nov add 4 short, 6 long); judge on 25 Nov.
  24 Nov (judged a day early: n=4 vs 5 is enough and the gap is tiny): short Kodak 1,435, fat Jason 1,635, map 1,454
  (10 h), Zelda 1,315 (4 h) - median 1,445; long console 1,434, dating 1,347, weird 1,229, Lucia actor 2,252 (12 h),
  online 1,694 (7 h) - median 1,434. +1 % (bar +20 %). Watch: short median 17.7 s vs long 26.2 s. -> DROP. Back to
  110-170 words for all; the 24 Nov short ones are already made.

## Numbers

<!-- AUTO:START -->
_Numbers updated 2026-11-27 07:20 UTC by scripts/gta_learn.py (GTA videos only; no API cost)._

**Accounts:** youtube 71 (first seen 15); instagram 10 (first seen 1)

| published (UTC) | video | cat | logo | s | IG 24h | IG now | IG watch s | IG skip % | IG shares | YT 24h | YT now | YT % viewed | exp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11-16T17:00 | GTA 6 still isn't on PC. Here's why | tech | - | 29.2 | 1401 | 1401 | 13.0 | 33.5 | - | - | 4 | 90.37 |  |
| 11-16T20:00 | GTA 6 at $80 is cheaper than GTA 5 was | money | - | - | 242 | 243 | 15.3 | 33.2 | - | - | 10 | 96.16 |  |
| 11-16T23:00 | GTA 6's wildest scenes match real Florida videos | real world | - | 31.6 | 174 | 174 | 11.6 | 39.3 | - | - | 35 | 53.55 |  |
| 11-17T02:00 | The GTA 6 trailer that broke YouTube | other | - | 34.7 | 133 | 135 | 11.5 | 42 | - | - | 1158 | 73.96 |  |
| 11-17T17:00 | 27 minutes of GTA 6 gameplay: what nobody notice | other | - | 27.5 | 426 | 430 | 9.0 | 36.9 | 1 | - | 45 | 68.91 |  |
| 11-17T20:00 | GTA 6 took 13 years. Here's what happened | other | - | 42.2 | 191 | 192 | 11.1 | 43.1 | - | - | 243 | 46.03 |  |
| 11-17T23:00 | Will GTA 6 even fit on your PS5? | tech | - | 34.4 | 1354 | 1357 | 16.4 | 26.6 | - | - | 152 | 51.85999999999999 |  |
| 11-18T02:00 | Lucia is the GTA hero we waited 29 years for | characters | - | 31.6 | 1470 | 1646 | 14.4 | 30.7 | - | - | 1295 | 52.09 |  |
| 11-18T11:00 | Is the $100 GTA 6 Ultimate Edition worth it? | money | - | 38.4 | 307 | 347 | 14.8 | 44.6 | - | 1 | 185 | 58.21999999999999 |  |
| 11-18T14:00 | Why an NBA team becomes 'Vice City' tonight | real world | - | - | 171 | 199 | 13.2 | 31 | - | 2 | 332 | 105.88 |  |
| 11-18T17:00 | GTA 6 is already unlocked in these countries | tech | - | 57.1 | 183 | 185 | 16.2 | 30.9 | - | 1 | 173 | 47.96 |  |
| 11-18T23:00 | Why the GTA 6 box has no disc inside | tech | - | 47.2 | 557 | 567 | 18.8 | 32 | - | - | 201 | 61.59 |  |
| 11-19T14:00 | The GTA 5 record GTA 6 has to beat | records | - | - | 1386 | 1391 | 22.5 | 30.2 | - | 1077 | 1044 | 102.27 |  |
| 11-19T20:00 | GTA 6: Rockstar's war on the leakers | drama | Y | - | 1339 | 1346 | 25.9 | 33.3 | - | 295 | 856 | 79.59 |  |
| 11-19T23:00 | GTA 6 is in America, but Tokyo nearly won, says  | real world | Y | - | 1647 | 1651 | 28.0 | 27.8 | 4 | 73 | 779 | 52.839999999999996 |  |
| 11-20T02:00 | GTA 6's map: the real places it looks like | real world | Y | - | 1470 | 1476 | 27.0 | 23.1 | 4 | 1040 | 1022 | 58.62 |  |
| 11-20T12:00 | GTA 6 costs double GTA 5 in India, but there's a | money | Y | - | 1532 | 1536 | 28.5 | 21.1 | 3 | 1147 | 1256 | 64.4 |  |
| 11-20T14:00 | GTA 6's wildest scenes match real Florida videos | real world | Y | - | 1278 | 1282 | 19.6 | 25.6 | - | 1132 | 1204 | 55.279999999999994 |  |
| 11-20T17:00 | GTA 6 still isn't on PC. Here's why | tech | Y | - | 1219 | 1223 | 19.9 | 21.3 | 1 | 1147 | 1042 | 60.74 |  |
| 11-20T20:00 | GTA 6 tied the highest Metacritic score ever | records | Y | 56.6 | 1484 | 1485 | 20.0 | 25.9 | 1 | 1129 | 1134 | 68.31 |  |
| 11-20T23:00 | GTA 6's characters in Rockstar's own words | characters | Y | - | 1327 | 1333 | 25.6 | 27.8 | - | 485 | 952 | 54.120000000000005 |  |
| 11-21T02:00 | GTA 6 Trailer 2: 475 million views in a day? | records | Y | - | 1292 | 1318 | 19.1 | 32.4 | - | 284 | 308 | 50.64999999999999 |  |
| 11-21T14:00 | GTA 6 launch: 7.9 million people watching at onc | records | Y | - | 153 | 153 | 14.1 | 20.8 | - | 427 | 676 | 46.22 |  |
| 11-21T17:00 | GTA 6 fans found Dexter's apartment in Vice City | real world | Y | - | 630 | 631 | 14.5 | 41.4 | - | 670 | 767 | 54.400000000000006 |  |
| 11-21T20:00 | GTA 6 is about 50 hours long, one review says | reviews | Y | - | 1658 | 1658 | 29.2 | 27.6 | - | 1318 | 1357 | 75.5 |  |
| 11-21T23:00 | GTA 6 sold 19 million copies? Here's the catch | records | Y | - | - | - | - | - | - | 240 | 412 | 44.25 |  |
| 11-21T23:00 | GTA 6 made $3.79 billion on day one, Rockstar sa | money | Y | 60.2 | 1407 | 1408 | 29.5 | 29.9 | 14 | 263 | 436 | 54.79999999999999 |  |
| 11-22T02:00 | GTA 6 fans think we saw it back in 2021 | other | Y | - | 1497 | 1498 | 30.2 | 22 | - | 1036 | 1124 | 63.99 |  |
| 11-22T12:00 | GTA 6 runs best on one console. Here's which | tech | Y | 58.0 | 1434 | 1435 | 28.2 | 21.6 | 4 | 980 | 1016 | 61.11 | E1-long |
| 11-22T14:00 | Is dating Lucia in GTA 6 cheating? Couples disag | characters | Y | - | 1347 | 1356 | 22.2 | 31.9 | 6 | 1891 | 2927 | 70.58 | E1-long |
| 11-22T17:00 | GTA 6 has a secret Kodak Black radio station | other | Y | - | 1435 | 1451 | 12.6 | 37.1 | 1 | 1408 | 1529 | 86.07 | E1-short |
| 11-22T20:00 | GTA 6's weirdest secrets players found in week o | other | Y | - | 1229 | 1230 | 13.4 | 39.2 | 3 | 717 | 978 | 61.84 | E1-long |
| 11-23T02:00 | GTA 6 players are trying to make Jason fat | characters | Y | - | 1635 | 1635 | 23.1 | 28.1 | 1 | 811 | 1211 | 76.36 | E1-short |
| 11-23T12:00 | GTA 6's Lucia actress was in GTA 5 all along | characters | Y | - | 2259 | 2280 | 30.8 | 21.2 | 3 | 1856 | 2027 | 65.66 | E1-long |
| 11-23T14:00 | GTA 6's map vs GTA 5: how big is it really? | real world | Y | - | 1456 | 1464 | 17.3 | 26.4 | 2 | 62 | 246 | 61.68 | E1-short |
| 11-23T17:00 | GTA 6 has no online mode. When is it coming? | other | Y | - | 1708 | 1712 | 26.0 | 27.3 | - | 616 | 975 | 66.85 | E1-long |
| 11-23T20:00 | GTA 6's Metacritic fight just dragged in Zelda | reviews | Y | - | 1338 | 1339 | 18.1 | 34.8 | 1 | 459 | 627 | 56.330000000000005 | E1-short |
| 11-24T02:00 | GTA 6 hid a real Easter egg at the top of a towe | real world | Y | - | 1262 | 1268 | 15.9 | 35.4 | - | 319 | 415 | 43.33 | E1-long |
| 11-24T12:00 | GTA 6's Xbox glitch breaks the 30 fps lock | tech | Y | - | 1580 | 1580 | 18.2 | 33.7 | 2 | 156 | 518 | 61.24000000000001 | E1-short |
| 11-24T14:00 | GTA 6's Jason was in the Army. Rockstar explains | characters | Y | - | 1706 | 1706 | 27.9 | 21.9 | - | 267 | 1095 | 67.89 | E1-long |
| 11-24T17:00 | GTA 6's Cheetah supercar is real. It costs £1 mi | money | Y | - | 1868 | 1873 | 18.5 | 21.5 | - | 1160 | 1170 | 51.28 | E1-short |
| 11-24T20:00 | GTA 6 brought back GTA 5's Mount Chiliad mystery | other | Y | - | 1836 | 1840 | 26.1 | 28.8 | - | 1418 | 1841 | 70.79 | E1-long |
| 11-25T02:00 | GTA 6 outsold three consoles before it even laun | records | Y | - | 1423 | 1426 | 20.9 | 26.3 | - | 345 | 486 | 41.07 | E1-long |
| 11-25T12:00 | GTA 6's Lucia isn't from Vice City. Here's where | characters | Y | - | 1599 | 1601 | 22.2 | 24.2 | - | 1219 | 1234 | - | E4-lucia |
| 11-25T14:00 | GTA 6's money glitch survived the new update | other | Y | - | 1537 | 1542 | 26.1 | 29.8 | 2 | 364 | 991 | - |  |
| 11-25T17:00 | GTA 6's Jason lives rent-free. Here's the catch | characters | Y | - | 1805 | 1805 | 39.4 | 21 | 1 | 1162 | 1169 | - |  |
| 11-25T20:00 | GTA 6 sold 44.9 million in four days, analyst sa | records | Y | - | 957 | 959 | 25.5 | 34.4 | 3 | 109 | 135 | - |  |
| 11-26T02:00 | GTA 6 pulled players away from Fortnite, analyst | other | Y | - | 1498 | 1499 | 21.3 | 23.7 | 4 | 567 | 923 | - |  |
| 11-26T12:00 | GTA 6: Lucia's hidden looks are in magazines. He | characters | Y | - | 1644 | 1644 | 17.7 | 27.8 | 5 | 1783 | 1783 | - | E4-lucia |
| 11-26T14:00 | GTA 6 is PlayStation's biggest launch ever, Sony | records | Y | - | 213 | 213 | 16.8 | 25.9 | - | 49 | 49 | - |  |
| 11-26T17:00 | GTA 6 won't let you steal every car. Here's how | other | Y | - | - | 1536 | 26.2 | 24.5 | - | - | 1074 | - |  |
| 11-26T20:00 | GTA 6 hides Mario-style caps for Jason and Lucia | characters | Y | - | - | 1475 | 11.7 | 30.9 | 2 | - | 200 | - |  |
| 11-27T02:00 | GTA 6 takes all your cash when you die. Keep it  | other | Y | - | - | 1489 | 23.2 | 29.8 | - | - | 61 | - |  |

Videos with 24 h numbers: 50 of 53.

**By topic type** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- characters: 1635 / 1190.5 / 23.1 / n=9
- reviews: 1498.0 / 888.5 / 23.6 / n=2
- other: 1466.0 / 717 / 17.4 / n=10
- money: 1407 / 705.0 / 18.5 / n=5
- tech: 1354 / 568.0 / 18.2 / n=7
- drama: 1339 / 295 / 25.9 / n=1
- records: 1292 / 314.5 / 20.0 / n=8
- real world: 1270.0 / 319 / 16.6 / n=8

**Logo on cover/first screen** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- logo: 1463.0 / 670 / 22.2 / n=37
- no logo: 307 / 1.5 / 14.4 / n=13

**By slot (UTC)** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- 12:00: 1589.5 / 1183.0 / 25.2 / n=6
- 02:00: 1470 / 567 / 20.9 / n=9
- 17:00: 1401 / 1147 / 16.2 / n=9
- 14:00: 1347 / 364 / 19.6 / n=9
- 23:00: 1340.5 / 251.5 / 22.2 / n=7
- 20:00: 1338 / 717 / 20.0 / n=9
- 11:00: 307 / 1 / 14.8 / n=1

**By length** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- >55 s: 1420.5 / 621.5 / 24.1 / n=4
- <45 s: 1393.5 / 616 / 19.4 / n=45
- 45-55 s: 557 / None / 18.8 / n=1

**Format** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- story format: 1580 / 459 / 21.3 / n=17
- old format: 1333.0 / 764.0 / 19.0 / n=33

**Top 3 (IG 24h):** GTA 6's Lucia actress was in GTA 5 all a (2259; hook: "") | GTA 6's Cheetah supercar is real. It cos (1868; hook: "") | GTA 6 brought back GTA 5's Mount Chiliad (1836; hook: "")

**Bottom 3 (IG 24h):** GTA 6 launch: 7.9 million people watchin (153; hook: "") | The GTA 6 trailer that broke YouTube (133; hook: "Why did GTA 6's trailer come early?") | GTA 6 sold 19 million copies? Here's the (None; hook: "")
<!-- AUTO:END -->
