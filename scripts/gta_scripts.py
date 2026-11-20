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
    cover_frame={"shot": "trailer_2_01400", "f": 0.5, "x": 0.68},   # jet-ski jump
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
        ("A 2025 boxing night called La Velada, with 9.68 million.", "CLIP:extended_look_05648", "LA VELADA: 9.68M",
         None),
        ("So no game launch has ever pulled a crowd like this one, by Streams Charts' count.",
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
    cover_frame={"shot": "extended_look_08201", "f": 0.5, "x": 0.3},   # masked man
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
        ("The creepy part is on the roof.", "CLIP:trailer_2_00114", None, "serious"),
        ("Players found a knife, tape, rope and a syringe up there.", "CLIP:extended_look_07018", None, None),
        ("Let's not ask what that's for.", "CLIP:launch_trailer_00423", None, "laughs softly"),
        ("Down at the docks, there's a boat you can steal.", "CLIP:launch_trailer_00026", None, None),
        ("Fans say it looks just like Slice of Life, Dexter's boat.", "CLIP:extended_look_15728", "SLICE OF LIFE?",
         None),
        ("Has Rockstar confirmed it? No. It hasn't said this is Dexter's home.", "CLIP:extended_look_12920", None,
         None),
        ("But fans had spotted this building back in August, months before launch.", "CLIP:extended_look_09766",
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
    cover_frame={"shot": "extended_look_09432", "f": 0.5, "x": 0.55},   # police chase
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
        ("So it costs twenty dollars more than GTA 5, but gives you about twenty more hours of story.",
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
    cover_frame={"shot": "trailer_1_00686", "f": 0.5, "x": 0.28},   # masked Lucia, robbery
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
        ("So until Take-Two shares real numbers, it's only an estimate. A very big one.", "CLIP:extended_look_09166",
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
    cover_frame={"shot": "trailer_1_00065", "f": 0.5, "x": 0.42},   # Lucia in prison
    beats=[
        ("Fans think GTA 6 was hiding in plain sight, years before its first trailer.", "CLIP:extended_look_03021",
         None, "curious"),
        ("In 2021, Rockstar released a remaster of GTA San Andreas.", "CLIP:trailer_1_00026",
         "SAN ANDREAS REMASTER, 2021", None),
        ("It had a picture of a house that only appeared in that version.", "CLIP:trailer_2_00188", None, None),
        ("Some fans wondered if it came from GTA 6's development.", "CLIP:extended_look_12920", None, None),
        ("Now the game is out, and fans mapping Leonida found that same house, in Belville.",
         "CLIP:extended_look_11275", "BELVILLE", None),
        ("VGC says the two images line up down to the smallest details.", "CLIP:extended_look_10262", None,
         "surprised"),
        ("Even the plants and trees outside are in the same places.", "CLIP:extended_look_04786", None, None),
        ("So that 2021 picture may have been our first look at GTA 6.", "CLIP:trailer_2_00232", None, None),
        ("The first official trailer only came in December 2023.", "CLIP:trailer_1_00300", "TRAILER 1: DEC 2023",
         None),
        ("To be clear, it's a fan theory. Rockstar hasn't confirmed it.", "CLIP:trailer_2_00346", None, "serious"),
        ("But if fans are right, GTA 6 was first seen in 2021, and almost nobody noticed.",
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


# ---- RESERVE scripts (20 Nov 2026, owner away): evergreen, no time words; used only if a slot is empty ----
S["gta6-trailer-songs"] = dict(
    title="GTA 6's trailers brought two old songs back to life",
    thumb_text="TWO OLD SONGS",
    hook_card="TWO OLD SONGS",
    cover_lines=["TWO 80s SONGS", "EXPLODED ON SPOTIFY", "THANKS TO THE TRAILERS"],
    cover_frame={"shot": "trailer_1_00248", "f": 0.5, "x": 0.35},   # dancing on a car roof
    beats=[
        ("GTA 6 didn't just break view records. It brought two old songs back from the dead.",
         "CLIP:trailer_2_00920", None, "excited"),
        ("The first trailer used Tom Petty's Love Is a Long Road, a song from 1989.", "CLIP:trailer_1_00300",
         "TRAILER 1: TOM PETTY, 1989", None),
        ("After that trailer dropped, Spotify streams of the song jumped by about thirty-seven thousand percent.",
         "CLIP:trailer_1_00325", "+37,000%", "surprised"),
        ("And here's a nice detail: Tom Petty was born in Gainesville, Florida.", "CLIP:trailer_1_00356",
         "BORN IN FLORIDA", None),
        ("That's the state GTA 6's Leonida is based on.", "CLIP:extended_look_11275", None, None),
        ("Then the second trailer did it again, only bigger.", "CLIP:trailer_2_00346", None, "short pause"),
        ("It used Hot Together by The Pointer Sisters, a song from 1986.", "CLIP:extended_look_10196",
         "TRAILER 2: POINTER SISTERS, 1986", None),
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
    cover_frame={"shot": "trailer_1_00217", "f": 0.5, "x": 0.2},   # Vice City beach
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
    seen = {}
    for t in list(out)[::-1]:
        c = out[t].get("cover") or {}
        lines = c.get("lines") or []
        if t in new:
            words = sum(len(x.split()) for x in lines)
            if len(lines) != 3 or not 6 <= words <= 12 or any(len(x) > 22 for x in lines):
                errs.append(f"{t}: cover_lines must be 3 lines, 6-12 words, each <= 22 characters ({lines})")
            if any(x.upper().startswith(("GTA 6", "GTA VI")) for x in lines):
                errs.append(f"{t}: a cover line starts with 'GTA 6' (the logo already says it)")
        fr = c.get("frame") or {}
        if fr.get("shot"):
            key = ("CLIP:" + fr["shot"], round(float(fr.get("f", 0.5)), 1))
        else:
            img = fr.get("image") or c.get("image") or "img1"
            key = (out[t]["images"].get(img, ""), round(float(fr.get("t", -1)), 1))
        if t in new and key in seen and seen[key] != t:
            print(f"  warning {t}: cover picture {key[0]} (t={key[1]}) also used by {seen[key]}; set cover_frame")
        seen.setdefault(key, t)
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    (ROOT / "config/gta_scripts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote config/gta_scripts.json")
