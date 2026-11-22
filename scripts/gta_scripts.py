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
        ("The real twist is the exchange rate.", "CLIP:extended_look_12327", None, "curious"),
        ("At about 94 rupees to the dollar, eighty dollars is around 7,500 rupees.", "CLIP:extended_look_10196",
         "$80 ≈ ₹7,500", None),
        ("So for the standard edition, Indian players actually pay about 1,500 rupees less than Americans.",
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
    cover_frame={"image": "img1", "t": 5.0, "x": 0.66},   # Lucia in a bandana
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
    title="GTA 6 is in America, but Tokyo nearly won, says an ex-dev",
    thumb_text="ALMOST TOKYO?",
    hook_card="ALMOST TOKYO?",
    cover_lines=["ALMOST IN", "TOKYO?"],
    cover_frame={"image": "img9", "t": 3.5, "x": 0.85},   # Jason close-up
    beats=[
        ("A former Rockstar developer says GTA almost went to Tokyo, so why does it always end up in America?",
         "CLIP:extended_look_12327", None, "curious"),
        ("Obbe Vermeij used to be a technical director at Rockstar North.", "CLIP:trailer_2_00996", None, None),
        ("He says a GTA set in Tokyo \"almost actually happened.\"", "CLIP:extended_look_08740",
         "QUOTE: OBBE VERMEIJ", None),
        ("And Tokyo wasn't the only city on the table.", "CLIP:trailer_1_00300", "TOKYO + 3 MORE", None),
        ("He says Rio, Moscow and Istanbul were considered too.", "CLIP:extended_look_11275",
         "RIO, MOSCOW, ISTANBUL", None),
        ("So why does every numbered GTA still end up in America?", "CLIP:trailer_2_00346", None, None),
        ("Rockstar co-founder Dan Houser has a simple answer.", "CLIP:extended_look_07446", None, None),
        ("He says other countries may have great cities, \"but they're not American cities.\"",
         "CLIP:trailer_2_00188", None, None),
        ("For him, GTA needs guns and larger-than-life characters, and America has both.", "CLIP:extended_look_03021", None,
         None),
        ("There's a practical problem too.", "CLIP:trailer_2_00232", None, None),
        ("Vermeij says a new country is \"just not realistic\" when a GTA only comes out about every twelve years.",
         "CLIP:launch_trailer_00026", "QUOTE: OBBE VERMEIJ", None),
        ("Thirteen years after GTA 5, GTA 6 went back to a city fans already know and love: Vice City.",
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
    title="GTA 6's map: the real places it looks like",
    thumb_text="REAL PLACES?",
    hook_card="REAL PLACES?",
    cover_lines=["REAL PLACES", "YOU CAN VISIT"],
    beats=[
        ("GTA 6's map looks a lot like real places, and you can actually visit them.", "CLIP:extended_look_11275",
         None, "excited"),
        ("The game is set in Leonida, which is widely seen as Rockstar's Florida.", "CLIP:trailer_1_00217", "LEONIDA",
         None),
        ("And its big city, Vice City, is clearly inspired by Miami.", "CLIP:extended_look_07446", "VICE CITY", None),
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
    title="GTA 6's wildest scenes match real Florida videos",
    thumb_text="IT REALLY HAPPENED",
    hook_card="THIS WAS REAL?",
    cover_lines=["THIS WAS", "REAL?"],
    beats=[
        ("Some of the wildest scenes in GTA 6's first trailer look just like real viral videos.",
         "CLIP:extended_look_10196", None, "surprised"),
        ("When the trailer dropped in December 2023, fans started matching its moments to real viral videos from "
         "Florida.", "CLIP:trailer_1_00325", "DEC 2023", None),
        ("Remember the woman dancing on top of a car?", "CLIP:trailer_1_00248", None, "curious"),
        ("Know Your Meme traced it to a real clip from Miami's MacArthur Causeway, during spring break 2017.",
         "CLIP:trailer_2_00346", "MIAMI, 2017", None),
        ("Then there's the man hauling a huge alligator out of a backyard pool.", "CLIP:trailer_1_00424", None, None),
        ("A real trapper did exactly that, and a Florida news station filmed it in 2019.",
         "CLIP:trailer_1_00424", "FLORIDA NEWS, 2019", None),
        ("And the alligator wandering into a store? A real one walked into a Florida Walmart back in 2013.",
         "CLIP:trailer_1_00475", "WALMART, 2013", "laughs softly"),
        ("Even dirt bike crews racing around South Florida made the local news.",
         "CLIP:extended_look_11148", None, None),
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
        ("Reviewers also praise how packed and detailed the game's world feels.", "CLIP:trailer_1_00217", None, None),
        ("One roundup calls it the most reactive city Rockstar has built.", "CLIP:extended_look_10262",
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
        ("Rockstar sums up its GTA 6 characters in one sentence each, and one of them is way too relatable.",
         "CLIP:extended_look_03021", None, "curious"),
        ("First, Jason Duval, one of the two leads.", "CLIP:trailer_2_00232", None, None),
        ("Rockstar's line: \"Jason wants an easy life, but things just keep getting harder.\"",
         "CLIP:trailer_2_00081", "QUOTE: ROCKSTAR GAMES", None),
        ("Then Lucia Caminos, the other lead.", "CLIP:trailer_1_00065", None, None),
        ("Rockstar's bio says: \"Lucia's father taught her to fight as soon as she could walk.\"", "CLIP:trailer_2_00498",
         "QUOTE: ROCKSTAR GAMES", None),
        ("Brian Heder is Jason's landlord, and he runs a boat yard in the Keys.", "CLIP:launch_trailer_00026",
         None, None),
        ("Rockstar says: \"Brian's a classic drug runner from the golden age of smuggling in the Keys.\"",
         "CLIP:trailer_2_00851", "QUOTE: ROCKSTAR GAMES", None),
        ("In Vice City, Boobie Ike owns property, a club and a recording studio.", "CLIP:trailer_1_00341", None,
         None),
        ("The warning: \"Boobie's all smiles until it's time to talk business.\"", "CLIP:trailer_1_00325",
         "QUOTE: ROCKSTAR GAMES", None),
        ("Raul Bautista is a bank robber who is always hunting for talent.", "CLIP:extended_look_08740",
         None, None),
        ("And the way-too-relatable one goes to Jason's friend, Cal Hampton.", "CLIP:extended_look_15698", None, None),
        ("Rockstar says: \"Cal is at the low tide of America and happy there.\"", "CLIP:trailer_2_00831",
         "QUOTE: ROCKSTAR GAMES", None),
        ("In other words, he's at the bottom, and he's completely fine with it. Honestly? Same.",
         "CLIP:trailer_2_00895", "SAME, CAL", "laughs softly"),
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
        ("For comparison, the first trailer got about 93 million views in its first day, on YouTube alone.",
         "CLIP:trailer_1_00300", "TRAILER 1: 93M", None),
        ("And that was already huge for a GTA trailer.", "CLIP:trailer_1_00398", None, None),
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


# ---- 21 Nov 2026 (written and fact-checked in session, 20 Nov) ----

S["gta6-stream-record"] = dict(
    title="GTA 6 launch: 7.9 million people watching at once",
    thumb_text="7.9M WATCHING",
    hook_card="7.9 MILLION?",
    cover_lines=["7.9 MILLION WATCHED", "OTHERS PLAY IT", "AT THE SAME TIME"],
    cover_frame={"shot": "trailer_2_01400", "f": 0.5, "x": 0.68},   # jet ski, Jason + Lucia (cover as published)
    beats=[
        ("When GTA 6 unlocked this week, almost eight million people watched other people play it, all at once.",
         "CLIP:trailer_2_00232", None, "excited"),
        ("Streams Charts, which tracks livestreams, counted an early peak of over 7.9 million viewers.",
         "CLIP:extended_look_15524", "7.91M AT ONCE", None),
        ("That's the biggest game launch it has ever recorded.", "CLIP:extended_look_12735", None, None),
        ("The old launch record was Valorant's closed beta in 2020, with about 1.7 million.",
         "CLIP:extended_look_09432", "VALORANT, 2020: 1.74M", None),
        ("GTA 6 pulled in more than four times that.", "CLIP:launch_trailer_00685", "4.6X", "surprised"),
        ("On Twitch alone, it peaked at 3.31 million.", "CLIP:extended_look_12606", "TWITCH: 3.31M", None),
        ("That beat the Twitch record for any game, set by League of Legends in 2022.", "CLIP:extended_look_12327",
         "LOL WORLDS 2022: 3.11M", None),
        ("In one day, Twitch viewers watched thirty-six million hours of it.", "CLIP:extended_look_11437",
         "36M HOURS IN ONE DAY", None),
        ("Even the internet felt it: an internet exchange called DE-CIX set a traffic record.", "CLIP:extended_look_07501",
         "33 TERABITS A SECOND", None),
        ("So has anything drawn a bigger crowd on Twitch? Just one thing.", "CLIP:trailer_2_00346", None, "curious"),
        ("A 2025 boxing night called La Velada, with 9.68 million.", "CLIP:trailer_1_00341", "LA VELADA: 9.68M",
         None),
        ("So by Streams Charts' count, only a boxing night has ever beaten it on Twitch.",
         "CLIP:extended_look_07446", None, None),
        ("Were you playing it, or watching someone play it?", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Streams Charts (preliminary): GTA 6 peaked at more than 7.91 million concurrent viewers across "
                  "livestreaming platforms, the biggest game launch ever (all platforms); 3.31 million on Twitch, "
                  "overtaking League of Legends (3,111,143, T1-DRX Worlds 2022 final), the previous gaming record; "
                  "36,060,208 Twitch hours watched in one day, the most by a game; about 4.6 times Valorant's closed "
                  "beta; La Velada (2025 boxing event) still holds Twitch's overall record with 9.68 million.",
         "sources": ["https://streamscharts.com/news/gta-6-streaming-records"], "main": True},
        {"claim": "The previous launch leader was Valorant's closed beta in 2020 with a 1,737,267 peak (Streams Charts "
                  "data); GTA 6's combined peak was more than 7.88 million within three hours of release.",
         "sources": ["https://maketecheasier.com/gta-6-concurrent-viewer-record-streams-charts/"], "main": True},
        {"claim": "DE-CIX, an internet exchange operator, reached a new record-breaking high of 33.03 terabits per "
                  "second during the GTA 6 launch (Variety); Streams Charts: 7.91 million concurrent viewers at peak.",
         "sources": ["https://uk.news.yahoo.com/gta-6-launch-breaks-internet-150958798.html"], "main": True},
    ],
    description="Almost 8 million people watched GTA 6 streams at the same time. The records it broke, and the one "
                "it didn't.\nSources: Streams Charts (preliminary data), Make Tech Easier, Variety.",
    hashtags=["#GTA6", "#Twitch", "#GrandTheftAuto"],
)

S["gta6-dexter-apartment"] = dict(
    title="GTA 6 fans found Dexter's apartment in Vice City",
    thumb_text="DEXTER'S APARTMENT?",
    hook_card="DEXTER'S PLACE?",
    cover_lines=["FANS SAY THEY FOUND", "DEXTER'S APARTMENT", "IN VICE CITY"],
    cover_frame={"shot": "extended_look_08201", "f": 0.5, "x": 0.3},   # masked man (cover as published)
    beats=[
        ("GTA 6 fans have found a TV serial killer's apartment, hiding in Vice City.", "CLIP:extended_look_08816",
         None, "whispers"),
        ("In the show Dexter, he lives in Miami.", "CLIP:trailer_1_00300", None, None),
        ("And Vice City is Rockstar's Miami.", "CLIP:extended_look_04786", None, None),
        ("Players found his building. It's called Trinity Apartments, a nod to the show's Trinity Killer.",
         "CLIP:extended_look_04180", "TRINITY APARTMENTS", None),
        ("TheWrap says it's nearly a complete recreation of Dexter's apartment.", "CLIP:extended_look_04115", None,
         None),
        ("You can walk right up to the door, but you can't go inside.", "CLIP:extended_look_00000", None, None),
        ("The creepy part is on the roof, where players found a knife, tape, rope and a syringe.",
         "CLIP:trailer_2_00114", None, "serious"),
        ("Let's not ask what that's for.", "CLIP:launch_trailer_00423", None, "laughs softly"),
        ("Down at the docks, there's a boat you can steal.", "CLIP:launch_trailer_00026", None, None),
        ("Fans say it looks just like Slice of Life, Dexter's boat.", "CLIP:extended_look_15728", "SLICE OF LIFE?",
         None),
        ("Has Rockstar confirmed it? No. It hasn't said this is Dexter's home.", "CLIP:extended_look_12920", None,
         None),
        ("But fans had spotted this building back in August.", "CLIP:extended_look_09766",
         None, None),
        ("Which TV show should GTA hide next?", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Players found Dexter Morgan's apartment in Vice City; the complex is called Trinity Apartments (a "
                  "nod to the Trinity Killer); players can walk up to the door but cannot enter; on the roof is a "
                  "kill kit with a knife, tape, rope and a syringe; nearby players can steal a boat that resembles "
                  "Dexter's 'Slice of Life'; Rockstar hasn't explicitly identified the location as Dexter's home; "
                  "fans first flagged the building in August.",
         "sources": ["https://www.dexerto.com/gta/gta-6-players-find-dexters-apartment-serial-killer-kit-and-can-even-steal-his-boat-3429888/"],
         "main": True},
        {"claim": "TheWrap: 'nearly a complete recreation of Dexter Morgan's Miami apartment from the hit series "
                  "Dexter'; players can steal the 'Slice of Life' boat, find tools on the roof, and cannot enter.",
         "sources": ["https://www.thewrap.com/culture-lifestyle/culture/gta-6-dexter-morgan-apartment-easter-egg/"],
         "main": True},
    ],
    description="GTA 6 players found what looks like Dexter Morgan's Miami apartment in Vice City, a rooftop kit and "
                "his boat. Rockstar hasn't confirmed it.\nSources: Dexerto, TheWrap (19 Nov 2026).",
    hashtags=["#GTA6", "#Dexter", "#GTA6EasterEgg"],
)

S["gta6-story-length"] = dict(
    title="GTA 6 is about 50 hours long, one review says",
    thumb_text="50 HOURS?",
    hook_card="HOW LONG?",
    cover_lines=["HOW MANY HOURS", "TO FINISH THE STORY?", "A REVIEWER TIMED IT"],
    cover_frame={"shot": "trailer_1_00084", "f": 0.6, "x": 0.5},   # Lucia, prison jumpsuit (R3: face)
    beats=[
        ("How long does it actually take to finish GTA 6's story?", "CLIP:extended_look_07899", None, "curious"),
        ("ScreenRant's reviewer reached the end in fifty hours and forty-two minutes.", "CLIP:extended_look_11437",
         "50 HOURS 42 MINUTES", None),
        ("And that included some side content.", "CLIP:extended_look_10330", None, None),
        ("ScreenRant puts the main story at roughly fifty hours, told across five chapters.",
         "CLIP:trailer_2_00346", "5 CHAPTERS", None),
        ("Now compare that with GTA 5.", "OFFICIAL:v_c670974867", None, None),
        ("Since San Andreas, the main GTA stories have landed at around thirty hours.", "OFFICIAL:v_24ba6644de",
         "ABOUT 30 HOURS", None),
        ("So this one gives you roughly twenty extra hours of story.", "CLIP:extended_look_07501", "+20 HOURS",
         "surprised"),
        ("And the map it all happens on is roughly twice the size of GTA 5's.", "CLIP:extended_look_11275", None,
         None),
        ("Now the price. The standard edition costs $79.99.", "CLIP:trailer_2_00416", "$79.99", None),
        ("Spread over fifty hours, that's about a dollar sixty an hour.", "CLIP:extended_look_09166",
         "ABOUT $1.60 AN HOUR", None),
        ("ScreenRant says one hundred percent could take triple digits.", "CLIP:extended_look_10360",
         "100%: 100+ HOURS?", None),
        ("So you pay twenty dollars more than GTA 5 did, but you get a lot more game.",
         "CLIP:extended_look_05748", None, None),
        ("How many hours have you played so far?", "CLIP:extended_look_03869", None, None),
    ],
    facts=[
        {"claim": "ScreenRant: GTA 6's main story 'takes roughly 50 hours to complete, taking place across five "
                  "chapters'; its reviewer reached story completion at 50 hours and 42 minutes while doing some side "
                  "content; previous GTA games 'have landed around the 30-hour mark for main story content since GTA: "
                  "San Andreas'; the map is roughly twice the size of GTA 5; 100% completion could easily hit a "
                  "triple-digit runtime.",
         "sources": ["https://screenrant.com/gta-6-main-story-length-completion/"], "main": True},
        {"claim": "GTA V launched at $59.99 in the US; GTA 6 is $79.99. $79.99 over 50 hours is about $1.60 an hour "
                  "(arithmetic).",
         "sources": ["https://hothardware.com/news/gta-6-launch-80-single-player-title-rockstar-reveals"], "main": True},
    ],
    description="One review finished GTA 6's story in 50 hours 42 minutes. How that compares with GTA 5, and what it "
                "means for the $80 price.\nSources: ScreenRant (18 Nov 2026), HotHardware.",
    hashtags=["#GTA6", "#GTA6Review", "#GrandTheftAuto"],
)

S["gta6-sales-estimate"] = dict(
    title="GTA 6 sold 19 million copies? Here's the catch",
    thumb_text="19 MILLION?",
    hook_card="19 MILLION?",
    cover_lines=["19 MILLION SOLD", "ON DAY ONE?", "HERE'S THE CATCH"],
    cover_frame={"shot": "trailer_1_00686", "f": 0.5, "x": 0.35},   # masked Lucia, robbery
    beats=[
        ("By the morning GTA 6 came out, it may have already sold nineteen million copies.",
         "CLIP:extended_look_10196", None, "surprised"),
        ("But here's the catch. It's an estimate from an analytics firm, Sensor Tower, not from Rockstar.",
         "CLIP:extended_look_12920", None, None),
        ("Its estimate: about 19.1 million copies and 1.84 billion dollars.", "CLIP:extended_look_09994",
         "19.1M COPIES, $1.84B", None),
        ("Now think back to GTA 5's launch in 2013.", "OFFICIAL:v_c670974867", None, None),
        ("In its first twenty-four hours, it sold 11.21 million copies and made 815.7 million dollars.",
         "OFFICIAL:v_24ba6644de", "GTA 5: 11.21M, $815.7M", None),
        ("Those numbers were confirmed by Guinness World Records.", "OFFICIAL:v_fdac18d437", None, None),
        ("If the estimate is right, GTA 6 beat GTA 5's whole first day by Thursday morning.",
         "CLIP:launch_trailer_00685", None, "excited"),
        ("Sensor Tower says the Extended Look on Netflix helped drive a sixfold jump in pre-orders.",
         "CLIP:extended_look_04451", "6X PRE-ORDERS", None),
        ("And what does Take-Two say? It hasn't confirmed a single sales number.", "CLIP:extended_look_07446", None,
         None),
        ("Earlier this month, its CEO Strauss Zelnick even said, \"we still aren't ready to declare victory.\"",
         "CLIP:trailer_2_01188", "QUOTE: STRAUSS ZELNICK, TAKE-TWO", "serious"),
        ("Even so, nineteen million would beat GTA 5's first day of about eleven million.", "CLIP:extended_look_09166",
         None, None),
        ("Did you buy GTA 6 on day one?", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Sensor Tower estimates GTA VI sold 19.1 million units as of Thursday morning (19 Nov 2026), about "
                  "$1.84 billion in revenue; Take-Two has not given official sales figures; Zelnick on the earnings "
                  "call earlier this month: 'we still aren't ready to declare victory'; Sensor Tower: the Netflix "
                  "'Extended Look' helped drive a sixfold jump in pre-orders.",
         "sources": ["https://finance.yahoo.com/media-advertising/articles/two-set-shatter-sales-records-162847652.html"],
         "main": True},
        {"claim": "GTA VI sold an estimated 19.1 million copies by the morning of its release (Sensor Tower); "
                  "'Take-Two hasn't confirmed any numbers yet'.",
         "sources": ["https://www.mensjournal.com/news/gta-6-sales-19-million-copies-gta-v-record"], "main": True},
        {"claim": "GTA V made $815.7 million and sold 11.21 million copies in its first 24 hours (Guinness World "
                  "Records).",
         "sources": ["https://www.guinnessworldrecords.com/news/2013/10/confirmed-grand-theft--auto-breaks-six-sales-world-records-51900"],
         "main": True},
    ],
    description="An analytics firm estimates GTA 6 sold 19.1 million copies by launch morning. Take-Two hasn't "
                "confirmed a number yet.\nSources: Reuters (via Yahoo Finance), Men's Journal, Guinness World Records.",
    hashtags=["#GTA6", "#GTA5", "#GrandTheftAuto"],
)

S["gta6-first-look-2021"] = dict(
    title="GTA 6 fans think we saw it back in 2021",
    thumb_text="SEEN IN 2021?",
    hook_card="SEEN IN 2021?",
    cover_lines=["FANS SAY WE SAW IT", "BACK IN 2021", "WITHOUT NOTICING"],
    cover_frame={"shot": "extended_look_10196", "f": 0.5, "x": 0.5},   # Lucia close-up (cover as published, 21 Nov fix)
    beats=[
        ("Fans think GTA 6 was hiding in plain sight, years before its first trailer.", "CLIP:extended_look_03021",
         None, "curious"),
        ("In 2021, Rockstar released a remaster of GTA San Andreas.", "CLIP:trailer_2_00996",
         "SAN ANDREAS REMASTER, 2021", None),
        ("It had a picture of a house that only appeared in that version.", "CLIP:trailer_2_00188", None, None),
        ("Some fans wondered if it came from GTA 6's development.", "CLIP:extended_look_12920", None, None),
        ("Then fans mapping GTA 6's world found that same house, in Belville.",
         "CLIP:extended_look_11275", "BELVILLE", None),
        ("VGC says the two images line up down to the smallest details.", "CLIP:extended_look_10262", None,
         "surprised"),
        ("Even the plants and trees outside are in the same places.", "CLIP:extended_look_04786", None, None),
        ("So that 2021 picture may have been our first look at GTA 6.", "CLIP:trailer_2_00232", None, None),
        ("The first official trailer only came in December 2023.", "CLIP:trailer_1_00300", "TRAILER 1: DEC 2023",
         None),
        ("To be clear, it's a fan theory. Rockstar hasn't confirmed it.", "CLIP:trailer_2_00346", None, "serious"),
        ("If fans are right, we first saw GTA 6 back in 2021.",
         "CLIP:extended_look_07446", None, None),
        ("What other GTA 6 clues do you think fans missed?", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "A house in Belville in GTA 6 matches a house image from GTA: San Andreas - Definitive Edition "
                  "(2021); the image was exclusive to that edition and was speculated to come from GTA 6 development; "
                  "found by a member of the GTA VI Mapping server; 'The two images of the houses line up to the "
                  "smallest details, like the placement of plants and trees outside of the home'; VGC: it 'may have "
                  "been our first look at GTA 6'. A fan theory; no Rockstar comment reported.",
         "sources": ["https://www.videogameschronicle.com/news/gta-6-players-discover-our-real-first-look-at-the-game-was-likely-hidden-in-a-2021-remaster/"],
         "main": True},
        {"claim": "GTA 6's first trailer was released in December 2023.",
         "sources": ["https://www.videogameschronicle.com/news/the-gta-6-trailer-has-allegedly-leaked-online/"],
         "main": False},
    ],
    description="Fans matched a house in GTA 6's Belville to a picture in 2021's San Andreas remaster. Was it our "
                "first look? A fan theory; Rockstar hasn't confirmed it.\nSource: VGC (18 Nov 2026).",
    hashtags=["#GTA6", "#GTASanAndreas", "#GrandTheftAuto"],
)


# ---- 21 Nov 2026 (daily run): remake of tonight's sales video (Rockstar published official numbers on 20 Nov) ----
S["gta6-official-sales"] = dict(
    title="GTA 6 made $3.79 billion on day one, Rockstar says",
    thumb_text="$3.79 BILLION",
    hook_card="$3.79 BILLION?",
    cover_lines=["$3.79 BILLION", "IN ONE DAY?", "BIGGER THAN ANY MOVIE"],
    cover_frame={"shot": "launch_trailer_00119", "f": 0.5, "x": 0.67},   # Jason on the phone, marina (R3: face)
    beats=[
        ("By the end of day one, GTA 6 had made more money than any movie ever made in its whole run.",
         "CLIP:extended_look_10132", None, "excited"),
        ("On Friday, Rockstar announced it: 3.79 billion dollars in day one sales.", "CLIP:extended_look_07446",
         "$3.79 BILLION", None),
        ("That counts pre-orders and sales worldwide, up to the end of launch day.", "CLIP:trailer_1_00300",
         "TO THE END OF 19 NOV", None),
        ("Rockstar also says it sold 32.5 million copies before the game even came out.",
         "CLIP:extended_look_09994", "32.5M COPIES PRE-RELEASE", None),
        ("Before launch, an analytics firm had estimated nineteen million copies. Rockstar's own number is much bigger.",
         "CLIP:extended_look_12920", None, "surprised"),
        ("Now go back to GTA 5 in 2013.", "OFFICIAL:v_c670974867", None, None),
        ("In its first twenty-four hours, it made 815.7 million dollars, a Guinness World Record.",
         "OFFICIAL:v_24ba6644de", "GTA 5: $815.7M", None),
        ("So GTA 6's first day was more than four times bigger.", "CLIP:launch_trailer_00685", "4.6X GTA 5", None),
        ("And the movies? Avatar, the highest-grossing film ever, made about 2.9 billion dollars in its whole run.",
         "CLIP:extended_look_07501", "AVATAR: $2.92B ALL-TIME", None),
        ("Rockstar calls it the biggest entertainment launch in history.", "CLIP:trailer_2_00346", None, None),
        ("Did you buy it on day one, or are you waiting for a sale? Pick a side. "
         "Follow for a new GTA 6 secret every day.", "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Rockstar Games press release (Take-Two 8-K exhibit 99.1, New York, 20 Nov 2026): 'Grand Theft Auto "
                  "VI Shatters Entertainment Box Office Records with $3.79 Billion in Day One Retail Sales'; day one "
                  "retail sales based on company estimates through end of day November 19th worldwide; 'sold 32.5 "
                  "million units pre-release, a new record across all platforms'; 'the biggest entertainment launch "
                  "in history'.",
         "sources": ["https://www.sec.gov/Archives/edgar/data/0000946581/000162828026075217/exhibit9918k.htm"],
         "main": True},
        {"claim": "Variety: 'preorder and first-day sales reached $3.79 billion, the game developer announced "
                  "Friday'; it 'has already out-grossed the highest grossing movie of all time, 'Avengers: Endgame' ($2.9 "
                  "billion), in one day' (Wikipedia: Avatar now holds that record at $2.923B; both are below $3.79B).",
         "sources": ["https://au.variety.com/2026/more/news/gta-6-sales-billions-first-day-42778/"], "main": True},
        {"claim": "Highest-grossing film: Avatar, $2.923 billion worldwide (reclaimed the record from Avengers: "
                  "Endgame, $2.797 billion, in March 2021).",
         "sources": ["https://en.wikipedia.org/wiki/List_of_box_office_records_set_by_Avengers:_Endgame"],
         "main": True},
        {"claim": "Sensor Tower, an analytics firm, had estimated 19.1 million copies by the morning of release.",
         "sources": ["https://finance.yahoo.com/media-advertising/articles/two-set-shatter-sales-records-162847652.html"],
         "main": False},
        {"claim": "GTA V made $815.7 million in its first 24 hours, one of six sales world records confirmed by Guinness "
                  "World Records. $3.79B / $815.7M = 4.6.",
         "sources": ["https://www.guinnessworldrecords.com/news/2013/10/confirmed-grand-theft--auto-breaks-six-sales-world-records-51900"],
         "main": True},
    ],
    description="Rockstar says GTA 6 made $3.79 billion in day one retail sales (pre-orders included, to the end of "
                "19 Nov) and sold 32.5 million copies before release: more than any film's whole box office run.\n"
                "Sources: Rockstar Games / Take-Two press release (20 Nov 2026), Variety, Guinness World Records, "
                "Wikipedia (box office records).",
    hashtags=["#GTA6", "#GTA5", "#GrandTheftAuto"],
)


# ---- 22 Nov 2026 batch (written 21 Nov by the daily run; E1 short = kodak-radio + true-fat-jason; E2 = all) ----
S["gta6-console-best"] = dict(
    title="GTA 6 runs best on one console. Here's which",
    thumb_text="WHICH CONSOLE?",
    hook_card="WHICH CONSOLE?",
    cover_lines=["WHICH CONSOLE", "RUNS IT BEST?", "ONE STRUGGLES"],
    cover_frame={"shot": "trailer_1_00625", "f": 0.5, "x": 0.44},   # Lucia, red bandana, cash (R3: face)
    experiment="E1-long",
    beats=[
        ("On the wrong console, GTA 6 can drop to around twenty frames a second.", "CLIP:trailer_2_00232", None,
         "serious"),
        ("Digital Foundry tested them all. First, the bad news.",
         "CLIP:extended_look_09166", None, None),
        ("Every console aims for thirty frames a second. There's no sixty frames mode.",
         "CLIP:extended_look_07501", "30 FPS ON EVERY CONSOLE", None),
        ("Rockstar told Kotaku the consoles can't run its simulation any faster.",
         "CLIP:extended_look_12327", None, None),
        ("So which one holds thirty best?", "CLIP:extended_look_10833", None, "curious"),
        ("Last place: the Xbox Series S.", "CLIP:extended_look_10674", "LAST: SERIES S", None),
        ("It runs at just 720p, and in big shootouts it falls to around twenty.",
         "CLIP:extended_look_09432", "720p, ~20 FPS", None),
        ("The base PS5 and Series X sit in the middle, both at 1440p.", "CLIP:trailer_2_00346",
         "PS5 + SERIES X: 1440p", None),
        ("Blow up enough cars, and the PS5 dips to twenty-three.", "CLIP:trailer_2_01113", "PS5: DIPS TO 23",
         None),
        ("The Series X dips a bit lower, but on a 120 hertz VRR TV, those dips feel smoother.",
         "CLIP:extended_look_11192", "SERIES X: VRR HELPS", None),
        ("And the winner is the PS5 Pro.", "CLIP:launch_trailer_00685", "WINNER: PS5 PRO", "excited"),
        ("It's the only one with ray-traced shadows, and it looks close to native 4K.",
         "CLIP:extended_look_07446", "NEAR-4K + RT SHADOWS", None),
        ("On the Pro, Digital Foundry saw no drops in fifty hours of normal play.", "CLIP:extended_look_11275",
         None, None),
        ("PlayStation or Xbox: which side are you on? Follow for more GTA 6 tips.",
         "CLIP:trailer_2_00920", None, None),
    ],
    facts=[
        {"claim": "Digital Foundry (18 Nov 2026): every version targets 30 fps, no 40/60 fps mode; PS5 Pro 1440p "
                  "internal with PSSR to a near-4K image, the only version with ray-traced shadows, brief drops to "
                  "~24 fps only in an explosion-heavy test, ranked best; base PS5 and Series X 1440p internal, "
                  "spatially upscaled; Series X dips a touch below PS5 (~20-22 fps worst) with 120 Hz VRR and LFC "
                  "smoothing dips on a compatible TV; Series S 720p with FSR to ~1080p, 'around 20 FPS or lower' in "
                  "the heaviest action, a 'distant fourth'.",
         "sources": ["https://www.gtaboom.com/digital-foundry-finds-that-gta-6-indeed-runs-best-on-ps5-pro-b72f"],
         "main": True},
        {"claim": "Base PS5 dips as low as 23 fps when blowing up vehicles; DF saw no dips in normal play over 50+ "
                  "hours on PS5 Pro; DF called the Pro 'the best way to play this game by far'.",
         "sources": ["https://www.altchar.com/game-news/gta-vi-dips-as-low-as-23fps-on-base-ps5-in-heavy-action-digital-foundry-finds-aJybE7x7IsZa"],
         "main": True},
        {"claim": "Rockstar's Marc Chambers to Kotaku (18 Nov 2026): the hardware 'is not powerful enough to run the "
                  "game's complex simulation at higher frame rates'.",
         "sources": ["https://endgametools.com/en/gta-6/news/gta-6-30-fps-target",
                     "https://kotaku.com/grand-theft-auto-6-gta6-performance-framerate-ps5-xbox-series-x-s-2000758096"],
         "main": True},
    ],
    description="Digital Foundry tested GTA 6 on PS5, PS5 Pro, Xbox Series X and Series S. All aim for 30 fps; one "
                "holds it best, one struggles.\nSources: Digital Foundry (via GTA BOOM, AltChar, Endgame Tools), "
                "Kotaku.",
    hashtags=["#GTA6", "#PS5Pro", "#Xbox"],
)

S["gta6-dating-lucia"] = dict(
    title="Is dating Lucia in GTA 6 cheating? Couples disagree",
    thumb_text="IS IT CHEATING?",
    hook_card="IS IT CHEATING?",
    cover_lines=["IS DATING LUCIA", "CHEATING?", "COUPLES ARE ARGUING"],
    cover_frame={"shot": "trailer_1_00728", "f": 0.5, "x": 0.3},   # Lucia leaning over Jason, motel (R3: face)
    experiment="E1-long",
    beats=[
        ("Real couples are arguing over GTA 6. The question: is dating Lucia cheating?",
         "CLIP:trailer_2_00920", None, "amused"),
        ("In the game, you can look after Jason and Lucia's relationship.",
         "CLIP:extended_look_03869", None, None),
        ("Buy her flowers, pick up groceries, fix up the house, and a little heart pops up.",
         "CLIP:trailer_2_00416", None, None),
        ("You can hold her hand.", "CLIP:trailer_2_00976", None, None),
        ("And Vice says even a robbery together counts as quality time.", "CLIP:trailer_1_00686", None,
         None),
        ("Ignore her goodnight text, and it can hurt the relationship a little.", "CLIP:extended_look_03894", None,
         None),
        ("Online, people are fighting over whether dating Lucia is cheating on your real partner.",
         "CLIP:extended_look_06535", None, None),
        ("One Reddit user wrote, \"Don't treat AI better than your actual girl.\"", "CLIP:trailer_1_00300", None,
         None),
        ("Others say if a game ends your relationship, it was ending anyway.",
         "CLIP:extended_look_06595", None, None),
        ("Some couples are even signing ten-day deals: no interruptions until November 29th.",
         "CLIP:trailer_2_01344", "10-DAY 'GTA CONTRACTS'", None),
        ("And here's the twist: in the game, there's no one else to date.", "CLIP:trailer_2_00759", None,
         "surprised"),
        ("And you can't break up with her.", "CLIP:trailer_2_01437", None, None),
        ("Is dating Lucia cheating: yes or no? Pick a side. Follow for more GTA 6 facts.",
         "CLIP:extended_look_07899", None, None),
    ],
    facts=[
        {"claim": "Relationship tasks Lucia appreciates (Chapter 1): fix the car, buy flowers, pick up groceries, order "
                  "a necklace, haircut, house repairs; a heart notification appears when an action changes the "
                  "relationship; no romance option with anyone else and you can't break up (Output Lag, checked 20 "
                  "Nov 2026).",
         "sources": ["https://outputlag.com/guides/gta-6-lucia-relationship/"], "main": True},
        {"claim": "Vice (18 Nov 2026): hold R2 to hold hands; 'Even robbing a bank together counts as quality time'; "
                  "ignoring the goodnight text 'can hurt their relationship a little'; the romance is optional.",
         "sources": ["https://www.vice.com/en/article/gta-6-dating-vice-city/"], "main": True},
        {"claim": "Unilad (19 Nov 2026): heated arguments across TikTok, X and Reddit over whether in-game courtship "
                  "counts as cheating; a Reddit user: 'Don't treat AI better than your actual girl.'; pushback: 'If "
                  "'dating' a non-existent digital character is the cause for your relationship to end, it was going "
                  "to end anyway.'; couples signing 10-day 'contracts' to stop mission interruptions until November "
                  "29.",
         "sources": ["https://www.unilad.com/technology/gta-6-sparks-fierce-debate-in-game-courtship-counts-as-cheating-513504-20261119"],
         "main": True},
    ],
    description="Flowers, groceries, holding hands: GTA 6 lets you look after Jason and Lucia's relationship, and "
                "real couples are arguing about it.\nSources: Unilad, Vice, Output Lag.",
    hashtags=["#GTA6", "#Lucia", "#GrandTheftAuto"],
)

S["gta6-kodak-radio"] = dict(
    title="GTA 6 has a secret Kodak Black radio station",
    thumb_text="SECRET STATION",
    hook_card="SECRET STATION?",
    cover_lines=["KODAK BLACK HAS", "A SECRET STATION", "HOW TO UNLOCK IT"],
    cover_frame={"shot": "trailer_2_00795", "f": 0.5, "x": 0.31},   # Lucia + Jason, drinks at a bar (R3: face)
    experiment="E1-short",
    beats=[
        ("GTA 6 has a secret radio station, and it isn't on the normal dial.", "CLIP:extended_look_07899",
         None, "curious"),
        ("Vice says it's hosted by rapper Kodak Black, and it's called The Sniper of La Perle.",
         "CLIP:extended_look_12606", "THE SNIPER OF LA PERLE", None),
        ("To unlock it, you have to scan four posters around Vice City.",
         "CLIP:extended_look_10262", "SCAN 4 POSTERS", None),
        ("Three are in La Perle: Aunt Zola's Soul Food, TWA Ponya Tattoo, and the Drip Drops clothing store.", "CLIP:extended_look_12327", "3 IN LA PERLE", None),
        ("The fourth is upstairs at the Jack of Hearts club in Crosstown.", "CLIP:extended_look_10510",
         "JACK OF HEARTS CLUB", None),
        ("Find all four, and you unlock twenty-two songs, including Kodak Black's own.", "CLIP:extended_look_12735",
         "22 SONGS", "excited"),
        ("Going for one hundred percent? You need it.", "CLIP:extended_look_11275", None, None),
        ("Kodak Black or Weird Al's eighties station: which side are you on? Follow for more GTA 6 secrets.",
         "CLIP:extended_look_05748", None, None),
    ],
    facts=[
        {"claim": "Vice (20 Nov 2026): a hidden playlist, 'The Sniper of La Perle', hosted by Kodak Black, not on the "
                  "main dial; unlocked by scanning four posters: Aunt Zola's Soul Food (cashier), TWA Ponya Tattoo "
                  "(entrance) and Drip Drops clothing store (counter) in La Perle, and an upstairs studio poster at "
                  "the Jack of Hearts club in Crosstown; 22 songs including Kodak Black tracks; needed for the 'Unique "
                  "Playlists' requirement for 100% completion.",
         "sources": ["https://www.vice.com/en/article/gta-6-players-discover-secret-radio-station-hosted-by-florida-rap-star-kodak-black/"],
         "main": True},
        {"claim": "Weird Al hosts an '80s hits radio station in GTA 6 (Kotaku's list of details players spotted).",
         "sources": ["https://kotaku.com/18-coolest-details-players-have-spotted-in-gta-6-so-far-2000758435"],
         "main": False},
    ],
    description="How to unlock The Sniper of La Perle, GTA 6's hidden Kodak Black station: four posters, three in "
                "La Perle and one in Crosstown.\nSources: Vice, Kotaku.",
    hashtags=["#GTA6", "#KodakBlack", "#GTA6Tips"],
)

S["gta6-weird-secrets"] = dict(
    title="GTA 6's weirdest secrets players found in week one",
    thumb_text="BIGFOOT IS REAL?",
    hook_card="BIGFOOT?",
    cover_lines=["BIGFOOT IS REAL?", "PLAYERS FOUND", "THE WEIRDEST SECRETS"],
    cover_frame={"shot": "launch_trailer_00263", "f": 0.5, "x": 0.25},   # Lucia in a red convertible (R3: face)
    experiment="E1-long",
    beats=[
        ("GTA 6 players have found Bigfoot, and he's not even the weirdest secret.", "CLIP:extended_look_10196",
         None, "amused"),
        ("Kotaku rounded up what players spotted, and it gets strange fast.",
         "CLIP:trailer_1_00183", None, None),
        ("First, players have spotted Bigfoot in the game. And UFOs too.", "CLIP:extended_look_04675", "BIGFOOT + UFOs", "surprised"),
        ("Somewhere out there, there's even a giant crab monster.", "CLIP:extended_look_10360", None, None),
        ("Get stranded at sea, and a dog riding a jet ski can show up to save you.", "CLIP:extended_look_10450",
         None, None),
        ("It takes you to an island of dogs, with hidden treasure worth over twelve hundred dollars.",
         "CLIP:trailer_2_00188", "$1,200+ TREASURE", None),
        ("Fans think it's based on Loosy, a real Florida dog whose jet ski ride went viral.",
         "CLIP:launch_trailer_00026", "LOOSY, FORT LAUDERDALE", None),
        ("Rockstar hasn't confirmed that.", "CLIP:trailer_1_00398", None, None),
        ("There are sixty-two different kinds of birds.", "CLIP:extended_look_04645", "62 KINDS OF BIRDS", None),
        ("And one of them is an old friend: Tony, the bird from GTA San Andreas, makes a cameo.",
         "CLIP:extended_look_04501", "TONY FROM SAN ANDREAS", None),
        ("You can even steal a scooter from an old lady.", "CLIP:extended_look_10262", None, "laughs softly"),
        ("And that's only what players have found so far.", "CLIP:extended_look_07446", None, None),
        ("Bigfoot or the jet ski dog: which is the best secret? Follow for more GTA 6 secrets.",
         "CLIP:trailer_2_00232", None, None),
    ],
    facts=[
        {"claim": "Kotaku (19-20 Nov 2026), details players spotted: steal a scooter from an old lady; a dog can ride a "
                  "jet ski; Bigfoot is real, UFOs exist, and there is a giant crab monster; 62 different kinds of "
                  "birds; Tony the bird from San Andreas makes a cameo; Weird Al hosts an '80s station.",
         "sources": ["https://kotaku.com/18-coolest-details-players-have-spotted-in-gta-6-so-far-2000758435"],
         "main": True},
        {"claim": "Parade (20 Nov 2026): if a protagonist is stranded at sea, 'a dog riding a jet-ski will appear' and "
                  "takes them to an island of dogs with hidden treasure worth over $1,200; the dog is 'likely based "
                  "on a real-life pup', Loosy, whose personal-watercraft ride in Fort Lauderdale went viral in May; "
                  "not confirmed by Rockstar.",
         "sources": ["https://parade.com/entertainment/gta-6-players-discover-beloved-character-may-be-based-on-real-florida-dog"],
         "main": True},
    ],
    description="Bigfoot, UFOs, a giant crab monster, a jet-ski rescue dog and a San Andreas cameo: the strangest "
                "things players found in GTA 6's first days.\nSources: Kotaku, Parade.",
    hashtags=["#GTA6", "#GTA6Secrets", "#GrandTheftAuto"],
)

S["gta6-true-fat-jason"] = dict(
    title="GTA 6 players are trying to make Jason fat",
    thumb_text="TRUE FAT JASON",
    hook_card="HOW FAT?",
    cover_lines=["HOW FAT CAN", "JASON GET?", "PLAYERS TRIED IT"],
    cover_frame={"shot": "extended_look_10387", "f": 0.5, "x": 0.5},   # Lucia bench pressing (R3: face)
    experiment="E1-short",
    beats=[
        ("GTA 6 players have a new mission: make Jason as fat as possible.", "CLIP:extended_look_03021", None,
         "amused"),
        ("San Andreas' old weight system is back.", "CLIP:trailer_2_00383", None, None),
        ("Eat too much, and Jason or Lucia gains weight. Work out, and they build muscle.",
         "CLIP:extended_look_10387", None, None),
        ("One fan posted a max weight, low muscle Jason and called him True Fat Jason.", "CLIP:trailer_2_00114",
         "'TRUE FAT JASON'", None),
        ("The trick GamesRadar shared: eat at least four burgers or tacos, sleep, and skip the gym.",
         "CLIP:extended_look_07238", "4+ BURGERS, NO GYM", None),
        ("But here's the twist: True Fat Jason isn't very fat at all.", "CLIP:extended_look_03869", None,
         "surprised"),
        ("GamesRadar says neither he nor max weight Lucia seems quite as big as Arthur Morgan at his heaviest.",
         "CLIP:extended_look_10196", None, None),
        ("Gym Jason or True Fat Jason: which one are you building? Follow for more GTA 6 secrets.",
         "CLIP:trailer_2_00232", None, None),
    ],
    facts=[
        {"claim": "GamesRadar (19 Nov 2026): a fan posted 'max weight, low muscle Jason AKA the True Fat Jason'; a fan "
                  "method: 'eat at least four burgers or tacos', sleep, eat more, avoid workouts; 'Neither seems quite "
                  "as big as Arthur Morgan's at his heaviest'; headline: 'True Fat Jason' and 'max weight Lucia' "
                  "aren't very fat at all.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/gta-6-players-confirm-true-fat-jason-and-max-weight-lucia-arent-very-fat-at-all-setting-the-stage-for-the-first-pc-mod-to-super-size-them/"],
         "main": True},
        {"claim": "LADbible: Rockstar is bringing back San Andreas' weight and muscle system; 'Eating changes Jason and "
                  "Lucia's body weight.' 'Exercise visibly builds and tones their muscles.'",
         "sources": ["https://www.ladbible.com/entertainment/gaming/gta-6-gameplay-lucia-jason-weight-gain-feature-578092-20260827"],
         "main": True},
    ],
    description="San Andreas' weight system is back, and players are chasing 'True Fat Jason'. It turns out he isn't "
                "very fat at all.\nSources: GamesRadar, LADbible.",
    hashtags=["#GTA6", "#GTASanAndreas", "#GrandTheftAuto"],
)


# ---- 23 Nov 2026 batch (written 22 Nov by the daily run; E1 short = map-size + zelda-score; E2 = all) ----
S["gta6-lucia-actor"] = dict(
    title="GTA 6's Lucia actress was in GTA 5 all along",
    thumb_text="SHE WAS IN GTA 5",
    hook_card="SHE WAS IN GTA 5?",
    cover_lines=["LUCIA'S ACTRESS", "WAS IN GTA 5?", "SPOT HER ROLE"],
    cover_frame={"shot": "trailer_2_00961", "f": 0.5, "x": 0.4},   # Lucia, green dress, rooftop bar (R3: face)
    experiment="E1-long",
    beats=[
        ("The woman who plays Lucia in GTA 6 was already in GTA 5. You just never noticed.",
         "CLIP:extended_look_08816", None, "curious"),
        ("Her name is Manni Perez, and she's nominated at the Game Awards for Best Performance, as Lucia.",
         "CLIP:extended_look_10196", "LUCIA: MANNI L. PEREZ", None),
        ("LADbible checked her IMDb, and her very first credit is GTA 5.", "OFFICIAL:v_c670974867",
         "FIRST CREDIT: GTA 5", None),
        ("She voiced a character called Clubber number two.", "CLIP:trailer_1_00341", "'CLUBBER 2'", "amused"),
        ("Then, in a 2019 GTA Online update, she was a blackjack dealer with no name.", "OFFICIAL:v_7f4ce4e75d",
         "UNNAMED DEALER, 2019", None),
        ("On TV, she's been in Jessica Jones, The Blacklist and Law and Order.", "CLIP:trailer_2_01293", None, None),
        ("And she trains in Muay Thai, Brazilian jiu-jitsu and MMA.", "CLIP:extended_look_10387", None, None),
        ("Back in 2018, she said her biggest fear was playing a woman who needs to be saved by a man.",
         "CLIP:extended_look_03021", None, None),
        ("And Jason? Dylan Rourke posted on Instagram that he played him.", "CLIP:trailer_2_00232",
         "JASON: DYLAN ROURKE", "excited"),
        ("It's his first video game. Before this, he was on Station 19 and Modern Family.",
         "CLIP:extended_look_07899", None, None),
        ("His message to fans ended with: See y'all in Leonida.", "CLIP:trailer_1_00356", None, None),
        ("Lucia or Jason: whose story are you here for? Pick a side. Follow for more GTA 6 secrets.",
         "CLIP:extended_look_05748", None, None),
    ],
    facts=[
        {"claim": "LADbible (19 Nov 2026): Lucia is played by Manni L Perez (she shared the character graphic on her "
                  "Instagram); her first IMDb credit is 'Clubber 2' in GTA V; TV: Jessica Jones, The Blacklist, "
                  "Chicago P.D., Law & Order: SVU; trains Muay Thai, Brazilian jiu-jitsu, MMA. Dylan Rourke revealed "
                  "on Instagram that he played Jason; his statement ends 'See y'all in Leonida.'; his credits include "
                  "Station 19 and Modern Family.",
         "sources": ["https://www.ladbible.com/entertainment/gaming/gta-6-jason-lucia-manni-perez-dylan-rourke-484374-20261119"],
         "main": True},
        {"claim": "Yahoo (19 Nov 2026): Perez was nominated at the Game Awards for Best Performance for her voice work "
                  "as Lucia; credited as the voice of Clubber #2 in GTA V; an unnamed blackjack dealer in a 2019 GTA "
                  "Online update; 2018 Paz Magazine: 'my biggest fear is to play a woman that needs to be saved by a "
                  "man'.",
         "sources": ["https://www.yahoo.com/entertainment/celebrity/article/the-gta-6-voice-actor-for-lucia-has-finally-been-revealed-what-to-know-about-manni-perez-161144388.html"],
         "main": True},
        {"claim": "ScreenRant (19 Nov 2026): Jason is played by Dylan Rourke; GTA 6 is his video game debut; earlier TV "
                  "parts include Station 19 (three episodes) and Modern Family.",
         "sources": ["https://screenrant.com/gta-6-cast-voice-actors/"], "main": True},
    ],
    description="Lucia's actress Manni L. Perez had a tiny voice role in GTA 5 years before GTA 6. Plus Jason's "
                "actor, Dylan Rourke.\nSources: LADbible, Yahoo, ScreenRant.",
    hashtags=["#GTA6", "#Lucia", "#GTA5"],
)

S["gta6-map-size"] = dict(
    title="GTA 6's map vs GTA 5: how big is it really?",
    thumb_text="HOW BIG?",
    hook_card="HOW BIG?",
    cover_lines=["TWICE AS BIG", "AS GTA 5?", "WHAT WE KNOW"],
    cover_frame={"shot": "trailer_2_00232", "f": 0.5, "x": 0.6},   # Jason driving, close-up (R3: face)
    experiment="E1-short",
    beats=[
        ("How much bigger is GTA 6's map than GTA 5's? Here's what's actually known.", "CLIP:trailer_2_00232",
         None, "curious"),
        ("First, Rockstar has never given a size in square miles.", "CLIP:trailer_1_00300", None, None),
        ("But Forbes reports Rockstar puts it at around twice the size of GTA 5's map.", "OFFICIAL:v_3360902d78",
         "ABOUT 2x GTA 5", None),
        ("And a YouTuber who spoke to Rockstar says it's three times Red Dead Redemption 2.",
         "CLIP:trailer_1_00183", "3x RDR2 (REPORTED)", None),
        ("There are six regions, from Vice City to the swamps and the Keys.", "CLIP:extended_look_10298", "6 REGIONS",
         None),
        ("Game Informer counted more than a hundred and seventy animal species.", "CLIP:extended_look_04645",
         "170+ ANIMAL SPECIES", "surprised"),
        ("And one estimate says driving across it takes about thirty-five minutes.", "CLIP:extended_look_07501",
         "~35 MIN TO CROSS", None),
        ("Bigger map or more detail: which matters more to you? Pick a side. Follow for more GTA 6 facts.",
         "CLIP:extended_look_11275", None, None),
    ],
    facts=[
        {"claim": "GTA Zone (updated 29 Oct 2026): 'Rockstar still hasn't published a square-mile figure, but it now "
                  "gives ratios' (roughly twice GTA 5).",
         "sources": ["https://gta-zone.com/news/gta-6-map-size/"], "main": True},
        {"claim": "Forbes (6 Oct 2026): 'GTA 6's Leonida is around twice the size of GTA 5's map, per Rockstar'; six "
                  "regions (Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia, Mount Kalaga National "
                  "Park); more than 170 animal species (Game Informer cover story).",
         "sources": ["https://www.forbes.com/sites/brianmazique/2026/10/06/gta-6s-map-is-about-twice-the-size-of-gta-5-with-hurricanes-and-170-animal-species/"],
         "main": True},
        {"claim": "SlashGear (19 Nov 2026): YouTuber TGG says Rockstar told him the map is three times RDR2's and twice "
                  "GTA V's; estimates (from outside Rockstar) say about 35 minutes to drive across the map.",
         "sources": ["https://www.slashgear.com/2319631/grand-theft-auto-6-map-huge-bigger-than-originally-thought/"],
         "main": True},
    ],
    description="Rockstar never gave GTA 6's map size in square miles. Here's what's reported: about twice GTA 5, "
                "six regions, 170+ animal species.\nSources: Forbes, SlashGear, GTA Zone.",
    hashtags=["#GTA6", "#GTA6Map", "#GTA5"],
)

S["gta6-online-when"] = dict(
    title="GTA 6 has no online mode. When is it coming?",
    thumb_text="NO ONLINE?",
    hook_card="NO ONLINE?",
    cover_lines=["NO ONLINE MODE?", "WHEN DOES IT", "FINALLY COME?"],
    cover_frame={"shot": "extended_look_03869", "f": 0.5, "x": 0.2},   # Jason in a tank top with Lucia (R3: face)
    experiment="E1-long",
    beats=[
        ("You can't play GTA 6 with your friends. Not online, and not on the same couch.",
         "CLIP:extended_look_03021", None, "serious"),
        ("The store pages say it plainly: Grand Theft Auto Six is a single-player experience.",
         "CLIP:extended_look_09166", "SINGLE-PLAYER ONLY", None),
        ("But GTA 5 didn't have online on day one either. It came out on September 17th, 2013.",
         "OFFICIAL:v_c670974867", None, None),
        ("GTA Online followed two weeks later, on October 1st.", "OFFICIAL:v_7f4ce4e75d", "+2 WEEKS", None),
        ("So where is GTA 6's online mode? So far, Rockstar and Take-Two haven't announced one, or a date.",
         "CLIP:extended_look_12920", "NO DATE YET", "curious"),
        ("The biggest hint came from Twitch's boss, Dan Clancy, in September.", "CLIP:extended_look_15524", None,
         None),
        ("He told Bloomberg there'd be a big bump with GTA 6, \"but then an even bigger one next year when they "
         "launch multiplayer.\"", "CLIP:extended_look_12606", "'NEXT YEAR'", None),
        ("Bloomberg's Jason Schreier has also reported that the online part is expected in 2027.",
         "CLIP:extended_look_07446", "EXPECTED: 2027", None),
        ("Rockstar hasn't confirmed that.", "CLIP:trailer_1_00398", None, None),
        ("Meanwhile, Take-Two says it will keep supporting GTA Online on GTA 5.", "OFFICIAL:v_07edb091bb", None,
         None),
        ("Story first, or online first: which one do you care about more? Pick a side. Follow for more GTA 6 "
         "facts.", "CLIP:extended_look_05748", None, None),
    ],
    facts=[
        {"claim": "Leonipedia (updated 21 Nov 2026): 'Status as of November 21, 2026: no online mode announced for GTA "
                  "6'; the PlayStation and Xbox store pages say 'Grand Theft Auto VI is a single-player experience'; "
                  "PlayStation Store: 1 player; Bloomberg's Jason Schreier (14 Oct 2026): the online component 'is "
                  "expected to be released in 2027'; Zelnick: 'We do expect to support GTA Online going forward.'",
         "sources": ["https://leonipedia.com/guides/online-release-date/"], "main": True},
        {"claim": "GameVerse (19 Nov 2026): GTA 6 is out and solo only: no online, no co-op, no split-screen; Rockstar "
                  "and Take-Two have not announced, named or dated an online mode.",
         "sources": ["https://gameverse.app/blog/gta-6-multiplayer"], "main": True},
        {"claim": "Just Jared (17 Nov 2026): GTA V launched 17 Sept 2013 and GTA Online arrived 1 Oct 2013, about two "
                  "weeks later; Twitch CEO Dan Clancy to Bloomberg (Sept 2026): 'You are going to see this big bump "
                  "with GTA 6, but then an even bigger one next year when they launch multiplayer.'",
         "sources": ["https://www.justjared.com/2026/11/17/gta-6-online-release-date-multiplayer-launch/"],
         "main": True},
    ],
    description="GTA 6 launched single-player only. GTA Online came two weeks after GTA 5; for GTA 6, Rockstar hasn't "
                "announced an online mode or date.\nSources: Leonipedia, GameVerse, Just Jared (Bloomberg).",
    hashtags=["#GTA6", "#GTAOnline", "#GTA6Online"],
)

S["gta6-zelda-score"] = dict(
    title="GTA 6's Metacritic fight just dragged in Zelda",
    thumb_text="99 OR 5.6?",
    hook_card="99 OR 5.6?",
    cover_lines=["CRITICS SAY 99", "PLAYERS SAY 5.6", "WHO'S RIGHT?"],
    cover_frame={"shot": "trailer_2_00631", "f": 0.5, "x": 0.25},   # Lucia in the prison yard (R3: face)
    experiment="E1-short",
    beats=[
        ("GTA 6's score fight has dragged in a game from 1998: Zelda.", "CLIP:trailer_1_00728", None, "amused"),
        ("On Metacritic, critics gave it ninety-nine. That ties the all-time record.", "CLIP:extended_look_07446",
         "CRITICS: 99", None),
        ("But on November 21st, its PlayStation 5 user score was just five point six.", "CLIP:extended_look_10037",
         "PLAYERS: 5.6", "surprised"),
        ("GTABase counted almost thirty thousand negative ratings.", "CLIP:extended_look_15524",
         "~30,000 NEGATIVE", None),
        ("The complaints: thirty frames a second, bugs, a slow start, and no disc.", "CLIP:extended_look_09166",
         None, None),
        ("Then it got weird. The other game with a ninety-nine is Zelda: Ocarina of Time.",
         "CLIP:extended_look_07351", None, None),
        ("Its user score fell from nine point six to eight point seven in under a day.", "CLIP:extended_look_11437",
         "ZELDA: 9.6 TO 8.7", None),
        ("Push Square says it looks like GTA 6 fans hitting back.", "CLIP:extended_look_12606", None, None),
        ("Critics or players: who got GTA 6 right? Pick a side. Follow for more GTA 6 facts.",
         "CLIP:extended_look_05748", None, None),
    ],
    facts=[
        {"claim": "GTABase (21 Nov 2026): PS5 user score 5.6/10 vs critic score 99 (152 critics); 'Almost 30,000 user "
                  "ratings are negative, 44% of the total'; complaints include 30 FPS, bugs, slow pace at the start, "
                  "no physical copy; Ocarina of Time (N64) also has a 99.",
         "sources": ["https://www.gtabase.com/gta-6/articles/gta-6-review-bombed-on-metacritic"], "main": True},
        {"claim": "Notebookcheck (21 Nov 2026): GTA 6 user score 'currently 5.6/10'; its 99 Metascore ties the N64 "
                  "Zelda for best of all time; Ocarina of Time's user rating fell 'from 9.6 to 8.7' in less than 24 "
                  "hours.",
         "sources": ["https://www.notebookcheck.net/Zelda-Ocarina-of-Time-Metacritic-user-rating-sinks-in-response-to-GTA-6-review-bombing.1456403.0.html"],
         "main": True},
        {"claim": "Push Square (21 Nov 2026): fans of the Rockstar release 'appear to have launched a counter-attack' on "
                  "Ocarina of Time; CBR (21 Nov 2026): complaints about bugs, 30 fps and no physical disc.",
         "sources": ["https://www.pushsquare.com/news/2026/11/gta-6-ps5-review-bombing-out-of-control-as-zelda-receives-revenge-ratings",
                     "https://www.cbr.com/grand-theft-auto-6-metacritic-user-rating-review-scores/"],
         "main": True},
    ],
    description="Critics gave GTA 6 a 99 on Metacritic; players gave it 5.6 (PS5, 21 Nov). Then Zelda: Ocarina of "
                "Time's user score dropped.\nSources: GTABase, Notebookcheck, Push Square, CBR.",
    hashtags=["#GTA6", "#Metacritic", "#Zelda"],
)

S["gta6-egg-tower"] = dict(
    title="GTA 6 hid a real Easter egg at the top of a tower",
    thumb_text="AT THE VERY TOP",
    hook_card="AT THE TOP?",
    cover_lines=["HIDDEN EASTER EGG", "AT THE VERY TOP", "HOW TO FIND IT"],
    cover_frame={"shot": "extended_look_10132", "f": 0.5, "x": 0.4},   # Lucia in the 'Baddie' crop top (R3: face)
    experiment="E1-long",
    beats=[
        ("Climb what may be the highest point in GTA 6, and you find a real Easter egg.",
         "CLIP:extended_look_07899", None, "curious"),
        ("It's a radio tower in South Vice-Dale County, and the climb is long.", "CLIP:extended_look_11275",
         "SOUTH VICE-DALE", None),
        ("At the top, there's a nest of brightly colored eggs.", "CLIP:extended_look_15698", "A NEST OF EGGS",
         "amused"),
        ("Throw one off the tower, and it triggers a special cutscene.", "CLIP:extended_look_07446", None, None),
        ("The egg lands on someone's windshield.", "CLIP:extended_look_04835", None, "laughs softly"),
        ("But there's something stranger in the sky.", "CLIP:trailer_1_00398", None, None),
        ("In Port Gellhorn, after 2 a.m., a bright light can appear above you.", "CLIP:trailer_2_01188",
         "PORT GELLHORN, 2 AM", None),
        ("Run toward it, and you might see a woman being abducted by aliens.", "CLIP:trailer_2_00996", None,
         "surprised"),
        ("Play as Jason, and it becomes a rescue mission at an abandoned research facility.",
         "CLIP:extended_look_02513", None, None),
        ("The door code is found at a military airfield.", "CLIP:launch_trailer_00390",
         "CODE: 2-3-4-1", None),
        ("Inside, you can find a living alien and carry it out.", "CLIP:extended_look_00000", None, None),
        ("Even the achievement is a joke: The Truth Is Out There.", "CLIP:trailer_1_00300", "TRUTH IS OUT THERE",
         None),
        ("Egg tower or alien rescue: which one are you trying first? Pick a side. Follow for more GTA 6 secrets.",
         "CLIP:extended_look_05748", None, None),
    ],
    facts=[
        {"claim": "ComicBook (20 Nov 2026): a radio tower in South Vice-Dale County, arguably the highest point in the "
                  "game, long climb; 'players are rewarded with a literal nest of eggs at the top'; throwing one off "
                  "'will actually trigger a special cutscene' (the egg hits someone's windshield). Alien abduction: "
                  "Port Gellhorn, outside at 2am or later, a bright light in the sky; running toward it you may see a "
                  "woman being abducted by aliens; as Jason, a rescue quest at an abandoned research facility in "
                  "Pelican Valley, entry code 2-3-4-1 found at a military airfield; a living alien Jason can carry "
                  "out; achievement 'The Truth is Out There'.",
         "sources": ["https://comicbook.com/gaming/list/5-most-exciting-gta-6-easter-eggs-players-have-found-after-launch-day/"],
         "main": True},
    ],
    description="A literal Easter egg nest on top of a radio tower in South Vice-Dale County, and an alien abduction "
                "in Port Gellhorn after 2 a.m.\nSource: ComicBook.",
    hashtags=["#GTA6", "#GTA6Secrets", "#EasterEgg"],
)


# ---- RESERVE scripts (20 Nov 2026, owner away): evergreen, no time words; used only if a slot is empty ----
S["gta6-trailer-songs"] = dict(
    title="GTA 6's trailers brought two old songs back to life",
    thumb_text="TWO OLD SONGS",
    hook_card="TWO OLD SONGS",
    cover_lines=["TWO 80s SONGS", "EXPLODED ON SPOTIFY", "THANKS TO THE TRAILERS"],
    cover_frame={"shot": "trailer_1_00065", "f": 0.5, "x": 0.2},   # Lucia in prison (R3: face)
    beats=[
        ("GTA 6 didn't just break view records. It brought two old songs back from the dead.",
         "CLIP:trailer_2_00920", None, "excited"),
        ("The first trailer used Tom Petty's Love Is a Long Road, a song from 1989.", "CLIP:trailer_1_00300",
         "TOM PETTY, 1989", None),
        ("After that trailer dropped, Spotify streams of the song jumped by about thirty-seven thousand percent.",
         "CLIP:trailer_1_00325", "+37,000%", "surprised"),
        ("And here's a nice detail: Tom Petty was born in Gainesville, Florida.", "CLIP:trailer_1_00356",
         "BORN IN FLORIDA", None),
        ("That's the state GTA 6's Leonida is based on.", "CLIP:extended_look_11275", None, None),
        ("Then the second trailer did it again, only bigger.", "CLIP:trailer_2_00346", None, "short pause"),
        ("It used Hot Together by The Pointer Sisters, a song from 1986.", "CLIP:extended_look_10196",
         "POINTER SISTERS, 1986", None),
        ("In the two hours after that trailer came out, its Spotify streams surged by one hundred and eighty-two "
         "thousand percent.", "CLIP:trailer_1_00341", "+182,000%", "excited"),
        ("That's almost five times Tom Petty's jump.", "CLIP:extended_look_08740", None, None),
        ("Two songs from the eighties, suddenly everywhere again, because of one game.", "CLIP:trailer_2_00831",
         None, None),
        ("Which song would you put on GTA 6's radio?", "CLIP:launch_trailer_00026", None, None),
    ],
    facts=[
        {"claim": "GTA 6 trailer 1 (Dec 2023) used Tom Petty's 'Love Is A Long Road' (1989, Full Moon Fever); "
                  "Spotify streams rose by 36,979% compared with the week before (IGN citing Spotify, via GameSpot); "
                  "Tom Petty was born in Gainesville, Florida, in 1950; GTA 6's Leonida is based on Florida.",
         "sources": ["https://www.gamespot.com/articles/gta-6-trailer-helps-tom-petty-song-surge-37000-on-spotify/1100-6519729/",
                     "https://tompetty.com/blogs/news/tom-petty-s-love-is-a-long-road-from-full-moon-fever-featured-in-trailer-1-of-grand-theft-auto-vi"],
         "main": True},
        {"claim": "GTA 6 trailer 2 used the 1986 song 'Hot Together' by The Pointer Sisters; its Spotify streams "
                  "'surged by 182,000% in the two hours after the trailer's release'; the Tom Petty song saw 'a "
                  "similar (though somewhat more modest) 37,000% increase'. 182,000 / 37,000 = 4.9.",
         "sources": ["https://www.techradar.com/gaming/spotify-streams-of-the-latest-grand-theft-auto-6-trailer-song-increased-by-182-000-percent-just-two-hours-after-the-trailer-dropped"],
         "main": True},
    ],
    description="Tom Petty's 'Love Is a Long Road' (+37,000% on Spotify) and The Pointer Sisters' 'Hot Together' "
                "(+182,000% in two hours): how GTA 6's trailers revived two 80s songs.\n"
                "Sources: GameSpot/IGN, TechRadar, tompetty.com.",
    hashtags=["#GTA6", "#TomPetty", "#PointerSisters"],
)

S["gta6-vice-city-1986"] = dict(
    title="GTA 6 isn't our first trip to Vice City",
    thumb_text="BACK TO VICE CITY",
    hook_card="1986 VS NOW",
    cover_lines=["VICE CITY IN 1986", "VS GTA 6'S VICE CITY", "WHAT CHANGED?"],
    cover_frame={"shot": "extended_look_07899", "f": 0.5, "x": 0.5},   # Lucia in a car (R3: face)
    beats=[
        ("GTA 6 isn't the first time Rockstar has taken us to Vice City.", "CLIP:extended_look_10132", None,
         "curious"),
        ("The first trip was GTA Vice City, which came out in October 2002 on the PlayStation 2.",
         "CLIP:trailer_1_00300", "OCT 2002, PS2", None),
        ("It was set in 1986, in a city based heavily on Miami.", "CLIP:trailer_1_00325", "SET IN 1986", None),
        ("You played as gangster Tommy Vercetti, voiced by the actor Ray Liotta.", "CLIP:extended_look_08740",
         "TOMMY VERCETTI", None),
        ("It was a huge hit, with over seventeen and a half million copies sold.", "CLIP:trailer_1_00341",
         "17.5M COPIES", "surprised"),
        ("It was one of the PlayStation 2's best-selling games.", "CLIP:trailer_2_00346", None, None),
        ("Now GTA 6 brings Vice City back, inside a state called Leonida, inspired by Florida.",
         "CLIP:extended_look_11275", "LEONIDA", None),
        ("And instead of one gangster, there are two leads: Jason Duval and Lucia Caminos.", "CLIP:trailer_2_00920",
         "JASON + LUCIA", "excited"),
        ("Same city name, more than twenty years later, and a whole new story.", "CLIP:trailer_2_00831", None, None),
        ("Did you ever play the original Vice City?", "CLIP:launch_trailer_00026", None, None),
    ],
    facts=[
        {"claim": "GTA Vice City 'was released in October 2002 for the PlayStation 2'; 'set in 1986 in fictional "
                  "Vice City, which is based heavily on the city of Miami, Florida'; protagonist 'gangster Tommy "
                  "Vercetti (voiced by Ray Liotta)'; 'has sold over 17.5 million copies overall'; 'one of the "
                  "PlayStation 2's best-selling games with 14.2 million copies sold'.",
         "sources": ["https://en.wikipedia.org/wiki/Grand_Theft_Auto:_Vice_City"], "main": True},
        {"claim": "'GTA 6 takes place in the state of Leonida, a fictional location inspired by Florida'; 'our two "
                  "protagonists, Jason Duval and Lucia Caminos'; Rockstar's site: 'Vice City, USA.' and 'Home to the "
                  "neon-soaked streets of Vice City and beyond'.",
         "sources": ["https://www.destructoid.com/?p=436313",
                     "https://www.rockstargames.com/VI/only-in-leonida/vice-city"], "main": True},
    ],
    description="GTA Vice City (PS2, October 2002) was set in 1986 with Tommy Vercetti, voiced by Ray Liotta, and "
                "sold over 17.5 million copies. GTA 6 brings Vice City back with Jason and Lucia.\n"
                "Sources: Wikipedia, Destructoid, Rockstar Games.",
    hashtags=["#GTA6", "#GTAViceCity", "#GrandTheftAuto"],
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
            "experiment": v.get("experiment"),     # docs/GTA_LEARNINGS.md experiment id, e.g. "E1-short"
            # cover + opening card words, written here (no paid cover call); the picture is the first beat's shot
            "cover": {"image": "img1", "lines": v.get("cover_lines") or [v["hook_card"]], "why": "written in session",
                      **({"frame": v["cover_frame"]} if v.get("cover_frame") else {})}}


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
            # 19 Nov 2026: "QUOTE: <name>" over a character reads as if that character were the real person. Long
            # shot ranges (> 8 s) often hide other scenes with people, so they are not safe either.
            import re as _re
            who = (sc["callout"] or "").upper().partition("QUOTE:")[2].split(",")[0].strip()
            if who and who not in ("ROCKSTAR", "ROCKSTAR GAMES", "TAKE-TWO") and (
                    have > 8 or _re.search(r"\b(man|woman|men|women|couple|person|jason|lucia|girl|guy)\b",
                                           shots[sid].get("shows", ""), _re.I)):
                errs.append(f"{topic} {sc['id']}: quote label over people or a long mixed shot ({sid})")
    return errs


def _recent_plan(days: int) -> list:
    """PLAN rows from (today - 1) to today + days, plus reserves: the scripts whose covers are checked strictly."""
    import datetime as dt
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import gta_queue as q
    except Exception:  # noqa: BLE001
        return []
    lo = max(dt.date.today().isoformat(), "2026-11-21")       # the rule starts with the 21 Nov videos
    hi = (dt.date.today() + dt.timedelta(days=days)).isoformat()
    return [r for r in q.PLAN if lo <= r[0] <= hi] + [(None, None, t) for t in getattr(q, "RESERVE", [])]


if __name__ == "__main__":
    out, errs = {}, []
    for t, v in S.items():
        out[t] = build(t, v)
        errs += check(t, out[t])
        print(t, sum(len(sc["narration"].split()) for sc in out[t]["scenes"]), "words,",
              len(out[t]["scenes"]), "beats,", len(set(out[t]["images"].values())), "shots")
    # 21 Nov 2026 (owner): cover words must say what the video is about -> 3 lines, 6-12 words, each <= 22 characters,
    # never starting with "GTA 6" (the real logo is above them). And no cover picture repeated from a recent video.
    new = {t for t in out if t in {x[2] for x in _recent_plan(4)}}
    import datetime as _dt
    _ist = (_dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)).date().isoformat()
    todo = {x[2] for x in _recent_plan(4) if x[0] is None or x[0] > _ist}     # not made yet (tomorrow on + reserves)
    seen = {}
    for t in list(out)[::-1]:
        c = out[t].get("cover") or {}
        lines = c.get("lines") or []
        if t in new:
            words = sum(len(x.split()) for x in lines)
            if len(lines) != 3 or not 6 <= words <= 12 or any(len(x) > 22 for x in lines):
                errs.append(f"{t}: cover_lines must be 3 lines, 6-12 words, each <= 22 characters ({lines})")
            # 21 Nov 2026: a 24-character callout ("32.5M COPIES PRE-RELEASE") ran under the corner logo and lost
            # its first digit; 23 characters fit ("AVATAR: $2.92B ALL-TIME").
            for sc in out[t]["scenes"] if t in todo else []:
                if len(sc["callout"] or "") > 23:
                    errs.append(f"{t} {sc['id']}: callout over 23 characters runs under the logo ({sc['callout']})")
            if any(x.upper().startswith(("GTA 6", "GTA VI")) for x in lines):
                errs.append(f"{t}: a cover line starts with 'GTA 6' (the logo already says it)")
        fr = c.get("frame") or {}
        if fr.get("shot"):
            key = ("CLIP:" + fr["shot"], round(float(fr.get("f", 0.5)), 1))
        else:
            img = fr.get("image") or c.get("image") or "img1"
            key = (out[t]["images"].get(img, ""), round(float(fr.get("t", -1)), 1))
        # 21 Nov analysis (R3 in docs/GTA_LEARNINGS.md): a clear Lucia/Jason face on the cover wins, faceless ones flop
        faces = {f["shot"] for f in json.loads((ROOT / "assets/official/attention_shots.json").read_text()).get("faces", [])}
        if t in new and fr.get("shot") and fr["shot"] not in faces:
            print(f"  warning {t}: cover shot {fr['shot']} is not in the 'faces' list (rule R3: use a Lucia/Jason face)")
        if t in new and key in seen and seen[key] != t:
            print(f"  warning {t}: cover picture {key[0]} (t={key[1]}) also used by {seen[key]}; set cover_frame")
        seen.setdefault(key, t)
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    (ROOT / "config/gta_scripts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote config/gta_scripts.json")
