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

## What the numbers say so far (20 Nov, 13 videos with 24 h numbers + 3 newer)
- F1 Logo + story format: the 3 videos since 19 Nov 20:00 UTC (logo on cover/first screen, story format, Mark voice)
  had 1,334 / 1,634 / 1,452 Instagram views in under 24 h. The 13 before them: median 307 at 24 h (range 133-1,470).
  Their Instagram average watch time is 26-28 s vs a median of 14.6 s before; skip rate 23-33 % vs 31 % median.
  Logo and story format changed together, so this is one finding, not two.
- F2 Instagram views do not turn into followers: ~1,500 views per Reel but only 6 followers in total. YouTube
  subscribers went 15 -> 47. Followers are now the bottleneck on Instagram (E2 tests this).
- F3 Before the logo, the 3 best topics on Instagram were a character (Lucia, 1,470), a "will it work for me" tech
  question (PS5 space 1,354; no PC 1,401) and a record (GTA 5's record, 1,386). The 3 worst were viral-clip /
  event / trailer-timing stories (133-174). Topic types to favour: characters, "does this affect me" tech/money,
  records. Topic types to avoid: events and trailer trivia.
- F4 YouTube is uneven: within 24 h the real-places video got 712 views and the Tokyo one 58, with the same
  format and logo. Not enough data to say why yet; keep collecting (the YouTube Data API counts are now saved every
  6 h, table `yt_live`).

- F5 Posting time (21 Nov, from the owner's screenshots, 09:37 IST; 23 videos):
  - Instagram: no time pattern. Before the logo, every slot had hits (1,350-1,580) and flops (135-350); since the
    logo every slot gets ~1,270-1,650 except the PC video at 17:00 UTC (727). Topic and cover decide, not the hour.
  - YouTube: the 23:00 UTC slot (04:30 IST) is weak every time: PS5 152, no disc 202, Tokyo 76, characters 121
    (5 h old) - while the SAME videos did well on Instagram (1,357 / 566 / 1,647 / 1,267). YouTube views as a share
    of Instagram views: 23:00 UTC 5-36 %; all other slots 28-160 % (02:00 68-76 %, 12:00 72 %, 14:00 72-160 %,
    17:00 99-151 %, 20:00 28-127 %). 4 of 4 videos, so it's a pattern worth testing, not proof (E3).

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

## Adopted rules (proven on our GTA numbers)
- R1 (20 Nov): real GTA VI logo on the cover and first screen + story format (F1).
- R2 (20 Nov): favour character, "does this affect me" (price/console/storage) and record topics; avoid event and
  trailer-trivia topics (F3). Re-check when 10 more videos have numbers.
  Confirmed 21 Nov on 23 videos (F6): every daily batch has >= 3 of 5 from characters / records / real-world
  practical / "does it affect me"; at most 1 news/drama; no events, timelines or trailer trivia.
- R3 (21 Nov): cover picture = a clear Lucia or Jason face (or masked Lucia) from `faces` in
  `assets/official/attention_shots.json`; no faceless covers (cars, buildings, scenery, crowds). Never the same
  face shot two days running (F6).
- R4 (21 Nov): the last beat asks a side-taking question that splits viewers ("PS5 or PC - which side are you
  on?"), never a neutral "what do you think?" (F6: 13 YT comments on the PC vs console video vs ~0 elsewhere).
- R5 (21 Nov): at least 1 of 5 daily videos is a practical / real-world fact viewers save or send (price in
  rupees/dollars, size, where places are in real life, what console you need) - these get all the shares (F6).

## Experiments log
<!-- newest first: E<n> | started | change | hypothesis | videos (test / control) | result with numbers | decision -->
- E3 | from 22 Nov | slots 12:00, 14:00, 17:00, 20:00, 02:00 UTC (the 23:00 slot moves to 12:00 = 17:30 IST; config
  gta_slots) | the 12:00 video gets >= 50 % of its Instagram views on YouTube at 24 h, like the other slots, while the
  23:00 videos got 5-36 % | 22-24 Nov 12:00 videos vs 19-21 Nov 23:00 videos, same metric | result: pending |
  decision: pending (if adopted, keep 23:00 out; if not, go back)
- E2 | from 22 Nov scripts | every video's last beat ends with a follow line after the comment question, e.g.
  "Follow for a new GTA 6 secret every day." | Instagram followers per 1,000 Reel views rise from ~0.1 (19-21 Nov)
  to 1+ | all videos 22-24 Nov vs 19-21 Nov (account-level: daily follower and subscriber gain per 1,000 views) |
  result: pending | decision: pending
- E1 | from 22 Nov scripts | length: 2 of the 5 daily videos 100-115 words (~40 s), 3 at 140-165 words (~55 s);
  alternate which slots get the short ones each day | the short ones get >= 20 % more Instagram views at 24 h with
  a lower skip rate | test = short ones, control = long ones, same days | result: pending | decision: pending

## Numbers

<!-- AUTO:START -->
_Numbers updated 2026-11-20 11:46 UTC by scripts/gta_learn.py (GTA videos only; no API cost)._

**Accounts:** youtube 47 (first seen 15); instagram 6 (first seen 1)

| published (UTC) | video | cat | logo | s | IG 24h | IG now | IG watch s | IG skip % | IG shares | YT 24h | YT now | YT % viewed | exp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11-16T17:00 | GTA 6 still isn't on PC. Here's why | tech | - | 29.2 | 1401 | 1401 | 13.0 | 33.5 | - | - | 4 | 90.37 |  |
| 11-16T20:00 | GTA 6 at $80 is cheaper than GTA 5 was | money | - | - | 242 | 243 | 15.3 | 33.2 | - | - | 10 | 128.93 |  |
| 11-16T23:00 | GTA 6's wildest scenes match real Florida videos | real world | - | 31.6 | 174 | 174 | 11.6 | 39.3 | - | - | 30 | 49.29 |  |
| 11-17T02:00 | The GTA 6 trailer that broke YouTube | other | - | 34.7 | 133 | 135 | 11.5 | 42 | - | - | 1157 | 74.26 |  |
| 11-17T17:00 | 27 minutes of GTA 6 gameplay: what nobody notice | other | - | 27.5 | 426 | 430 | 9.0 | 36.9 | 1 | - | 45 | 68.91 |  |
| 11-17T20:00 | GTA 6 took 13 years. Here's what happened | other | - | 42.2 | 191 | 192 | 11.1 | 43.1 | - | - | 243 | 46.12 |  |
| 11-17T23:00 | Will GTA 6 even fit on your PS5? | tech | - | 34.4 | 1354 | 1357 | 16.4 | 26.6 | - | - | 152 | 48.34 |  |
| 11-18T02:00 | Lucia is the GTA hero we waited 29 years for | characters | - | 31.6 | 1470 | 1545 | 14.6 | 30.1 | - | - | 1200 | 58.56 |  |
| 11-18T11:00 | Is the $100 GTA 6 Ultimate Edition worth it? | money | - | 38.4 | 307 | 346 | 14.9 | 44.4 | - | 1 | 161 | 33.18 |  |
| 11-18T14:00 | Why an NBA team becomes 'Vice City' tonight | real world | - | - | 171 | 198 | 13.3 | 31.2 | - | 2 | 244 | 105.76 |  |
| 11-18T17:00 | GTA 6 is already unlocked in these countries | tech | - | 57.1 | 183 | 184 | 16.2 | 31.1 | - | 1 | 133 | 32.02 |  |
| 11-18T23:00 | Why the GTA 6 box has no disc inside | tech | - | 47.2 | 557 | 566 | 18.7 | 32.1 | - | - | 187 | - |  |
| 11-19T14:00 | The GTA 5 record GTA 6 has to beat | records | - | - | 1386 | 1386 | 22.6 | 30.1 | - | - | 878 | - |  |
| 11-19T20:00 | GTA 6: Rockstar's war on the leakers | drama | Y | - | - | 1334 | 26.0 | 33 | - | - | 225 | - |  |
| 11-19T23:00 | GTA 6 is in America, but Tokyo nearly won, says  | real world | Y | - | - | 1634 | 28.1 | 27.6 | 4 | - | 58 | - |  |
| 11-20T02:00 | GTA 6's map: the real places it looks like | real world | Y | - | - | 1452 | 27.3 | 22.8 | 4 | - | 712 | - |  |
| 11-20T12:00 | GTA 6 costs double GTA 5 in India, but there's a | money | Y | - | - | - | - | - | - | - | - | - |  |
| 11-20T14:00 | GTA 6's wildest scenes match real Florida videos | real world | Y | - | - | - | - | - | - | - | - | - |  |
| 11-20T17:00 | GTA 6 still isn't on PC. Here's why | tech | Y | - | - | - | - | - | - | - | - | - |  |
| 11-20T20:00 | GTA 6 tied the highest Metacritic score ever | records | Y | 56.6 | - | - | - | - | - | - | - | - |  |
| 11-20T23:00 | GTA 6's characters in Rockstar's own words | characters | Y | - | - | - | - | - | - | - | - | - |  |
| 11-21T02:00 | GTA 6 Trailer 2: 475 million views in a day? | records | Y | - | - | - | - | - | - | - | - | - |  |

Videos with 24 h numbers: 13 of 22.

**By topic type** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- characters: 1470 / None / 14.6 / n=1
- records: 1386 / None / 22.6 / n=1
- tech: 955.5 / 1 / 16.3 / n=4
- money: 274.5 / 1 / 15.1 / n=2
- other: 191 / None / 11.1 / n=3
- real world: 172.5 / 2 / 12.4 / n=2

**Logo on cover/first screen** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- no logo: 307 / 1 / 14.6 / n=13

**By slot (UTC)** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- 02:00: 801.5 / None / 13.1 / n=2
- 14:00: 778.5 / 2 / 18.0 / n=2
- 23:00: 557 / None / 16.4 / n=3
- 17:00: 426 / 1 / 13.0 / n=3
- 11:00: 307 / 1 / 14.9 / n=1
- 20:00: 216.5 / None / 13.2 / n=2

**By length** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- 45-55 s: 557 / None / 18.7 / n=1
- <45 s: 307 / 1.5 / 13.3 / n=11
- >55 s: 183 / 1 / 16.2 / n=1

**Format** (median per video: IG views 24h / YT views 24h / IG avg watch s / n)
- old format: 307 / 1 / 14.6 / n=13

**Top 3 (IG 24h):** Lucia is the GTA hero we waited 29 years (1470; hook: "Was GTA 6's Lucia GTA's first woman?") | GTA 6 still isn't on PC. Here's why (1401; hook: "Why no GTA 6 PC version at launch?") | The GTA 5 record GTA 6 has to beat (1386; hook: "")

**Bottom 3 (IG 24h):** GTA 6's wildest scenes match real Florid (174; hook: "A gator walked into a store?") | Why an NBA team becomes 'Vice City' toni (171; hook: "") | The GTA 6 trailer that broke YouTube (133; hook: "Why did GTA 6's trailer come early?")
<!-- AUTO:END -->
