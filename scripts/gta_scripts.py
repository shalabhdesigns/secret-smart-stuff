"""Scripts written and fact-checked by Claude in session (owner, 18 Nov 2026: "$20 every 3-4 days is way too much ...
create a video on the first try"). The pipeline uses notes.script as is: no paid script/review/repair stages.

Each beat: (narration, shot, callout, delivery). Shots are CLIP:<id> from assets/official/shots.json or OFFICIAL:<id>
(GTA V images only for GTA V lines). Facts and sources come from the verified briefs in scripts/gta_queue.py.

Run: PYTHONPATH=. python3 scripts/gta_scripts.py   -> checks every script and writes config/gta_scripts.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

S = {}

S["gta6-biggest-launches"] = dict(
    title="The GTA 5 record GTA 6 has to beat",
    thumb_text="GTA 6 VS GTA 5",
    hook_card="$1B IN 3 DAYS?",
    beats=[
        ("GTA 6 is finally out, and it's chasing one of the biggest records in entertainment.",
         "CLIP:launch_trailer_00685", None, "excited"),
        ("Back in 2013, GTA 5 made over eight hundred million dollars in its first twenty-four hours.",
         "OFFICIAL:v_24ba6644de", "$815.7M IN 24 HOURS", None),
        ("It also sold more than eleven million copies on that first day.",
         "OFFICIAL:v_fdac18d437", "11.21M COPIES", None),
        ("Three days later, it passed one billion dollars.", "OFFICIAL:v_07edb091bb", "$1B IN 3 DAYS", "surprised"),
        ("Guinness World Records called it the fastest entertainment product ever to make a billion dollars.",
         "CLIP:trailer_1_00398", None, None),
        ("That means it beat every movie, album and game that came before it.", "CLIP:trailer_1_00341", None, None),
        ("So can GTA 6 beat that?", "CLIP:trailer_2_00346", None, "curious"),
        ("Take-Two hasn't shared a single sales number yet.", "CLIP:extended_look_12920", None, None),
        ("But earlier this month, the company said pre-orders were \"tracking far above our initial expectations.\"",
         "CLIP:extended_look_07446", "QUOTE: TAKE-TWO", None),
        ("Here's the funny part: GTA 6's biggest rival isn't another game.", "CLIP:extended_look_09166", None, None),
        ("It's GTA 5, the game it replaces.", "OFFICIAL:v_c670974867", None, "laughs softly"),
        ("Does GTA 6 hit a billion dollars in three days? Yes or no?", "CLIP:trailer_1_00300", None, None),
    ],
    facts=[
        {"claim": "GTA V made $815.7 million in its first 24 hours, sold 11.21 million copies in 24 hours and reached "
                  "$1 billion in three days, the fastest entertainment property to do so (Guinness World Records).",
         "sources": ["https://www.guinnessworldrecords.com/news/2013/10/confirmed-grand-theft--auto-breaks-six-sales-world-records-51900"],
         "main": True},
        {"claim": "Take-Two, November 2026: GTA 6 pre-orders are 'tracking far above our initial expectations'; no "
                  "pre-order numbers published.",
         "sources": ["https://shacknews.com/article/151308/grand-theft-auto-6-pre-orders-q2-fy27"], "main": True},
    ],
    description="GTA 5 made $815.7 million in a day and $1 billion in three. Can GTA 6 beat its own big brother?\n"
                "Sources: Guinness World Records (2013), Shacknews (Take-Two earnings, Nov 2026).",
    hashtags=["#GTA6", "#GTA5", "#GrandTheftAuto"],
)

S["gta6-india-price"] = dict(
    title="GTA 6 costs double GTA 5 in India, but there's a twist",
    thumb_text="DOUBLE THE PRICE?",
    hook_card="2X THE PRICE?",
    cover_lines=["DOUBLE PRICE", "IN INDIA?"],
    beats=[
        ("In India, GTA 6 costs double what GTA 5 did, but there's a twist.", "CLIP:extended_look_10132", None, "surprised"),
        ("When GTA 5 launched here in 2013, it cost 2,999 rupees.", "OFFICIAL:v_c670974867", "₹2,999 IN 2013", None),
        ("GTA 6's standard edition is 5,999 rupees.", "CLIP:trailer_2_00232", "₹5,999", None),
        ("And the Ultimate Edition goes up to 7,499 rupees.", "CLIP:extended_look_15485", "₹7,499 ULTIMATE", None),
        ("That sounds brutal, until you look at America.", "CLIP:trailer_2_00346", None, None),
        ("Over there, GTA 5 cost sixty dollars, and GTA 6 costs eighty.", "CLIP:trailer_2_00416",
         "$59.99 → $79.99", None),
        ("That's only about a third more, not double.", "CLIP:extended_look_09166", "+33%", None),
        ("So the bigger jump really is in India.", "CLIP:extended_look_10833", None, None),
        ("But here's the twist: with the rupee at about 94 to the dollar, eighty dollars is now around 7,500 rupees.",
         "CLIP:extended_look_12327", "$80 ≈ ₹7,500", "curious"),
        ("So even after doubling, Indian players still pay about 1,500 rupees less than Americans.",
         "CLIP:extended_look_15698", None, None),
        ("Would you pay 5,999 rupees on day one, or wait for a sale?", "CLIP:trailer_2_00795", None, None),
    ],
    facts=[
        {"claim": "GTA V launched in India at Rs 2,999 in 2013 (distributor E-xpress Interactive).",
         "sources": ["https://www.mcvuk.com/update-grand-theft-auto-5-price-to-remain-rs-2999/"], "main": True},
        {"claim": "GTA 6 in India: Rs 5,999 standard, Rs 7,499 Ultimate; US price $79.99.",
         "sources": ["https://www.mysmartprice.com/gear/gaming/gaming-news/gta-6-pre-orders-go-live-in-india-standard-edition-costs-rs-5999-ultimate-edition-priced-at-rs-7499/"],
         "main": True},
        {"claim": "GTA V launched at $59.99 in the US; GTA 6 is $79.99.",
         "sources": ["https://hothardware.com/news/gta-6-launch-80-single-player-title-rockstar-reveals"], "main": False},
        {"claim": "Mid-November 2026 the rupee trades at about 94 to the US dollar (93.63 on 17 Nov 2026), so $79.99 is "
                  "about Rs 7,500, roughly Rs 1,500 more than India's Rs 5,999 standard edition.",
         "sources": ["https://hdfcsky.com/news/rupee-rises-31-paise-to-93-63-against-us-dollar-in-early-trade-november-17-2026"],
         "main": True},
    ],
    description="GTA 5 was Rs 2,999 in 2013. GTA 6 is Rs 5,999. In dollars, India still pays less than America.\n"
                "Sources: MCV (2013), MySmartPrice (2026), HDFC Sky (exchange rate, Nov 2026).",
    hashtags=["#GTA6", "#GTA6India", "#GrandTheftAuto"],
)

S["gta6-leak-war"] = dict(
    title="GTA 6: Rockstar's war on the leakers",
    thumb_text="LEAKED IN 2022",
    hook_card="LEAKED IN 2022",
    cover_lines=["LEAKED", "4 YEARS EARLY"],
    beats=[
        ("Four years before GTA 6 came out, a hacker leaked footage of it to the whole internet.",
         "CLIP:extended_look_08816", None, "serious"),
        ("In September 2022, he posted early development clips of the game online.",
         "CLIP:extended_look_03894", "SEPT 2022", None),
        ("He was a teenager, and he was caught.", "CLIP:trailer_2_00452", None, None),
        ("In December 2023, a UK court sent him to a hospital, with no end date.",
         "CLIP:trailer_2_00498", "UK COURT, DEC 2023", None),
        ("But the leaks didn't stop there.", "CLIP:trailer_2_01188", None, "short pause"),
        ("That same month, GTA 6's very first trailer leaked online.",
         "CLIP:trailer_1_00300", "TRAILER 1 LEAKED", None),
        ("So Rockstar released the trailer early, before its planned premiere.", "CLIP:trailer_2_00346", None, None),
        ("Then this August, new clips started showing up online.", "CLIP:extended_look_02226", "AUG 2026", None),
        ("This time, Take-Two went to court.", "CLIP:extended_look_12920", "TAKE-TWO GOES TO COURT", "serious"),
        ("It got court orders against two big platforms.", "CLIP:extended_look_12327", "COURT ORDERS", None),
        ("Now Microsoft, which owns GitHub, and Discord have to help find who posted the clips.",
         "CLIP:extended_look_07899", "MICROSOFT + DISCORD", None),
        ("From leaked footage to court orders, Rockstar has been fighting leakers for four years.",
         "CLIP:launch_trailer_00685", None, None),
        ("Did you watch the leaks, or did you wait for the real thing?", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Sept 2022: a teenage hacker leaked early GTA 6 development footage; in Dec 2023 a UK court gave him "
                  "an indefinite hospital order. GTA 6 came out on 19 Nov 2026, about four years later.",
         "sources": ["https://www.techradar.com/gaming/gta-6-hacker-who-intended-to-return-to-cyber-crime-as-soon-as-possible-sentenced-to-an-indefinite-hospital-order"],
         "main": True},
        {"claim": "Dec 2023: GTA 6 trailer 1 leaked online, so Rockstar released it early, before its planned premiere.",
         "sources": ["https://www.videogameschronicle.com/news/the-gta-6-trailer-has-allegedly-leaked-online/"],
         "main": True},
        {"claim": "Aug 2026: after new GTA 6 clips leaked, Take-Two won court orders requiring Microsoft (owner of "
                  "GitHub) and Discord to help identify the accounts (AFP).",
         "sources": ["https://www.khaleejtimes.com/entertainment/gaming/gta-6-publisher-subpoenas-bid-to-unmask-leaks"],
         "main": True},
    ],
    description="From the 2022 hack to 2026 court orders: how Rockstar and Take-Two fought GTA 6 leaks.\n"
                "Sources: TechRadar, VGC, AFP via Khaleej Times.",
    hashtags=["#GTA6", "#Rockstar", "#GrandTheftAuto"],
)

S["gta6-almost-tokyo"] = dict(
    title="GTA 6 is in America, but GTA almost went to Tokyo",
    thumb_text="ALMOST TOKYO?",
    hook_card="ALMOST TOKYO?",
    cover_lines=["ALMOST IN", "TOKYO?"],
    beats=[
        ("GTA almost went to Tokyo, so why does it always end up in America?", "CLIP:extended_look_12327", None,
         "curious"),
        ("Obbe Vermeij used to be a technical director at Rockstar North.", "CLIP:extended_look_15698",
         "OBBE VERMEIJ, EX-ROCKSTAR", None),
        ("He says a GTA set in Tokyo \"almost actually happened.\"", "CLIP:extended_look_12606",
         "QUOTE: OBBE VERMEIJ", None),
        ("And Tokyo wasn't the only city on the table.", "CLIP:trailer_1_00300", "TOKYO + 3 MORE", None),
        ("He says Rio, Moscow and Istanbul were considered too.", "CLIP:extended_look_11275",
         "RIO, MOSCOW, ISTANBUL", None),
        ("So why does every numbered GTA still end up in America?", "CLIP:trailer_2_00346", None, None),
        ("Rockstar co-founder Dan Houser has a simple answer.", "CLIP:extended_look_07446", None, None),
        ("He says other countries may have great cities, \"but they're not American cities.\"",
         "CLIP:extended_look_07899", "QUOTE: DAN HOUSER", None),
        ("For him, GTA needs America's guns and its larger-than-life characters.", "CLIP:extended_look_03021", None,
         None),
        ("There's a practical problem too.", "CLIP:trailer_2_00232", None, None),
        ("Vermeij says a whole new country is \"just not realistic\" when there's only a GTA every twelve years.",
         "CLIP:extended_look_08816", "QUOTE: OBBE VERMEIJ", None),
        ("So after thirteen years, GTA 6 went back to a city fans already know and love: Vice City.",
         "CLIP:extended_look_05708", "VICE CITY", None),
        ("If GTA ever does leave America, which city should it be?", "CLIP:extended_look_15485", None, None),
    ],
    facts=[
        {"claim": "Former Rockstar North technical director Obbe Vermeij said GTA: Tokyo 'almost actually happened', "
                  "and Rio, Moscow and Istanbul were also considered; a new country is 'just not realistic' 'when "
                  "there's a GTA every 12 years'.",
         "sources": ["https://hitmarker.net/news/rockstar-reportedly-considered-grand-theft-auto-games-set-in-tokyo-rio-moscow-and-istanbul-former-developer-claims-1606106"],
         "main": True},
        {"claim": "Dan Houser: other countries 'may have great cities, but they're not American cities'; GTA needs "
                  "guns and larger-than-life characters (Lex Fridman interview).",
         "sources": ["https://www.pcgamer.com/games/action/rockstar-co-founder-dan-houser-says-theres-a-reason-the-grand-theft-auto-games-are-always-set-in-us-cities-guns"],
         "main": True},
    ],
    description="GTA Tokyo almost happened. Why GTA always comes back to America, in Rockstar's own words.\n"
                "Sources: GamesHub via Hitmarker (Obbe Vermeij), PC Gamer (Dan Houser).",
    hashtags=["#GTA6", "#GTA", "#Rockstar"],
)

S["gta6-real-florida"] = dict(
    title="GTA 6's map: the real places you can visit",
    thumb_text="REAL PLACES?",
    hook_card="REAL PLACES?",
    cover_lines=["REAL PLACES", "YOU CAN VISIT"],
    beats=[
        ("GTA 6's map is based on real places, and you can actually go to them.", "CLIP:extended_look_11275",
         None, "excited"),
        ("The game is set in Leonida, Rockstar's version of Florida.", "CLIP:trailer_1_00217", "LEONIDA = FLORIDA",
         None),
        ("And its big city, Vice City, is basically Miami.", "CLIP:extended_look_07446", "VICE CITY = MIAMI", None),
        ("Rockstar says the Leonida Keys have \"some of the most beautiful and dangerous waters in all of "
         "America.\"", "CLIP:launch_trailer_00026", "QUOTE: ROCKSTAR", None),
        ("Outlets compare them to the real Florida Keys, the chain of islands south of Miami.",
         "CLIP:extended_look_10422", "FLORIDA KEYS", None),
        ("Then comes Grassrivers, and Rockstar promises \"deadlier predators and weirder discoveries.\"",
         "CLIP:trailer_1_00183", "QUOTE: ROCKSTAR", None),
        ("Grassrivers looks a lot like the Everglades, the huge wetland where real airboats skim across the grass.",
         "CLIP:extended_look_10298", "EVERGLADES", None),
        ("And Mount Kalaga, Rockstar says, offers \"prime hunting, fishing, and off-road trails.\"",
         "CLIP:extended_look_04645", "QUOTE: ROCKSTAR", None),
        ("Florida doesn't really have mountains, so that one is more Rockstar than reality.",
         "CLIP:extended_look_11148", None, "laughs softly"),
        ("Rockstar hasn't named the real places itself, but the resemblance is hard to miss.",
         "CLIP:trailer_2_00081", None, None),
        ("Which one would you visit first: the Keys, the Everglades, or Miami?", "CLIP:extended_look_10489",
         "KEYS, EVERGLADES OR MIAMI?", None),
    ],
    facts=[
        {"claim": "Rockstar's descriptions: the Leonida Keys have 'some of the most beautiful and dangerous waters in "
                  "all of America'; Grassrivers has 'deadlier predators and weirder discoveries'; Mount Kalaga "
                  "'offers prime hunting, fishing, and off-road trails'. Outlets compare the Leonida Keys to the "
                  "Florida Keys and Grassrivers to the Everglades; Rockstar hasn't named real places.",
         "sources": ["https://www.pcgamer.com/games/grand-theft-auto/gta6-map"], "main": True},
        {"claim": "Florida has no mountains: its highest point, Britton Hill, is 345 feet (105 m).",
         "sources": ["https://en.wikipedia.org/wiki/Britton_Hill"], "main": False},
    ],
    description="Leonida is Rockstar's Florida. Here are the real places its regions are compared to.\n"
                "Sources: Rockstar Games via PC Gamer.",
    hashtags=["#GTA6", "#Florida", "#GrandTheftAuto"],
)


# 19 Nov 2026: remakes in the new style of two 16 Nov videos that had under 100 views at 48 h (owner chose remake)
S["gta6-florida-man"] = dict(
    title="GTA 6's wildest scenes really happened in Florida",
    thumb_text="IT REALLY HAPPENED",
    hook_card="THIS WAS REAL?",
    cover_lines=["THIS WAS", "REAL?"],
    beats=[
        ("Some of the wildest scenes in GTA 6's first trailer actually happened in real life.",
         "CLIP:trailer_1_00475", None, "surprised"),
        ("When the trailer dropped in December 2023, fans started matching its moments to real viral videos from "
         "Florida.", "CLIP:trailer_1_00325", "DEC 2023", None),
        ("Remember the woman dancing on top of a moving car?", "CLIP:trailer_1_00248", None, "curious"),
        ("Know Your Meme traced it to a real clip from Miami's MacArthur Causeway, during spring break 2017.",
         "CLIP:trailer_2_00346", "MIAMI, 2017", None),
        ("Then there's the man hauling a huge alligator out of a backyard pool.", "CLIP:trailer_1_00424", None, None),
        ("A real trapper did exactly that, and a Florida news station filmed it in 2019.",
         "CLIP:extended_look_15485", "FLORIDA NEWS, 2019", None),
        ("And the alligator wandering into a store? A real one walked into a Florida Walmart back in 2013.",
         "CLIP:extended_look_07238", "WALMART, 2013", "laughs softly"),
        ("Even the dirt bikes popping wheelies through the streets were on South Florida news.",
         "CLIP:trailer_1_00656", None, None),
        ("Rockstar has never said which clips inspired these scenes.", "CLIP:extended_look_12920", None, None),
        ("But next time GTA 6 feels way over the top, remember that real Florida got there first.",
         "CLIP:trailer_1_00183", None, None),
        ("What's the craziest Florida story you've ever heard?", "CLIP:extended_look_10298", None, None),
    ],
    facts=[
        {"claim": "Know Your Meme (6 Dec 2023) matched GTA VI trailer moments to real Florida videos: a woman twerking "
                  "on a car on Miami's MacArthur Causeway during spring break (March 2017); a trapper dragging a large "
                  "alligator out of a pool (WPBF 25 News, April 2019); an alligator at a Florida Walmart (Sky News, "
                  "October 2013); ATVs and dirt bikes racing in South Florida (NBC 6, February 2023).",
         "sources": ["https://knowyourmeme.com/editorials/every-reference-to-real-life-videos-in-the-grand-theft-auto-vi-trailer"],
         "main": True},
        {"claim": "Rockstar has not confirmed which real clips inspired the trailer.",
         "sources": ["https://knowyourmeme.com/editorials/every-reference-to-real-life-videos-in-the-grand-theft-auto-vi-trailer"],
         "main": False},
    ],
    description="Fans matched GTA 6's craziest trailer moments to real Florida videos. Rockstar hasn't said which "
                "inspired it.\nSource: Know Your Meme (Dec 2023).",
    hashtags=["#GTA6", "#FloridaMan", "#GrandTheftAuto"],
)

S["gta6-not-on-pc"] = dict(
    title="GTA 6 still isn't on PC. Here's why",
    thumb_text="NO PC VERSION",
    hook_card="WHERE'S PC?",
    beats=[
        ("GTA 6 is finally out, but PC players still can't play it.", "CLIP:trailer_2_00232", None, "serious"),
        ("It launched on November 19th on PlayStation 5 and Xbox Series X and S only.",
         "CLIP:launch_trailer_00685", "PS5 + XBOX ONLY", None),
        ("And Rockstar still hasn't announced a PC date.", "CLIP:extended_look_12920", None, None),
        ("So why make PC players wait?", "CLIP:trailer_2_00346", None, "curious"),
        ("Take-Two's boss, Strauss Zelnick, says Rockstar always starts on console.", "CLIP:extended_look_07446",
         "QUOTE: ZELNICK, TAKE-TWO", None),
        ("In his words, the core audience has to \"be served first and best.\"", "CLIP:trailer_1_00325",
         "QUOTE: ZELNICK, TAKE-TWO", None),
        ("And if history is any guide, PC players know this wait well.", "CLIP:extended_look_09166", None, None),
        ("GTA 5 came out on consoles in September 2013, and only reached PC in April 2015.",
         "OFFICIAL:v_24ba6644de", "19 MONTHS LATER", None),
        ("Red Dead Redemption 2 waited just over a year for its PC version.", "CLIP:extended_look_04645",
         "1 YEAR+", None),
        ("So if history repeats, PC players could be waiting a year or more.", "CLIP:trailer_2_01188", None, None),
        ("Rockstar hasn't said that, but the pattern is hard to ignore.", "CLIP:extended_look_15698", None, None),
        ("PC players, would you wait, or buy a console just for GTA 6?", "CLIP:trailer_2_00795", None, None),
    ],
    facts=[
        {"claim": "GTA 6 launched on 19 Nov 2026 on PS5 and Xbox Series X|S only; no PC date announced.",
         "sources": ["https://frvr.com/blog/news/gta-6-boss-defends-late-pc-release-console-must-be-served-first-and-best/"],
         "main": True},
        {"claim": "Strauss Zelnick: Rockstar always starts on console; the core must 'be served first and best' "
                  "(Bloomberg, via FRVR, May 2026).",
         "sources": ["https://frvr.com/blog/news/gta-6-boss-defends-late-pc-release-console-must-be-served-first-and-best/",
                     "https://pcgamer.com/gaming-industry/pc-players-arent-grand-theft-auto-6s-core-audience-take-two-ceo-says-and-thats-why-we-have-to-wait-for-it"],
         "main": True},
        {"claim": "GTA V: consoles Sept 2013, PC April 2015. Red Dead Redemption 2: consoles Oct 2018, PC Nov 2019.",
         "sources": ["https://frvr.com/blog/news/gta-6-boss-defends-late-pc-release-console-must-be-served-first-and-best/"],
         "main": False},
    ],
    description="GTA 6 is out on PS5 and Xbox, but not PC. Take-Two's boss explains why, and history hints at the wait.\n"
                "Sources: FRVR (Bloomberg interview), PC Gamer.",
    hashtags=["#GTA6", "#PCGaming", "#GrandTheftAuto"],
)


# 20 Nov 2026: three new post-launch topics (records, characters, records/hype), researched and verified 19 Nov
S["gta6-review-scores"] = dict(
    title="GTA 6 tied the highest Metacritic score ever",
    thumb_text="99 / 100?",
    hook_card="ALMOST PERFECT?",
    cover_lines=["99 OUT OF 100", "ON METACRITIC?"],
    beats=[
        ("GTA 6's reviews are in, and the number is almost perfect.", "CLIP:extended_look_10196", None, "excited"),
        ("When the reviews landed, it scored 99 out of 100 on Metacritic.", "CLIP:trailer_1_00300", "99 / 100 METACRITIC", None),
        ("That ties The Legend of Zelda: Ocarina of Time for the highest score Metacritic has ever recorded.",
         "CLIP:trailer_1_00398", "TIED: OCARINA OF TIME", "surprised"),
        ("And out of well over a hundred reviews, not a single one was mixed or negative.", "CLIP:trailer_1_00325",
         "0 MIXED, 0 NEGATIVE", None),
        ("IGN, GameSpot, Eurogamer and The Guardian all gave it a perfect score.", "CLIP:extended_look_07446",
         "100/100 FROM IGN + GAMESPOT", None),
        ("IGN even called it \"the single most impressive video game I have ever played.\"", "CLIP:trailer_1_00356",
         "QUOTE: IGN REVIEW", None),
        ("So is it perfect? Not quite.", "CLIP:trailer_2_01188", None, "curious"),
        ("Many reviewers knocked it for running at thirty frames per second, with no performance mode.",
         "CLIP:extended_look_09432", "30 FPS, NO PERFORMANCE MODE", None),
        ("Some also say the story's pacing sags in places.", "CLIP:extended_look_07501", None, None),
        ("But almost every review praises the same thing: Leonida itself.", "CLIP:trailer_1_00217", None, None),
        ("One roundup calls Vice City the most reactive city Rockstar has ever built.", "CLIP:extended_look_10262",
         None, None),
        ("Thirteen years after GTA 5, the critics say the wait was worth it.", "CLIP:launch_trailer_00670", None,
         None),
        ("So is 99 too high, or does GTA 6 really deserve it?", "CLIP:trailer_2_00961", None, None),
    ],
    facts=[
        {"claim": "GTA 6: Metacritic 99 (PS5, 147 critic reviews; Xbox Series X|S 99 from 14) and OpenCritic Top Critic "
                  "Average 99 with 100% recommending; IGN, GameSpot, Eurogamer and The Guardian scored it 100; IGN: "
                  "'the single most impressive video game I have ever played'.",
         "sources": ["https://endgametools.com/en/gta-6/news/gta-6-reviews"], "main": True},
        {"claim": "The 99 is tied with Ocarina of Time for the highest score Metacritic has recorded; zero mixed or "
                  "negative reviews; criticisms: 30fps cap with no performance mode, pacing sags in places; praise for "
                  "Leonida's density, 'the most reactive city Rockstar has built'.",
         "sources": ["https://outputlag.com/featured-slider/gta-6-review-roundup/"], "main": True},
    ],
    description="GTA 6 scores 99 on Metacritic, tied with Ocarina of Time for the site's best ever. What critics loved "
                "and what they didn't.\nSources: Endgame Tools, Output Lag (review roundups, 18 Nov 2026).",
    hashtags=["#GTA6", "#GTA6Review", "#GrandTheftAuto"],
)

S["gta6-cast-one-liners"] = dict(
    title="GTA 6's characters in Rockstar's own words",
    thumb_text="WHO ARE THEY?",
    hook_card="ONE LINE EACH",
    beats=[
        ("Rockstar sums up each GTA 6 character in one sentence, and one is way too relatable.",
         "CLIP:extended_look_03021", None, "curious"),
        ("First, Jason Duval, one of the two leads.", "CLIP:trailer_2_00232", None, None),
        ("Rockstar's line: \"Jason wants an easy life, but things just keep getting harder.\"",
         "CLIP:trailer_2_00081", "QUOTE: ROCKSTAR GAMES", None),
        ("Then Lucia Caminos, who starts the story in prison.", "CLIP:trailer_1_00065", None, None),
        ("Her line: \"Lucia's father taught her to fight as soon as she could walk.\"", "CLIP:trailer_2_00498",
         "QUOTE: ROCKSTAR GAMES", None),
        ("Brian Heder is Jason's landlord, and he runs a boat yard in the Keys.", "CLIP:launch_trailer_00026",
         None, None),
        ("Rockstar says: \"Brian's a classic drug runner from the golden age of smuggling in the Keys.\"",
         "CLIP:trailer_2_00851", "QUOTE: ROCKSTAR GAMES", None),
        ("In Vice City, Boobie Ike owns property, a club and a recording studio.", "CLIP:trailer_1_00341", None,
         None),
        ("The warning: \"Boobie's all smiles until it's time to talk business.\"", "CLIP:trailer_1_00325",
         "QUOTE: ROCKSTAR GAMES", None),
        ("Raul Bautista is a bank robber who is always hunting for talent.", "CLIP:extended_look_12920",
         None, None),
        ("But the best line goes to Jason's friend, Cal Hampton.", "CLIP:trailer_2_00895", None, None),
        ("Rockstar says: \"Cal is at the low tide of America and happy there.\"", "CLIP:trailer_2_00831",
         "QUOTE: ROCKSTAR GAMES", "laughs softly"),
        ("Which GTA 6 character are you most excited to meet?", "CLIP:trailer_2_00795", None, None),
    ],
    facts=[
        {"claim": "Rockstar's character descriptions: 'Jason wants an easy life, but things just keep getting harder.' "
                  "'Lucia's father taught her to fight as soon as she could walk.' 'Brian's a classic drug runner from "
                  "the golden age of smuggling in the Keys.' (Jason's landlord, boat yard) 'Boobie's all smiles until "
                  "it's time to talk business.' (real estate, a club, a recording studio) Raul: 'a seasoned bank "
                  "robber always on the hunt for talent'. 'Cal is at the low tide of America and happy there.'",
         "sources": ["https://www.gtaboom.com/every-gta-6-character-confirmed-so-far-156f"], "main": True},
        {"claim": "Cal's official bio: 'at the low tide of America'; Lucia's bio suggests lifelong fighting.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/gta-6-characters"], "main": False},
    ],
    description="Rockstar describes each GTA 6 character in one line. Jason, Lucia, Brian, Boobie, Raul and Cal, in "
                "Rockstar's own words.\nSources: Rockstar Games character descriptions via GTA BOOM and GamesRadar+.",
    hashtags=["#GTA6", "#JasonAndLucia", "#GrandTheftAuto"],
)

S["gta6-trailer2-record"] = dict(
    title="GTA 6 Trailer 2: 475 million views in a day?",
    thumb_text="475M IN 1 DAY?",
    hook_card="475 MILLION?",
    cover_lines=["475 MILLION", "IN ONE DAY?"],
    beats=[
        ("In May 2025, GTA 6 fans got some really bad news.", "CLIP:trailer_2_01437", None, "serious"),
        ("The game was delayed, from 2025 into 2026.", "CLIP:extended_look_15698", "DELAYED TO 2026", None),
        ("Then, just days later, on a random Tuesday, Rockstar dropped trailer two with no warning at all.",
         "CLIP:trailer_2_00232", None, "surprised"),
        ("And people watched it like nothing before.", "CLIP:trailer_2_01400", None, None),
        ("Rockstar says it got 475 million views in its first twenty-four hours, across every platform.",
         "CLIP:trailer_2_00920", "475M VIEWS IN 24 HOURS", None),
        ("For comparison, the first trailer got about 93 million views on YouTube on its first day.",
         "CLIP:trailer_1_00300", "TRAILER 1: 93M", None),
        ("And that was already a record.", "CLIP:trailer_1_00398", None, None),
        ("So who held the big record before trailer two?", "CLIP:trailer_2_00346", None, "curious"),
        ("A movie. The Deadpool and Wolverine trailer had 365 million views, with help from a Super Bowl airing.",
         "CLIP:extended_look_15524", "DEADPOOL & WOLVERINE: 365M", None),
        ("GTA 6 beat it by more than a hundred million.", "CLIP:trailer_1_00341", "+110M", None),
        ("Rockstar says that makes it the biggest video launch ever, though that's its own count.",
         "CLIP:extended_look_12920", None, None),
        ("A delay, a surprise trailer, and nearly half a billion views in one day.", "CLIP:launch_trailer_00685",
         None, None),
        ("Where were you when trailer two dropped?", "CLIP:trailer_2_00795", None, None),
    ],
    facts=[
        {"claim": "Days after the delay to 2026, trailer 2 dropped completely unannounced on a Tuesday (May 2025); "
                  "Rockstar claims 475 million views across platforms in 24 hours, the biggest video launch ever, "
                  "over five times trailer 1's 93 million in its first day.",
         "sources": ["https://opencritic.com/news/16087/rockstar-claims-gta-6s-second-trailer-was-the-biggest-video-launch-of-all-time-with-nearly-half-a-billion-views-in-one-day"],
         "main": True},
        {"claim": "Rockstar told The Hollywood Reporter: 475M views across all platforms in 24 h; previous record the "
                  "Deadpool & Wolverine trailer with 365M (helped by a Super Bowl airing); trailer 1 got about 93M on "
                  "YouTube in its first day.",
         "sources": ["https://www.techradar.com/gaming/the-latest-grand-theft-auto-6-trailer-has-set-a-major-record-by-racking-up-475-million-views-in-just-24-hours",
                     "https://www.tweaktown.com/news/105135/grand-theft-auto-6-trailer-2-hits-475-million-views-blowing-away-deadpool-wolverines-record/index.html"],
         "main": True},
    ],
    description="A delay, then a surprise trailer: Rockstar says GTA 6's trailer 2 hit 475 million views in 24 hours, "
                "beating Deadpool & Wolverine.\nSources: TechRadar, TweakTown, TheGamer (Rockstar via The Hollywood "
                "Reporter).",
    hashtags=["#GTA6", "#GTA6Trailer", "#GrandTheftAuto"],
)


def build(topic: str, v: dict) -> dict:
    images, scenes = {}, []
    for i, (text, shot, callout, delivery) in enumerate(v["beats"], 1):
        key = next((k for k, s in images.items() if s == shot), None) or f"img{len(images) + 1}"
        images[key] = shot
        scenes.append({"id": f"b{i}", "narration": text, "image": key, "delivery": delivery, "focus": None,
                       "motion": "push" if i % 3 else "drift", "transition": "cut", "callout": callout, "pop": None,
                       "arrow": None, "card_text": None, "tone": "normal", "markers": None})
        if callout:   # 19 Nov 2026: the caption font has no rupee sign (it rendered as an empty box)
            scenes[-1]["callout"] = callout.replace("₹", "RS ")
    return {"viable": True, "title": v["title"], "thumb_text": v["thumb_text"], "hook_card": v["hook_card"],
            "hooks": [v["beats"][0][0]], "chosen_hook": 0, "images": images, "scenes": scenes,
            "facts": v["facts"], "description": v["description"], "hashtags": v["hashtags"],
            "affiliate_product": None, "written_by": "Claude in session (verified)",
            # cover + opening card words, written here (no paid cover call); the picture is the first beat's shot
            "cover": {"image": "img1", "lines": v.get("cover_lines") or [v["hook_card"]], "why": "written in session"}}


def check(topic: str, s: dict) -> list[str]:
    shots = json.loads((ROOT / "assets/official/shots.json").read_text())
    shots = shots.get("shots", shots)
    cat = json.loads((ROOT / "assets/official/catalogue.json").read_text())
    cat = cat.get("images", cat)
    errs = []
    for k, ref in s["images"].items():
        kind, _, sid = ref.partition(":")
        if kind == "CLIP" and (sid not in shots or shots[sid].get("avoid")):
            errs.append(f"{topic}: bad shot {sid}")
        if kind == "OFFICIAL" and sid not in cat:
            errs.append(f"{topic}: bad image {sid}")
    words = sum(len(sc["narration"].split()) for sc in s["scenes"])
    if not 95 <= words <= 175:
        errs.append(f"{topic}: {words} words")
    for sc in s["scenes"]:
        if len(sc["callout"] or "") > 34:
            errs.append(f"{topic}: long callout {sc['callout']}")
        # 19 Nov 2026: a 5 s beat on a 1.5 s shot ran on into an unrelated in-game social post. Mark beats whose shot
        # is clearly shorter than the line (about 2.8 spoken words a second; clips slow down at most 1.6x).
        kind, _, sid = s["images"].get(sc["image"], "").partition(":")
        if kind == "CLIP" and sid in shots:
            secs = len(sc["narration"].split()) / 2.8
            have = shots[sid]["end"] - shots[sid]["start"]
            if have * 1.25 < secs:
                print(f"  warning {topic} {sc['id']}: line ~{secs:.1f}s, shot {sid} {have:.1f}s (runs on)")
    return errs


if __name__ == "__main__":
    out, errs = {}, []
    for t, v in S.items():
        out[t] = build(t, v)
        errs += check(t, out[t])
        print(t, sum(len(sc["narration"].split()) for sc in out[t]["scenes"]), "words,",
              len(out[t]["scenes"]), "beats,", len(set(out[t]["images"].values())), "shots")
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    (ROOT / "config/gta_scripts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote config/gta_scripts.json")
