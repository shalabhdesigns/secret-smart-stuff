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
        ("You can walk right up to the door, but you can't go inside.", "CLIP:extended_look_12841", None, None),   # 23 Nov: 00000 opens on the rating card (published video unchanged)
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
        ("Is dating Lucia in GTA 6 cheating on your real partner? Real couples can't agree.",
         "CLIP:trailer_1_00728", None, "amused"),
        ("In the game, you can look after Jason and Lucia's relationship.",
         "CLIP:extended_look_03869", None, None),
        ("Buy her flowers, pick up groceries, fix up the house, and a little heart pops up.",
         "CLIP:extended_look_04180", None, None),
        ("You can hold her hand.", "CLIP:trailer_2_00976", None, None),
        ("And Vice says even a robbery together counts as quality time.", "CLIP:trailer_1_00686", None,
         None),
        ("Ignore her goodnight text, and it can hurt the relationship a little.", "CLIP:extended_look_03894", None,
         None),
        ("On TikTok, X and Reddit, the arguments are getting heated.",
         "CLIP:extended_look_06535", None, None),
        ("One Reddit user wrote, \"Don't treat AI better than your actual girl.\"", "CLIP:extended_look_10037", None,
         None),
        ("Others say if a game ends your relationship, it was ending anyway.",
         "CLIP:extended_look_06595", None, None),
        ("Some couples are even signing ten-day contracts, so nobody interrupts a mission until November 29th.",
         "CLIP:extended_look_10919", "10-DAY 'GTA CONTRACTS'", None),
        ("And here's the twist: in the game, you can't cheat on Lucia. There's no one else to date.",
         "CLIP:extended_look_07899", None, "surprised"),
        ("And you can't break up with her.", "CLIP:extended_look_03021", None, None),
        ("Is dating Lucia cheating: yes or no? Pick a side. Follow for more GTA 6 facts.",
         "CLIP:extended_look_05748", None, None),
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
        ("Going for one hundred percent completion? You need this station.", "CLIP:extended_look_11275", None, None),
        ("Kodak Black's hidden station or the normal radio: which side are you on? Follow for more GTA 6 secrets.",
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
         "CLIP:extended_look_15524", None, None),
        ("First, players have spotted Bigfoot in the game. And UFOs too.", "CLIP:trailer_1_00183", "BIGFOOT + UFOs", "surprised"),
        ("There's even a giant crab monster.", "CLIP:extended_look_10360", None, None),
        ("Get stranded at sea, and a dog riding a jet ski can show up to save you.", "CLIP:extended_look_10450",
         None, None),
        ("It takes you to an island of dogs, with hidden treasure worth over twelve hundred dollars.",
         "CLIP:extended_look_15728", "$1,200+ TREASURE", None),
        ("Parade says it's likely based on Loosy, a real Florida dog whose jet ski ride went viral.",
         "CLIP:launch_trailer_00026", "LOOSY, FORT LAUDERDALE", None),
        ("Rockstar hasn't confirmed that.", "CLIP:trailer_1_00398", None, None),
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
    description="Bigfoot, UFOs, a giant crab monster, a jet-ski rescue dog and a scooter theft: the strangest "
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
        ("GTA 6 players have a new goal: make Jason as fat as possible.", "CLIP:extended_look_03021", None,
         "amused"),
        ("San Andreas' old weight system is back.", "CLIP:trailer_2_00383", None, None),
        ("Eat too much, and Jason or Lucia gains weight. Work out, and they build muscle.",
         "CLIP:extended_look_10387", None, None),
        ("One fan posted a max weight, low muscle Jason and called him True Fat Jason.", "CLIP:trailer_2_00232",
         "'TRUE FAT JASON'", None),
        ("The trick GamesRadar shared: eat at least four burgers or tacos, sleep, and skip the gym.",
         "CLIP:extended_look_07238", "4+ BURGERS, NO GYM", None),
        ("But here's the twist: True Fat Jason isn't very fat at all.", "CLIP:extended_look_03869", None,
         "surprised"),
        ("GamesRadar compared him and max weight Lucia to Red Dead 2's Arthur Morgan at his heaviest.",
         "CLIP:extended_look_10196", None, None),
        ("Neither seems quite as big.", "CLIP:extended_look_03021", None, None),
        ("Gym Jason or True Fat Jason: which one are you building? Follow for more GTA 6 secrets.",
         "CLIP:extended_look_05748", None, None),
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
    cover_frame={"shot": "trailer_1_00065", "f": 0.5, "x": 0.33},   # Lucia in prison orange at a window (R3: face; 23 Nov: trailer_2_00961 showed her back)
    experiment="E1-long",
    beats=[
        ("The woman who plays Lucia in GTA 6 was already in GTA 5. You just never noticed.",
         "CLIP:extended_look_10196", None, "curious"),
        ("Her name is Manni Perez. She's nominated at the Game Awards for Best Performance, for playing Lucia.",
         "CLIP:extended_look_10132", "LUCIA: MANNI L. PEREZ", None),
        ("LADbible checked her IMDb, and her very first credit is GTA 5.", "OFFICIAL:v_c670974867",
         "FIRST CREDIT: GTA 5", None),
        ("She voiced a character called Clubber number two.", "CLIP:extended_look_10510", "'CLUBBER 2'", "amused"),
        ("Then, in a 2019 GTA Online update, she was a blackjack dealer with no name.", "OFFICIAL:v_24ba6644de",
         "UNNAMED DEALER, 2019", None),
        ("On TV, she's been in Jessica Jones, The Blacklist and Law and Order.", "CLIP:trailer_1_00084", None, None),
        ("And she trains in Muay Thai, Brazilian jiu-jitsu and MMA.", "CLIP:extended_look_10387", None, None),
        ("Back in 2018, she said her biggest fear was playing a woman who needs to be saved by a man.",
         "CLIP:extended_look_08816", None, None),
        ("And Jason? Dylan Rourke revealed on Instagram that he plays him.", "CLIP:trailer_2_00232",
         "JASON: DYLAN ROURKE", "excited"),
        ("It's his first video game. Before this, he was on Station 19 and Modern Family.",
         "CLIP:extended_look_03021", None, None),
        ("His message to fans ended with: See y'all in Leonida.", "CLIP:extended_look_07446", None, None),
        ("Lucia or Jason: whose story are you here for? Pick a side. Follow for more GTA 6 secrets.",
         "CLIP:extended_look_10919", None, None),
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
        ("Rockstar still hasn't said how big the map is in square miles.", "CLIP:trailer_1_00300", None, None),
        ("But Forbes reports Rockstar puts it at around twice the size of GTA 5's map.", "OFFICIAL:v_3360902d78",
         "ABOUT 2x GTA 5", None),
        ("Then a YouTuber who says Rockstar told him this puts it at three times Red Dead Redemption 2.",
         "CLIP:trailer_1_00183", "3x RDR2 (REPORTED)", None),
        ("There are six regions, from Vice City to the swamps.", "CLIP:extended_look_10298", "6 REGIONS",
         None),
        ("Game Informer reports more than a hundred and seventy animal species.", "CLIP:extended_look_04645",
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
    cover_frame={"shot": "extended_look_03869", "f": 0.5, "x": 0.32},   # Jason in a tank top with Lucia (R3: face)
    experiment="E1-long",
    beats=[
        ("You can't play GTA 6 with your friends. Not online, and not on the same couch.",
         "CLIP:extended_look_03021", None, "serious"),
        ("The store pages say it plainly: Grand Theft Auto Six is a single-player experience.",
         "CLIP:extended_look_09166", "SINGLE-PLAYER ONLY", None),
        ("But GTA 5 didn't have online on day one either. It came out on September 17th, 2013.",
         "OFFICIAL:v_c670974867", None, None),
        ("GTA Online followed two weeks later, on October 1st, 2013.", "OFFICIAL:v_bd8dd92adc", "+2 WEEKS", None),
        ("So where is GTA 6's online mode? So far, Rockstar and Take-Two haven't announced one, or a date.",
         "CLIP:extended_look_12920", "NO DATE YET", "curious"),
        ("One hint came from Twitch's boss, Dan Clancy, in September.", "CLIP:trailer_1_00300", "TWITCH CEO DAN CLANCY",
         None),
        ("He told Bloomberg: \"You are going to see this big bump with GTA 6, but then an even bigger one next year "
         "when they launch multiplayer.\"", "CLIP:launch_trailer_00026", "'NEXT YEAR'", None),
        ("Bloomberg's Jason Schreier has also reported that the online part is expected in 2027.",
         "CLIP:extended_look_07446", "EXPECTED: 2027", None),
        ("Rockstar hasn't confirmed that.", "CLIP:trailer_1_00398", None, None),
        ("Story first, or online first: which one do you care about more? Pick a side. Follow for more GTA 6 "
         "facts.", "CLIP:extended_look_09766", None, None),
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
    cover_frame={"shot": "trailer_2_00631", "f": 0.5, "x": 0.43},   # Lucia in the prison yard (R3: face)
    experiment="E1-short",
    beats=[
        ("GTA 6's score fight has dragged in a Nintendo 64 classic: Zelda.", "CLIP:trailer_1_00728", None, "amused"),
        ("On Metacritic, critics gave it ninety-nine. That ties the best score of all time.", "CLIP:extended_look_07446",
         "CRITICS: 99", None),
        ("But on November 21st, its PlayStation 5 user score was just five point six.", "CLIP:extended_look_10037",
         "PLAYERS: 5.6", "surprised"),
        ("GTABase counted almost thirty thousand negative ratings.", "CLIP:extended_look_15524",
         "~30,000 NEGATIVE", None),
        ("Players complained about thirty frames a second, bugs, a slow start, and no physical disc.", "CLIP:extended_look_09166",
         None, None),
        ("Then it got weird. Zelda: Ocarina of Time also has a ninety-nine.",
         "CLIP:extended_look_07351", None, None),
        ("Its user score fell from nine point six to eight point seven in under a day.", "CLIP:extended_look_11437",
         "ZELDA: 9.6 TO 8.7", None),
        ("Push Square says that drop looks like GTA 6 fans hitting back.", "CLIP:extended_look_12606", None, None),
        ("Critics or players: who got GTA 6 right? Pick a side. Follow for more GTA 6 facts.",
         "CLIP:extended_look_12735", None, None),
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
        ("It's a radio tower in South Vice-Dale County, and the climb is long.", "CLIP:trailer_1_00026",
         "SOUTH VICE-DALE", None),
        ("At the top, there's a literal nest of eggs.", "CLIP:extended_look_15698", "A NEST OF EGGS",
         "amused"),
        ("Throw one off the tower, and it triggers a special cutscene.", "CLIP:extended_look_07446", None, None),
        ("The egg lands on someone's windshield.", "CLIP:extended_look_04835", None, "laughs softly"),
        ("But there's something stranger in the sky.", "CLIP:trailer_2_00831", None, None),
        ("In Port Gellhorn, after 2 a.m., a bright light can appear above you.", "CLIP:trailer_2_01188",
         "PORT GELLHORN, 2 AM", None),
        ("Run toward it, and you might see a woman being abducted by aliens.", "CLIP:trailer_2_00996", None,
         "surprised"),
        ("Play as Jason, and it becomes a rescue mission at an abandoned research facility.",
         "CLIP:extended_look_02513", None, None),
        ("The door code is found at a military airfield.", "CLIP:launch_trailer_00390",
         "CODE: 2-3-4-1", None),
        ("Inside the facility, you can find a living alien and carry it out.", "CLIP:launch_trailer_00423", None, None),
        ("You even get an achievement for it: The Truth Is Out There.", "CLIP:trailer_1_00300", "TRUTH IS OUT THERE",
         None),
        ("Egg tower or alien rescue: which one are you trying first? Pick a side. Follow for more GTA 6 secrets.",
         "CLIP:extended_look_12606", None, None),
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


S["gta6-xbox-60fps"] = dict(
    title="GTA 6's Xbox glitch breaks the 30 fps lock",
    thumb_text="BEAT THE 30 FPS LOCK",
    hook_card="30 FPS? NOT ON XBOX",
    cover_lines=["XBOX GLITCH BEATS", "THE 30 FPS LOCK?", "HERE'S THE CATCH"],
    cover_frame={"shot": "extended_look_09026", "f": 0.5, "x": 0.58},   # Lucia driving, looking back (R3: face)
    experiment="E1-short",
    beats=[
        ("GTA 6 is locked to thirty frames a second. But Xbox players found a way around it.",
         "CLIP:extended_look_07899", None, "curious"),
        ("A player on Reddit spotted it first.", "CLIP:extended_look_10037", None, None),
        ("It only works on Xbox, with Quick Resume, and a 120 hertz TV.", "CLIP:extended_look_11192",
         "XBOX + 120HZ TV ONLY", None),
        ("Set your Xbox to sixty hertz, then start the game.", "CLIP:extended_look_09166", "STEP 1: 60HZ", None),
        ("When the six stars appear in the intro, switch back to 120.", "CLIP:extended_look_09432",
         "STEP 2: BACK TO 120HZ", None),
        ("Then open another game without quitting, and switch back.", "CLIP:extended_look_10833",
         "STEP 3: SWAP GAMES", None),
        ("The catch? You'll rarely hit sixty. It's usually around forty.", "CLIP:extended_look_07501",
         "~40 FPS, RARELY 60", "amused"),
        ("And animations run twice as fast, because the physics are tied to the frame rate.",
         "CLIP:launch_trailer_00469", "2x SPEED", None),
        ("Rockstar could patch it later.", "CLIP:extended_look_12327", None, None),
        ("Faster but unstable, or a steady thirty: which side are you on?",
         "CLIP:extended_look_03021", None, None),
    ],
    facts=[
        {"claim": "RockstarINTEL (Aaron Trueman, 22 Nov 2026): the game is otherwise 'locked to a target of 30FPS on "
                  "all consoles'; 'this neat trick actually unlocks the frame rate of the game'; 'First spotted by "
                  "u/Meowwie64' on Reddit; 'this is only possible on XBOX due to its reliance on the excellent Quick "
                  "Resume feature'; 'You must also be using a display that supports 120Hz.' Steps: set the Xbox frame "
                  "rate to 60Hz in TV & Display settings; boot GTA VI; wait until you see the 6 Stars in the intro "
                  "sequence; change the display settings back to 120Hz; cold boot another game (not already in Quick "
                  "Resume) via the Xbox Guide without quitting GTA VI; switch back to GTA VI. Downsides: 'You'll "
                  "rarely hit 60FPS', typically around 40FPS, unstable; physics are tied to frame rate, so gameplay "
                  "animations run at twice the normal speed (cutscenes unaffected). 'It is possible Rockstar decides "
                  "to patch this in the future.'",
         "sources": ["https://rockstarintel.com/gta-vi-60fps-glitch-discovered-and-heres-how-to-do-it/"],
         "main": True},
        {"claim": "Digital Foundry (18 Nov 2026): every console version targets 30 fps; there is no 60 fps mode.",
         "sources": ["https://www.gtaboom.com/digital-foundry-finds-that-gta-6-indeed-runs-best-on-ps5-pro-b72f"],
         "main": False},
    ],
    description="An Xbox Quick Resume trick unlocks GTA 6's 30 fps cap: the steps, and the catch (about 40 fps, "
                "double-speed animations). Found by a Reddit user; Rockstar could patch it.\n"
                "Source: RockstarINTEL.",
    hashtags=["#GTA6", "#Xbox", "#GTA6Tips"],
)

S["gta6-jason-army"] = dict(
    title="GTA 6's Jason was in the Army. Rockstar explains",
    thumb_text="JASON WAS IN THE ARMY",
    hook_card="JASON, EX-ARMY?",
    cover_lines=["JASON WAS IN", "THE ARMY?", "ROCKSTAR EXPLAINS"],
    cover_frame={"shot": "trailer_2_00882", "f": 0.5, "x": 0.63},   # Jason in a black tee, Lucia beside (R3: face)
    experiment="E1-long",
    beats=[
        ("Jason from GTA 6 used to be in the Army. But GTA 6's story lead says that's not a statement.",
         "CLIP:extended_look_03021", None, "curious"),
        ("Here's how Rockstar describes him.", "CLIP:trailer_2_00081", None, None),
        ("Jason grew up around grifters and crooks.", "CLIP:launch_trailer_00119", None, None),
        ("Then he did a stint in the Army, trying to shake off his troubled teens.", "CLIP:trailer_2_00232",
         "A STINT IN THE ARMY", "serious"),
        ("Now he's back doing what he knows best: working for local drug runners.", "CLIP:extended_look_09994",
         None, None),
        ("Then he meets Lucia, who could be the best or worst thing to ever happen to him.",
         "CLIP:trailer_1_00728", None, None),
        ("So does the Army part mean something? Rupert Humphries, Rockstar's senior vice president of narrative, "
         "told Love magazine:", "CLIP:extended_look_07446", None, None),
        ("\"We didn't want to make any kind of statement with Jason's backstory.\"", "CLIP:extended_look_15698",
         "QUOTE: R. HUMPHRIES", None),
        ("He says Jason does what he does because of his material circumstances.", "CLIP:trailer_2_00188", None,
         None),
        ("But he says a lot is up to the player: does he need to do it, or is he wired differently from other people?",
         "CLIP:extended_look_10081", None, "curious"),
        ("Pushed by money, or wired that way: which side are you on?",
         "CLIP:extended_look_08816", None, None),
    ],
    facts=[
        {"claim": "GamesRadar+ (Catherine Lewis, 5 Oct 2026): Rockstar introduced Jason as someone who 'grew up "
                  "around grifters and crooks', spent 'a stint in the Army trying to shake off his troubled teens' "
                  "and is back 'doing what he knows best, working for local drug runners'; Lucia 'could be the best or "
                  "worst thing to ever happen to him'. Rupert Humphries, GTA 6's senior vice president of narrative "
                  "(the story lead), told Love magazine: 'We didn't want to make any kind of statement with Jason's "
                  "backstory.' He said Jason takes the measures he does 'because of his material circumstances', 'but "
                  "a lot of this is up to the player to decide whether he needs to do that or if it's a choice he "
                  "makes because he's wired differently from other people.'",
         "sources": ["https://gamesradar.com/games/grand-theft-auto/gta-6-story-lead-insists-rockstar-didnt-want-to-make-any-kind-of-statement-with-jasons-ex-military-background"],
         "main": True},
    ],
    description="Rockstar says Jason did a stint in the Army before going back to crime. GTA 6's story lead, Rupert "
                "Humphries, says it wasn't meant as a statement, and leaves his reasons up to you.\n"
                "Source: GamesRadar+ (Love magazine interview).",
    hashtags=["#GTA6", "#JasonDuval", "#GTA6Story"],
)

S["gta6-real-cheetah"] = dict(
    title="GTA 6's Cheetah supercar is real. It costs £1 million",
    thumb_text="£1 MILLION GTA CAR",
    hook_card="A REAL GTA 6 CAR?",
    cover_lines=["A REAL GTA CAR", "FOR £1 MILLION?", "WHERE TO BUY IT"],
    cover_frame={"shot": "extended_look_07899", "f": 0.5, "x": 0.62},   # Lucia in a parked car (R3: face)
    experiment="E1-short",
    beats=[
        ("The Cheetah from GTA 6 is real, and it costs one million pounds.", "CLIP:trailer_2_00232",
         None, "surprised"),
        ("Rockstar teamed up with West Coast Customs to build it.", "CLIP:extended_look_07018", None, None),
        ("Underneath, it's a Ferrari Testarossa.", "CLIP:trailer_1_00325",
         "A REAL TESTAROSSA", None),
        ("It's on show at Selfridges in London until November 28th.", "CLIP:extended_look_04786",
         "SELFRIDGES, LONDON", None),
        ("You can't just add it to a basket. You go through Selfridges' personal shoppers.",
         "CLIP:extended_look_11560", None, "amused"),
        ("In the game, the Cheetah comes with the ninety-nine dollar Ultimate Edition.", "CLIP:extended_look_07501",
         "IN-GAME: $99.99 EDITION", None),
        ("In 2013, Rockstar gave away a real GTA 5 car. It later sold for about forty-five thousand dollars.",
         "OFFICIAL:v_a9877dd12c", "GTA 5 CAR: ~$45,000", None),
        ("One fan joked: in the game you steal it, at Selfridges you need a mortgage.", "CLIP:extended_look_09432",
         None, "laughs softly"),
        ("Real Cheetah or game Cheetah: which do you want?",
         "CLIP:extended_look_04835", None, None),
    ],
    facts=[
        {"claim": "TweakTown (Nov 2026): 'Rockstar's real GTA 6 supercar costs $1.3 million, while the in-game one is "
                  "in a $99.99 edition'; 'a customized Ferrari Testarossa reworked to look like the Grotti Cheetah'; "
                  "'Rockstar Games collaborated with West Coast Customs'; 'available to purchase for £1 million via "
                  "Selfridges Personal Shopping'; 'there's no add to cart button here'; the Selfridges pop-up runs "
                  "'from November 9 to November 28'; 'The in-game '95 Cheetah is included in GTA 6's $99.99 Ultimate "
                  "Edition.'",
         "sources": ["https://www.tweaktown.com/news/114594/rockstars-real-gta-6-supercar-costs-1-3-million-while-the-in-game-one-is-in-a-99-99-edition/index.html"],
         "main": True},
        {"claim": "Top Gear (13 Nov 2026): 'This £1m GTA 6 'Grotti Cheetah' (Ferrari Testarossa) is up for sale at "
                  "Selfridges'; built for Rockstar by LA-based West Coast Customs; 'a very Vice City-coded "
                  "blue-and-pink paint job'; 'Back in 2013, the game's developer gave away a real-life version of the "
                  "'Bravado Banshee''.",
         "sources": ["https://www.topgear.com/car-news/gaming/ps1m-gta-6-grotti-cheetah-ferrari-testarossa-sale-selfridges"],
         "main": True},
        {"claim": "IBTimes UK (10 Nov 2026): the 2013 GTA 5 promotion gave away a real Bravado Banshee; the winner "
                  "'eventually sold the vehicle for about $45,000 (£33,469) on eBay'; one commenter joked: 'In the game "
                  "you steal it. At Selfridges you need a mortgage.'",
         "sources": ["https://www.ibtimes.co.uk/rockstar-gta-6-grotti-cheetah-million-pound-supercar-1831230"],
         "main": True},
    ],
    description="Rockstar and West Coast Customs turned a Ferrari Testarossa into GTA 6's Grotti Cheetah. It's at "
                "Selfridges London (to 28 Nov) for £1 million. In the game, it's in the $99.99 Ultimate Edition.\n"
                "Sources: TweakTown, Top Gear, IBTimes UK.",
    hashtags=["#GTA6", "#GrottiCheetah", "#Selfridges"],
)

S["gta6-chiliad-secret"] = dict(
    title="GTA 6 brought back GTA 5's Mount Chiliad mystery",
    thumb_text="CHILIAD IS BACK",
    hook_card="REMEMBER CHILIAD?",
    cover_lines=["GTA 5'S MOUNTAIN", "MYSTERY IS BACK?", "LISTEN AT THE BAR"],
    cover_frame={"shot": "trailer_2_00976", "f": 0.2, "x": 0.46},   # Jason close-up in a car (24 Nov: 03021 at f 0.8 was too dark; cover as published)
    experiment="E1-long",
    beats=[
        ("A secret in GTA 6 brings back a GTA 5 mystery from 2013.", "CLIP:extended_look_10196", None, "curious"),
        ("In an early mission, Donnie Carter calls Jason to meet him and Brian.", "CLIP:launch_trailer_00119",
         None, None),
        ("Then Donnie sends Jason to a bar nearby.", "CLIP:trailer_2_00895", None, None),
        ("And as you walk up, some random locals are talking about Mount Chiliad.", "CLIP:trailer_2_00416",
         None, "surprised"),
        ("That's the big mountain in GTA 5's Blaine County.", "OFFICIAL:v_3360902d78", "MOUNT CHILIAD (GTA 5)",
         None),
        ("Back in 2013, players found a strange mural at the top.", "OFFICIAL:v_fdac18d437", None, None),
        ("It seemed to show a UFO, a jetpack and an egg, with mysterious symbols.", "CLIP:launch_trailer_00685",
         "UFO + JETPACK + EGG", None),
        ("Players searched Los Santos and Blaine County for clues.", "CLIP:extended_look_02968", None, None),
        ("In 2017, GTA Online added a jetpack and a secret underground base.", "OFFICIAL:v_a457313ec2",
         "DOOMSDAY HEIST, 2017", None),
        ("But not everyone was convinced the mystery was solved.", "CLIP:extended_look_10037", None, None),
        ("Now one player says the locals in GTA 6 \"were talking about how there was a hidden bunker with jetpacks "
         "and eggs under Chiliad.\"", "CLIP:trailer_2_00996", None, None),
        ("A real clue, or just Rockstar teasing: which side are you on?",
         "CLIP:extended_look_03021", None, None),
    ],
    facts=[
        {"claim": "GAMINGbible (Richard Breslin, 20 Nov 2026): a hidden NPC conversation in an early GTA VI mission: "
                  "Donald 'Donnie' Carter calls Jason to meet him and Brian Heder, then sends Jason to a nearby bar; "
                  "approaching it, 'seemingly random NPCs' talk about 'the strange events surrounding Mount Chiliad in "
                  "Blaine County'. Found by Reddit user Tr1angleChoke; SprungVenus: 'Heard that too; they were talking "
                  "about how there was a hidden bunker with jetpacks and eggs under Chiliad.' GTA V released in "
                  "September 2013; at the top of Mount Chiliad players found 'a strange mural featuring what appeared "
                  "to be a UFO, a jetpack and an egg, along with several mysterious symbols'; players searched Los "
                  "Santos and Blaine County for clues; Rockstar added a jetpack and a secret underground facility in "
                  "GTA Online's Doomsday Heist update in 2017, but 'not everyone was convinced' the mystery was "
                  "solved; Rockstar may be 'simply teasing its fans'. The writer had not heard it first-hand.",
         "sources": ["https://www.gamingbible.com/news/gta-6-gta-5-mount-chiliad-mystery-easter-egg-802897-20261120",
                     "https://www.reddit.com/r/GTA6/comments/1y02b4y/crazy_npc_easter_egg_dialog_in_gta_6/"],
         "main": True},
    ],
    description="Players say random locals in an early GTA 6 mission talk about GTA 5's Mount Chiliad mystery: the "
                "2013 mural with a UFO, a jetpack and an egg.\nSource: GAMINGbible (Reddit finds).",
    hashtags=["#GTA6", "#MountChiliad", "#GTA5"],
)

S["gta6-outsold-consoles"] = dict(
    title="GTA 6 outsold three consoles before it even launched",
    thumb_text="OUTSOLD 3 CONSOLES",
    hook_card="BEAT 3 CONSOLES?",
    cover_lines=["OUTSOLD 3 CONSOLES", "BEFORE LAUNCH?", "HERE ARE THE NUMBERS"],
    cover_frame={"shot": "launch_trailer_00631", "f": 0.2, "x": 0.56},   # Lucia on a rooftop at sunset (24 Nov: 10081 at f 0.2 showed her back; cover as published)
    experiment="E1-long",
    beats=[
        ("Before launch, GTA 6 outsold three famous game consoles.", "CLIP:extended_look_10132", None,
         "surprised"),
        ("Take-Two says it sold thirty-two and a half million copies before release.", "CLIP:extended_look_07446",
         "32.5M BEFORE RELEASE", None),
        ("That beats the original Xbox, at twenty-four million.", "CLIP:extended_look_10618", "XBOX: 24M", None),
        ("It beats the GameCube, at about twenty-two million.", "CLIP:extended_look_11148", "GAMECUBE: 21.74M",
         None),
        ("And it beats Sega's Mega Drive, at almost thirty-one million.", "CLIP:extended_look_04835",
         "MEGA DRIVE: 30.75M", None),
        ("It came very close to the Nintendo 64, at thirty-two point nine million.", "CLIP:launch_trailer_00026",
         "N64: 32.93M", "amazed"),
        ("GAMINGbible says that makes it the thirtieth best-selling game of all time, from day one.",
         "CLIP:extended_look_12606", "#30 OF ALL TIME", None),
        ("Elden Ring took three years to sell that many.", "CLIP:trailer_1_00183", None, None),
        ("For comparison, GTA 5 sold about eleven million on its first day.", "OFFICIAL:v_c670974867",
         "GTA 5 DAY ONE: ~11M", None),
        ("GTA 5 went on to sell two hundred and thirty-five million. That's third of all time, behind Minecraft "
         "and Tetris.", "OFFICIAL:v_24ba6644de", "GTA 5: 235M", None),
        ("Will GTA 6 pass GTA 5's two hundred and thirty-five million? Yes or no: pick a side.",
         "CLIP:extended_look_07899", None, None),
    ],
    facts=[
        {"claim": "GAMINGbible (Olly Smith, 22 Nov 2026): 'As revealed by Take-Two Interactive, Rockstar's parent "
                  "company, Grand Theft Auto VI has sold 32.5 million units pre-release across PlayStation 5 and Xbox "
                  "Series X/S' (company estimates through the end of 19 November); this 'comes exceedingly close to "
                  "the lifetime sales of the Nintendo 64, which has shifted 32.93 million units since 1996'; more "
                  "than other consoles: Sega Mega Drive (30.75M), original Xbox (24M), Nintendo GameCube (21.74M); "
                  "'GTA VI has already become the 30th best-selling game of all time in its first day alone'; 'it "
                  "took Elden Ring three years to hit the same number of sales'; GTA V sold 'around 11 million copies "
                  "in the first day of release'; GTA V lifetime 235 million, third behind Minecraft (425M) and "
                  "Tetris (520M).",
         "sources": ["https://www.gamingbible.com/news/gta-6-day-one-copies-sold-270457-20261122"],
         "main": True},
    ],
    description="Take-Two: 32.5 million GTA 6 copies sold before release. That's more than the original Xbox, "
                "GameCube and Mega Drive sold in their lifetimes, and close to the N64.\nSources: GAMINGbible, "
                "Take-Two.",
    hashtags=["#GTA6", "#GTA6Sales", "#GTA5"],
)


# ---- RESERVE scripts (20 Nov 2026, owner away): evergreen, no time words; used only if a slot is empty ----
S["gta6-lucia-liberty"] = dict(
    title="GTA 6's Lucia isn't from Vice City. Here's where",
    thumb_text="LUCIA'S REAL HOME",
    hook_card="NOT FROM VICE CITY?",
    cover_lines=["LUCIA ISN'T FROM", "VICE CITY?", "HERE'S WHERE"],
    cover_frame={"shot": "extended_look_10196", "f": 0.5, "x": 0.45},   # Lucia close-up, purple wall (25 Nov: 08816 cover was too dark; f 0.3 = profile)
    experiment="E4-lucia",
    beats=[
        ("Lucia is the star of GTA 6, but she isn't from Vice City.", "CLIP:extended_look_10196", None, "curious"),
        ("She moved there from Liberty City. That's GTA's own version of New York.", "CLIP:extended_look_15698",
         "FROM LIBERTY CITY", None),
        ("Rockstar's bio says: \"Lucia's father taught her to fight as soon as she could walk.\"",
         "CLIP:extended_look_10387", "QUOTE: ROCKSTAR GAMES", None),
        ("And fighting for her family is what landed her in the Leonida Penitentiary.", "CLIP:trailer_2_00631",
         None, None),
        ("Rockstar says it was sheer luck that got her out.", "CLIP:trailer_2_00498", None, None),
        ("In the trailer, it's Jason who picks her up from jail.", "CLIP:trailer_1_00604", None, None),
        ("Her new rule? \"Only smart moves from here.\"", "CLIP:extended_look_10132", None, "amused"),
        ("So what is she after? Rockstar says: \"Lucia wants the good life her mom has dreamed of since their days "
         "in Liberty City.\"", "CLIP:extended_look_07446", "QUOTE: ROCKSTAR GAMES", None),
        ("And instead of just dreaming about it, Lucia is ready to take matters into her own hands.",
         "CLIP:extended_look_03021", None, None),
        ("So is Lucia doing this for her family, or for herself? Which side are you on?",
         "CLIP:trailer_1_00728", None, None),
    ],
    facts=[
        {"claim": "GamesRadar+ (Scott McCrae, 6 May 2025): Rockstar revealed that protagonist Lucia 'has moved to Vice "
                  "City from none other than Liberty City', GTA's New York. Rockstar's bio: 'More than anything, Lucia "
                  "wants the good life her mom has dreamed of since their days in Liberty City', and instead of "
                  "half-baked fantasies she is prepared to take matters into her own hands. In the trailer, Jason "
                  "picks Lucia up from jail.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/liberty-city-lives-on-in-spirit-as-gta-6-reveals-new-protagonist-lucia-is-from-gtas-new-york"],
         "main": True},
        {"claim": "Rockstar's character descriptions (via GTA BOOM): 'Lucia's father taught her to fight as soon as "
                  "she could walk.' She was incarcerated at the Leonida Penitentiary for a crime connected to "
                  "'fighting for her family'; Rockstar describes her release as 'sheer luck'; her line: 'only smart "
                  "moves from here'. Lucia 'grew up in Liberty City, the GTA universe's version of New York'; she is "
                  "'prepared to take matters into her own hands', unlike her mother's 'half-baked fantasies'.",
         "sources": ["https://www.gtaboom.com/everything-confirmed-about-jason-and-lucia-in-gta-6-cc2c",
                     "https://www.gtaboom.com/every-gta-6-character-confirmed-so-far-156f"], "main": True},
    ],
    description="Lucia isn't from Vice City: Rockstar's bio says she came from Liberty City, GTA's New York. Her "
                "father taught her to fight, fighting for her family put her in the Leonida Penitentiary, and she "
                "wants the good life her mom dreamed of.\nSources: Rockstar Games character text via GamesRadar+ "
                "and GTA BOOM.",
    hashtags=["#GTA6", "#LuciaCaminos", "#LibertyCity"],
)

S["gta6-money-glitch"] = dict(
    title="GTA 6's money glitch survived the new update",
    thumb_text="MONEY GLITCH LIVES",
    hook_card="THE GLITCH SURVIVED",
    cover_lines=["MONEY GLITCH", "SURVIVED THE UPDATE?", "HOW IT WORKS"],
    cover_frame={"shot": "trailer_2_01418", "f": 0.5, "x": 0.42},   # Jason on a motorbike, plane overhead (24 Nov check)
    beats=[
        ("GTA 6 just got a new update, and the infinite money glitch survived it.", "CLIP:extended_look_10132",
         None, "surprised"),
        ("On PS5 it's about six hundred megabytes. On Xbox, about 1.6 gigs.", "CLIP:extended_look_11192",
         "PS5 604MB / XBOX 1.6GB", None),
        ("It fixes crashes, the weather, autosaves, phone calls and wanted levels.", "CLIP:extended_look_09432",
         None, None),
        ("But the money glitch is completely untouched.", "CLIP:extended_look_09994", None, None),
        ("Here's how it works. In an abandoned red barn northeast of Hamlet, there are drugs and a bag of cash to grab.",
         "CLIP:extended_look_02513", "RED BARN, NE OF HAMLET", None),
        ("Players load up to four stash bags into their trunk, then save and reload.", "CLIP:extended_look_10037",
         "UP TO 4 BAGS", None),
        ("The loot comes back, but the bags stay in the car.", "CLIP:trailer_2_00452", None, None),
        ("Sell it at a fence like Brian's Lockup, and that's roughly eight to eleven thousand dollars a run.",
         "CLIP:extended_look_06719", "$8K-$11K PER RUN", None),
        ("So why are so many players skipping it?", "CLIP:trailer_2_00795", None, None),
        ("Early GTA 6 leans on the feeling of being broke, and some players call the glitch an easy way to ruin "
         "the experience.", "CLIP:extended_look_05543", None, None),
        ("TweakTown also reports that some of that farmed cash can get restricted later.", "CLIP:extended_look_09166",
         None, "amused"),
        ("So: glitch your way rich, or grind it out? Which side are you on?", "CLIP:extended_look_03021",
         None, None),
    ],
    facts=[
        {"claim": "Notebookcheck (Chibuike Okpara, 23 Nov 2026): the new GTA 6 update 'leaves the lucrative infinite "
                  "money glitch completely untouched'; download 603.8 MB on PlayStation 5 and 1.6 GB on Xbox Series "
                  "X|S; Rockstar's patch notes list crash fixes and fixes for weather, autosave, phone calls, Wanted "
                  "Level, the deadlift bar and partners handing bags to fences. The glitch: an apparently abandoned "
                  "red barn northeast of Hamlet with cocaine bundles and a cash-filled stash bag; up to four stash "
                  "bags fit in a vehicle trunk; players save and immediately reload with the trunk's cargo intact; "
                  "'up to $10,000 per run'.",
         "sources": ["https://www.notebookcheck.net/New-GTA-6-update-leaves-infinite-money-glitch-untouched.1457986.0.html"],
         "main": True},
        {"claim": "TweakTown (Hamid Murtaza, 22 Nov 2026): 'GTA 6 already has an infinite money glitch, but many "
                  "players are skipping it'; loot the red barn northeast of Hamlet, load the bags into a car, drive "
                  "away and return or save and reload so the loot respawns while the bags stay in the vehicle, sell "
                  "at a fence such as Brian's Lockup; 'roughly $8,000 to $11,000 per run'; 'Early GTA 6 leans heavily "
                  "on the feeling of being broke'; some replies call it 'an easy way to ruin the experience'; "
                  "'certain funds become restricted later' for players who farmed early.",
         "sources": ["https://www.tweaktown.com/news/114814/gta-6-already-has-an-infinite-money-glitch-but-many-players-are-skipping-it/index.html"],
         "main": True},
        {"claim": "ComicBook.com (Logan Moore, 23 Nov 2026): Rockstar hasn't patched the infinite money glitch; it "
                  "is mentioned nowhere in the update's patch notes.",
         "sources": ["https://comicbook.com/gaming/news/gta-6-money-infinite-glitch-bug-update/"], "main": False},
    ],
    description="GTA 6's 23 November update (about 604 MB on PS5, 1.6 GB on Xbox) fixed crashes and more, but not "
                "the red-barn money glitch: roughly $8,000-$11,000 a run. Why many players skip it.\n"
                "Sources: Notebookcheck, TweakTown, ComicBook.com.",
    hashtags=["#GTA6", "#GTA6Tips", "#GTA6Update"],
)

S["gta6-jason-landlord"] = dict(
    title="GTA 6's Jason lives rent-free. Here's the catch",
    thumb_text="JASON'S LANDLORD",
    hook_card="NO RENT? REALLY?",
    cover_lines=["JASON LIVES", "RENT-FREE?", "MEET HIS LANDLORD"],
    cover_frame={"shot": "trailer_2_00188", "f": 0.2, "x": 0.54},   # Jason in cap + sunglasses at his house (24 Nov check)
    beats=[
        ("In GTA 6, Jason has a place in the Keys, and he lives there rent-free.", "CLIP:trailer_2_00188",
         None, "curious"),
        ("Sounds like a dream, until you meet his landlord.", "CLIP:trailer_2_00081", None, None),
        ("His name is Brian.", "CLIP:trailer_2_00851", "BRIAN HEDER", None),
        ("Rockstar calls him \"a classic drug runner from the golden age of smuggling in the Keys.\"",
         "CLIP:trailer_1_00183", "QUOTE: ROCKSTAR GAMES", None),
        ("And he's still at it, moving product through his boat yard with his third wife, Lori.",
         "CLIP:launch_trailer_00026", None, "amused"),
        ("So what does Jason pay instead of rent? He helps with local shakedowns.", "CLIP:extended_look_10330",
         None, None),
        ("Rockstar says Jason grew up around grifters and crooks, so none of this is new to him.",
         "CLIP:extended_look_05543", None, None),
        ("His friend Cal works with Brian too.", "CLIP:extended_look_11437", None, None),
        ("Rockstar says Cal \"feels safest hanging at home, snooping on Coast Guard comms with a few beers and some "
         "private browser tabs open.\"", "CLIP:trailer_2_01293", "QUOTE: ROCKSTAR GAMES", "laughs softly"),
        ("So the house is free. The job just comes with it.", "CLIP:trailer_2_00114", None, None),
        ("A free house in the Keys, but you work for a smuggler: deal or no deal?", "CLIP:extended_look_07899",
         None, None),
    ],
    facts=[
        {"claim": "GamesRadar+ (Anna Koselke, 6 May 2025), quoting Rockstar's character text: Brian is 'still moving "
                  "product through his boat yard with his third wife, Lori'; Jason lives at his place 'so long as he "
                  "helps with local shakedowns'; 'Cal feels safest hanging at home, snooping on Coast Guard comms with "
                  "a few beers and some private browser tabs open.' Cal is friends with Jason.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/rockstar-gives-us-our-best-look-at-the-gta-6-characters-yet-from-a-beer-loving-conspiracy-believing-hermit-to-a-rap-duo-with-a-relentless-social-media-presence"],
         "main": True},
        {"claim": "GTA BOOM: Jason works 'for local drug runners' in the Leonida Keys, living rent-free with a "
                  "veteran trafficker named Brian Heder. Rockstar: 'Brian's a classic drug runner from the golden age "
                  "of smuggling in the Keys.' (Jason's landlord, boat yard). PSU: Cal is a friend of Jason and an "
                  "associate of Brian.",
         "sources": ["https://www.gtaboom.com/everything-confirmed-about-jason-and-lucia-in-gta-6-cc2c",
                     "https://www.gtaboom.com/every-gta-6-character-confirmed-so-far-156f",
                     "https://www.psu.com/news/grand-theft-auto-vi-details-jason-lucias-backgrounds-introduces-cal-boobie-drequan-more"],
         "main": True},
        {"claim": "GamesRadar+ (5 Oct 2026): Rockstar introduced Jason as someone who 'grew up around grifters and "
                  "crooks'.",
         "sources": ["https://gamesradar.com/games/grand-theft-auto/gta-6-story-lead-insists-rockstar-didnt-want-to-make-any-kind-of-statement-with-jasons-ex-military-background"],
         "main": False},
    ],
    description="Jason lives rent-free in the Keys, at a place owned by Brian Heder, a classic drug runner who still "
                "moves product through his boat yard. The rent: local shakedowns. Plus Cal, in Rockstar's words.\n"
                "Sources: Rockstar Games character text via GamesRadar+, GTA BOOM, PSU.",
    hashtags=["#GTA6", "#JasonDuval", "#GTA6Story"],
)

S["gta6-44-million"] = dict(
    title="GTA 6 sold 44.9 million in four days, analyst says",
    thumb_text="44.9M IN 4 DAYS?",
    hook_card="BIGGER THAN MOVIES?",
    cover_lines=["44.9 MILLION SOLD", "IN FOUR DAYS?", "VS TWO BLOCKBUSTERS"],
    cover_frame={"shot": "extended_look_11609", "f": 0.5, "x": 0.8},   # Jason in a dark suit, airport lounge (24 Nov check)
    beats=[
        ("In four days, GTA 6 made about as much as two blockbuster movies combined.", "CLIP:extended_look_11609",
         None, "surprised"),
        ("That's the estimate from Rhys Elliott at Alinea Analytics.", "CLIP:extended_look_07446",
         "ALINEA ANALYTICS", None),
        ("He estimates it sold 44.9 million copies by the end of its first weekend.", "CLIP:extended_look_15524",
         "44.9M COPIES (EST.)", None),
        ("That's more than four billion dollars in four days.", "CLIP:extended_look_15485", "$4B+ IN 4 DAYS", None),
        ("Spider-Man: Brand New Day made over two and a half billion at the box office.", "CLIP:extended_look_07351",
         "SPIDER-MAN: $2.5B+", None),
        ("Christopher Nolan's The Odyssey made about 1.8 billion.", "CLIP:extended_look_15698",
         "THE ODYSSEY: $1.8B", None),
        ("Together, that's about 4.3 billion. GTA 6 roughly matched it in one long weekend.",
         "CLIP:extended_look_09432", "MOVIES: ~$4.3B", None),
        ("The report even says it made twice as much as Taylor Swift's entire Eras Tour.",
         "CLIP:extended_look_06422", "2x THE ERAS TOUR", "amused"),
        ("Rockstar's own number is 3.79 billion dollars on day one.", "CLIP:launch_trailer_00026",
         "OFFICIAL DAY 1: $3.79B", None),
        ("The 44.9 million is an estimate. Neither Rockstar nor Take-Two has confirmed it.",
         "CLIP:trailer_2_00452", None, None),
        ("The same estimate puts about three in four of those copies on PS5.", "CLIP:extended_look_11192",
         "PS5: 75.1% (EST.)", None),
        ("Elliott calls it the biggest entertainment launch of all time. Do you agree, yes or no?",
         "CLIP:extended_look_07899", None, None),
    ],
    facts=[
        {"claim": "LevelUp (23 Nov 2026): 'Analyst Rhys Elliott from Alinea Analytics estimates that, by the end of "
                  "its first weekend, GTA 6 had already sold a staggering 44.9 million copies worldwide' (PS5 and Xbox "
                  "Series X|S); approximately $4 billion USD in 4 days; 'roughly equal to the combined box office' of "
                  "Spider-Man: Brand New Day ('surpassed $2.5 billion USD') and Christopher Nolan's The Odyssey "
                  "('reached $1.8 billion USD'), 'Together, both productions generated approximately $4.3 billion "
                  "USD'; 'generated twice as much revenue as Taylor Swift's entire Eras Tour'; Elliott calls it the "
                  "biggest entertainment launch of all time; the figures 'have not been officially confirmed'.",
         "sources": ["https://www.levelup.com/en/news/gta-6-has-reportedly-sold-more-than-44-million-copies-and-its-revenue-nearly-matches-the-combined-box-office-earnings-of-spider-man-and-the-odyssey/"],
         "main": True},
        {"claim": "Gadget Review via Yahoo Finance (Rex Edison, 23 Nov 2026): Alinea Analytics put launch-weekend "
                  "sell-through at 44.9 million copies between the 19 November release and the end of 22 November, "
                  "'more than $4 billion in consumer revenue'; 'Neither number has been confirmed by Rockstar Games or "
                  "parent company Take-Two Interactive.' Rockstar's own figure: '$3.79 billion in worldwide first-day "
                  "retail sales'. PS5 '33.7 million copies, or 75.1%'; Xbox '11.2 million copies, representing 24.9%'.",
         "sources": ["https://finance.yahoo.com/media-advertising/articles/gta-vi-launch-weekend-sales-190418068.html"],
         "main": True},
    ],
    description="Alinea Analytics estimates GTA 6 sold 44.9 million copies and made over $4 billion by the end of "
                "its first weekend - about the box office of Spider-Man: Brand New Day and The Odyssey combined. "
                "Rockstar and Take-Two haven't confirmed it; their own day-one figure is $3.79 billion.\n"
                "Sources: LevelUp, Gadget Review (Yahoo Finance).",
    hashtags=["#GTA6", "#GTA6Sales", "#GrandTheftAuto"],
)

S["gta6-fortnite-drop"] = dict(
    title="GTA 6 pulled players away from Fortnite, analyst says",
    thumb_text="FORTNITE FEELS IT",
    hook_card="FORTNITE DOWN 28%?",
    cover_lines=["FORTNITE PLAYERS", "LEAVING FOR GTA?", "THE NUMBERS"],
    cover_frame={"shot": "extended_look_06943", "f": 0.5, "x": 0.49},   # Lucia in a red bandana, robbery (24 Nov check)
    beats=[
        ("GTA 6 has been out for one week, and Fortnite is already feeling it.", "CLIP:extended_look_10196",
         None, "curious"),
        ("Rhys Elliott at Alinea Analytics estimates 40.8 million people logged in to play it last Sunday.",
         "CLIP:extended_look_07446", "40.8M ON SUNDAY (EST.)", None),
        ("So where did all those players come from?", "CLIP:trailer_2_00452", None, None),
        ("The same analyst says Fortnite's player base is down about twenty-eight percent.",
         "CLIP:extended_look_15524", "FORTNITE: ABOUT -28%", None),
        ("And Call of Duty is down forty-two percent.", "CLIP:extended_look_09432", "CALL OF DUTY: -42%",
         "surprised"),
        ("Before launch, Sensor Tower predicted this. It said other games could lose more than ten percent of their "
         "daily players in GTA 6's first month.", "CLIP:extended_look_06719", "PREDICTED: OVER -10%", None),
        ("And it named Fortnite as one of the most exposed.", "CLIP:extended_look_05648", None, None),
        ("None of these numbers have been officially confirmed. They're analyst estimates.", "CLIP:extended_look_15698", None, None),
        ("So, back to Fortnite when the hype fades, or is GTA 6 your new main? Which side are you on?",
         "CLIP:extended_look_03021", None, None),
    ],
    facts=[
        {"claim": "LevelUp (23 Nov 2026), reporting Alinea Analytics (analyst Rhys Elliott): about 40.8 million people "
                  "logged in on Sunday, November 22; Fortnite's player base down about 28%; Call of Duty down 42%; "
                  "these figures 'have not been officially confirmed'.",
         "sources": ["https://www.levelup.com/en/news/gta-6-has-reportedly-sold-more-than-44-million-copies-and-its-revenue-nearly-matches-the-combined-box-office-earnings-of-spider-man-and-the-odyssey/"],
         "main": True},
        {"claim": "GTA BOOM (Ray Ampoloquio, 17 Nov 2026): Sensor Tower projected that daily active player numbers "
                  "across games other than GTA VI 'could fall more than 10% in the month after launch'; it 'names "
                  "Fortnite and single-player AAA titles as the most exposed'.",
         "sources": ["https://www.gtaboom.com/sensor-tower-says-fortnite-stands-to-lose-the-most-players-after-gta-vi-launches-7982"],
         "main": True},
    ],
    description="An analyst estimate says 40.8 million people played GTA 6 on its first Sunday, while Fortnite fell "
                "about 28% and Call of Duty 42%. Sensor Tower predicted the dip before launch. None of it is "
                "official.\nSources: LevelUp (Alinea Analytics), GTA BOOM (Sensor Tower).",
    hashtags=["#GTA6", "#Fortnite", "#GTA6News"],
)

# ---- 26 Nov 2026 batch (written 25 Nov by the daily run; slots 12:00 / 14:00 / 17:00 / 20:00 / 02:00 UTC) ----

S["gta6-lucia-looks"] = dict(
    title="GTA 6: Lucia's hidden looks are in magazines. Here's how",
    thumb_text="LUCIA'S HIDDEN LOOKS",
    hook_card="15 HIDDEN LOOKS",
    cover_lines=["LUCIA HAS 15", "HIDDEN LOOKS?", "HERE'S HOW TO GET THEM"],
    cover_frame={"shot": "trailer_1_00084", "f": 0.6, "x": 0.5},   # Lucia in prison orange, face clear (25 Nov preview)
    experiment="E4-lucia",
    beats=[
        ("Lucia has fifteen hidden looks in GTA 6, and they're tucked away inside magazines.",
         "CLIP:extended_look_10132", None, "curious"),
        ("Players found magazines hidden all over Leonida.", "CLIP:extended_look_04786", None, None),
        ("Get close to one, and your Waink app pops up. Scan it, and the style unlocks.",
         "CLIP:extended_look_03894", "SCAN IT WITH WAINK", None),
        ("Then you'll find it at the salon or the tattoo parlor.", "CLIP:extended_look_04115", None, None),
        ("Community guides count fifteen magazine styles just for Lucia, with hair and makeup.",
         "CLIP:extended_look_07899", "LUCIA: 15 STYLES", None),
        ("Jason gets thirteen.", "CLIP:trailer_2_00188", "JASON: 13 STYLES", "amused"),
        ("There are also seventeen tattoos and thirty-four luxury watches to collect.",
         "CLIP:extended_look_12606", "17 TATTOOS, 34 WATCHES", None),
        ("That's seventy-nine unlockables in total, by the guides' count.", "CLIP:extended_look_07446",
         "79 UNLOCKABLES", "surprised"),
        ("And Rockstar didn't publish any instructions for this. Players worked it out themselves.",
         "CLIP:extended_look_02968", None, None),
        ("Want new makeup and nails? Look for the lip icon. That's a beauty parlour.",
         "CLIP:trailer_1_00728", "LIP ICON = MAKEUP", None),
        ("So: Lucia's trailer look, or a brand new style? Which side are you on?",
         "CLIP:extended_look_10196", None, None),
    ],
    facts=[
        {"claim": "Notebookcheck (Karan Sharma, 24 Nov 2026): players 'have discovered that scanning hidden magazines "
                  "across Leonida can unlock exclusive hairstyles for Jason and hairstyles and makeup options for "
                  "Lucia'; magazines are scanned with the Waink app, whose pop-up shows up when the player is close to "
                  "one; after scanning, the style 'will become accessible through the salon or tattoo parlor'. "
                  "'According to community guides, there are 79 different cosmetic unlockable items, which include 13 "
                  "Jason magazine styles, 15 Lucia magazine styles, 17 magazine tattoos, and 34 luxury watches.' "
                  "Rockstar 'did not publish official instructions explaining how the Waink magazine unlocks would "
                  "work'.",
         "sources": ["https://www.notebookcheck.net/GTA-6-Waink-app-unlocks-new-hairstyles-and-makeup-for-Jason-and-Lucia.1458943.0.html"],
         "main": True},
        {"claim": "VGC (Jordan Middler, 18 Nov 2026): change hair at barber shops or stylists around Leonida; for "
                  "Lucia, 'if you go to a beauty parlour (indicated by a lip icon when hovering over the location "
                  "icon) you can change her makeup and nails'; Jason and Lucia each have signature hairstyles.",
         "sources": ["https://www.videogameschronicle.com/guide/how-to-change-hair-in-gta-6"], "main": True},
    ],
    description="Lucia's extra hairstyles and makeup hide in magazines across Leonida: scan them with the Waink app, "
                "then pick the style at a salon. Community guides count 15 Lucia styles, 13 for Jason, 17 tattoos "
                "and 34 watches.\nSources: Notebookcheck, VGC.",
    hashtags=["#GTA6", "#LuciaCaminos", "#GTA6Tips"],
)

S["gta6-ps-record"] = dict(
    title="GTA 6 is PlayStation's biggest launch ever, Sony says",
    thumb_text="39 MILLION PLAYERS",
    hook_card="SONY'S NEW RECORD",
    cover_lines=["39 MILLION PLAYERS", "IN FOUR DAYS?", "SONY'S NEW RECORD"],
    cover_frame={"shot": "launch_trailer_00119", "f": 0.5, "x": 0.67},   # 26 Nov fix: 10330 at f 0.2 showed a hoop, face under the logo
    beats=[
        ("Sony just called GTA 6 the biggest launch in PlayStation history.", "CLIP:trailer_2_00188", None,
         "excited"),
        ("That's across three decades and five console generations.", "CLIP:extended_look_07501",
         "5 CONSOLE GENERATIONS", None),
        ("More than thirty-nine million people played it on PS5 in its first four days.",
         "CLIP:extended_look_12606", "39M+ PS5 PLAYERS", None),
        ("Together, they played six hundred and eighty-three million hours.", "CLIP:extended_look_09432",
         "683M HOURS", None),
        ("That's about seventy-eight thousand years of GTA, in four days.", "CLIP:extended_look_15698",
         "~78,000 YEARS", "surprised"),
        ("The average player put in seventeen point four hours.", "CLIP:extended_look_11437", "17.4 HOURS EACH",
         "amused"),
        ("It also set PlayStation's record for the highest number of players in one game at the same time.",
         "CLIP:extended_look_12735", None, None),
        ("That beat the old records for multiplayer and free-to-play games too.", "CLIP:extended_look_10618",
         None, None),
        ("And seventy percent of brand-new PS5s played GTA 6 first.", "CLIP:extended_look_11192",
         "70% OF NEW PS5s", None),
        ("One thing Sony didn't share: the actual peak number.", "CLIP:extended_look_02226", None, "short pause"),
        ("And remember, that's PlayStation alone. Xbox players aren't counted.", "CLIP:extended_look_09166",
         None, None),
        ("So where did you play it first: PS5 or Xbox? Pick a side.", "CLIP:extended_look_10132", None, None),
    ],
    facts=[
        {"claim": "Sony (PlayStation Blog, 23 Nov 2026, quoted by GamesRadar+, Anna Koselke, 24 Nov 2026): 'becoming "
                  "the biggest game launch in PlayStation history, across three decades and five console "
                  "generations'; 'More than 39 million unique players have experienced Jason and Lucia's story in "
                  "Grand Theft Auto 6 on PlayStation 5'; 'GTA 6 set a new record for the highest number of concurrent "
                  "players for any game on PlayStation, surpassing previous records across multiplayer, free-to-play, "
                  "and single-player titles'; 'players cumulatively logged an incredible 683 million hours'; 'an "
                  "average of 17.4 hours'; 'GTA 6 was the first game played on 70% of new PS5 consoles'.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/gta-6-is-the-biggest-launch-in-playstation-history-with-sony-reporting-more-than-39-million-unique-players-playing-rockstars-new-game-on-ps5/"],
         "main": True},
        {"claim": "Player.One (Theo Stering, 24 Nov 2026): Sony's figures cover November 19 to 22, 'its first four "
                  "days'; 'Sony didn't publish the actual peak concurrent count or name the previous record holder'; "
                  "the 39 million counts unique players on PS5 and 'doesn't include anyone playing on Xbox Series "
                  "X|S'. Push Square (Liam Croft, 24 Nov 2026): from launch on 19 November through the opening "
                  "weekend, over 39 million unique players; PlayStation's post: 'the biggest launch in PlayStation "
                  "history'. Calculated: 683 million hours / 8,766 hours a year = about 77,900 years.",
         "sources": ["https://www.player.one/gta-6-breaks-playstation-launch-record-over-39m-ps5-players-log-683m-hours-70-new-ps5s-run-it-164608",
                     "https://www.pushsquare.com/news/2026/11/gta-6-officially-the-biggest-launch-in-playstation-history-with-over-39-million-players"],
         "main": True},
    ],
    description="Sony says GTA 6 is the biggest launch in PlayStation history: 39 million+ PS5 players in four days, "
                "683 million hours (about 78,000 years), and a new record for players at once. Xbox isn't counted."
                "\nSources: Sony via GamesRadar+, Player.One, Push Square.",
    hashtags=["#GTA6", "#PS5", "#PlayStation"],
)

S["gta6-steal-cars"] = dict(
    title="GTA 6 won't let you steal every car. Here's how",
    thumb_text="2 TOOLS YOU NEED",
    hook_card="CARS YOU CAN'T STEAL?",
    cover_lines=["SOME CARS WON'T", "LET YOU STEAL THEM?", "THE 2 TOOLS YOU NEED"],
    cover_frame={"shot": "launch_trailer_00263", "f": 0.5, "x": 0.25},   # 26 Nov fix: 00604 at f 0.8 showed no face
    beats=[
        ("It's called Grand Theft Auto, but some GTA 6 cars won't let you steal them. Not yet.",
         "CLIP:extended_look_07899", None, "curious"),
        ("Rockstar North's Rob Nelson put it like this: \"Previously, you could just press triangle to automatically hotwire and "
         "steal any vehicle that you wanted and take off.\"", "CLIP:extended_look_07501", "QUOTE: ROCKSTAR", None),
        ("Now some parked cars stay locked until you get the right tools.", "CLIP:extended_look_08740", None, None),
        ("Tool one: the Slim Jim, from Chapter 2.", "CLIP:trailer_1_00702", "SLIM JIM: CHAPTER 2", None),
        ("It opens locks quietly, and the trunk opens without the alarm. Some have cash inside.",
         "CLIP:extended_look_09994", None, "amused"),
        ("But it can't start a keyless car. That needs tool two: the key cloner, from Chapter 3.",
         "CLIP:extended_look_04835", "KEY CLONER: CHAPTER 3", None),
        ("Stand by the door, pick Clone Key, and find the sweet spot.", "CLIP:extended_look_11192", None, None),
        ("Nelson says you can smash the window and get in, \"but you can't start it without the key cloner.\"",
         "CLIP:extended_look_09166", "QUOTE: ROCKSTAR", None),
        ("One old trick still works: \"You can always carjack any driver you see.\"", "CLIP:extended_look_09432",
         "QUOTE: ROCKSTAR", "excited"),
        ("A grabbed car might still have a tracker. Advanced ones tell the cops where you are.",
         "CLIP:extended_look_09766", None, None),
        ("So: smash the window, or Slim Jim and sneak? Which side are you on?", "CLIP:extended_look_03021",
         None, None),
    ],
    facts=[
        {"claim": "GamesRadar+ (Dustin Bailey, 27 Aug 2026), quoting Rockstar North's Rob Nelson to IGN: 'Previously, "
                  "you could just press triangle to automatically hotwire and steal any vehicle that you wanted and "
                  "take off.' 'you start off the game and there are certain parked cars that are not accessible to you "
                  "until you get a bit further along with the story and you acquire certain tools to get into them.' "
                  "'You can always carjack any driver you see.'",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/rockstar-says-gta-6-wont-let-you-magically-hotwire-every-car-you-acquire-certain-tools-to-get-into-them/"],
         "main": True},
        {"claim": "Kotaku (Zack Zwiezen, 28 Aug 2026): Nelson told TGG: 'You can smash the window and get in, but you "
                  "can't start it without the key cloner.' A carjacked car 'might still have a tracker in it'.",
         "sources": ["https://kotaku.com/for-the-first-time-in-25-years-gta-6-will-make-stealing-cars-hard-2000729419"],
         "main": True},
        {"claim": "PC Gamer (Andrea Shearon, 18 Nov 2026): 'You get the slim jim from Moses during Chapter 2'; "
                  "'Unlocking a car with a slim jim also lets you pop the trunk without setting off an alarm, and you "
                  "might find some goodies in car trunks like weapons, drugs, or cash'; 'A slim jim won't start a car "
                  "with keyless ignition', that needs a key cloner. 'You get the key cloner in Chapter 3'; stand next "
                  "to the door, select 'Clone Key', use the stick to find the sweet spot; advanced trackers 'relay your "
                  "exact location to the cops'.",
         "sources": ["https://www.pcgamer.com/games/grand-theft-auto/gta-6-slim-jim/",
                     "https://www.pcgamer.com/games/grand-theft-auto/gta-6-clone-keys/"], "main": True},
    ],
    description="GTA 6 locks some parked cars until you get the right tools: the Slim Jim (Chapter 2) opens them "
                "quietly, the key cloner (Chapter 3) starts keyless cars, and carjacking still works.\nSources: "
                "Rockstar's Rob Nelson via GamesRadar+ and Kotaku; PC Gamer.",
    hashtags=["#GTA6", "#GTA6Tips", "#GrandTheftAuto"],
)

S["gta6-mario-caps"] = dict(
    title="GTA 6 hides Mario-style caps for Jason and Lucia",
    thumb_text="MARIO-STYLE CAPS",
    hook_card="A MARIO SECRET?",
    cover_lines=["MARIO CAPS FOR", "JASON AND LUCIA?", "HOW TO FIND THEM"],
    cover_frame={"shot": "extended_look_10081", "f": 0.2, "x": 0.55},   # Jason in a cap by the van, face clear at f 0.2 (25 Nov preview)
    beats=[
        ("Players found a secret in GTA 6 that gives Jason and Lucia Mario and Luigi-style caps.",
         "CLIP:extended_look_10081", None, "excited"),
        ("It's in the far north of Leonida, past Mount Kalaga, at some old stone ruins.", "CLIP:extended_look_06960",
         "NORTH OF MOUNT KALAGA", None),
        ("First, find a purple tarp near the ruins and interact with it.", "CLIP:extended_look_04675",
         "1. PURPLE TARP", None),
        ("Then climb the ruins, and stand in the smoke rising from one of the broken columns.",
         "CLIP:trailer_2_01113", "2. STAND IN THE SMOKE", None),
        ("A hidden block appears above your head.", "CLIP:extended_look_10330", "3. HIT THE BLOCK", "curious"),
        ("The player who found it, xGarbett, couldn't break it by jumping, so they shot it instead.",
         "CLIP:extended_look_02968", None, "amused"),
        ("It still worked. A familiar little tune plays, and two caps pop out.", "CLIP:extended_look_13887",
         None, None),
        ("A red one with a J for Jason, and a green one with an L for Lucia.", "CLIP:extended_look_03869",
         "RED J + GREEN L", None),
        ("Kotaku's Zach Zwiezen tested it, then tried the caps on at a clothing store.", "CLIP:trailer_2_00416",
         None, None),
        ("So who wears it better: Jason in red, or Lucia in green? Pick a side.", "CLIP:extended_look_10196",
         None, None),
    ],
    facts=[
        {"claim": "VGTimes (Arkadiy Andrienko, 24 Nov 2026): in Lammox County, 'north of Leonida beyond Mount Kalaga', "
                  "players 'have found a hidden Easter egg that unlocks red and green caps for Jason and Lucia'; "
                  "'players must interact with a purple tarp, climb the ruins, and stand in smoke rising from one of "
                  "the columns'; a hidden block appears above the character; hitting it plays a familiar tune and "
                  "releases two caps, one with a J (Jason) and one with an L (Lucia); the secret 'does not use "
                  "Nintendo's names or symbols'; the discoverer, xGarbett, couldn't break the block by jumping, so "
                  "they shot it instead, and that still revealed the caps; Kotaku's Zach Zwiezen also tested the find "
                  "and went to a clothing store to try on the accessories.",
         "sources": ["https://vgtimes.com/gaming-news/175580-gta-6-easter-egg-lets-jason-and-lucia-wear-mario-and-luigi-style-caps.html"],
         "main": True},
        {"claim": "KhelNow (Mahaksh Chouhan, 24 Nov 2026): the Easter egg is in northern Leonida, beyond Mount Kalaga, "
                  "at abandoned stone ruins; interact with the item on a purple tarp, climb to the top of the nearby "
                  "ruins, stand inside the plume of smoke rising from one of the broken columns; a floating invisible "
                  "block appears above the character; rewards: a red cap with the letter 'J' for Jason and a green cap "
                  "with the letter 'L' for Lucia; DiscussingFilm (23 Nov): 'A Mario easter egg has been found in GTA "
                  "6.'",
         "sources": ["https://khelnow.com/gaming/gta-6-mario-luigi-easter-egg-location-202611"], "main": True},
    ],
    description="Players found a Mario-style secret in GTA 6: past Mount Kalaga, use the purple tarp, stand in the "
                "smoke on the ruins and hit the hidden block for a red J cap (Jason) and a green L cap (Lucia).\n"
                "Sources: VGTimes, KhelNow.",
    hashtags=["#GTA6", "#GTA6Secrets", "#EasterEgg"],
)

S["gta6-lose-cash"] = dict(
    title="GTA 6 takes all your cash when you die. Keep it like this",
    thumb_text="KEEP YOUR CASH",
    hook_card="DIE = LOSE IT ALL?",
    cover_lines=["DIE AND LOSE", "ALL YOUR CASH?", "3 WAYS TO KEEP IT"],
    cover_frame={"shot": "launch_trailer_00670", "f": 0.5, "x": 0.6},   # Jason + Lucia embracing on a balcony at sunset (25 Nov preview)
    beats=[
        ("Die in GTA 6, and every dollar in your pocket is gone.", "CLIP:extended_look_03021", None, "serious"),
        ("In older GTA games, you only lost part of it. Not anymore.", "OFFICIAL:v_24ba6644de", None, None),
        ("And money matters more this time. Rockstar says you need enough of it to move the story forward.",
         "CLIP:extended_look_09994", None, None),
        ("Here's how to keep it. One: a BuckMe bank account, from an early Chapter 1 mission.",
         "CLIP:extended_look_03894", "1. BUCKME ACCOUNT", None),
        ("You can't move cash in the app. You have to visit an ATM.", "CLIP:extended_look_10699",
         None, "amused"),
        ("Banked money isn't totally safe: one guide says you still lose a little of it when you die.",
         "CLIP:extended_look_09432", None, None),
        ("Two: Family Savings. Money you put in there can't be withdrawn, and it can't be lost.",
         "CLIP:extended_look_07446", "2. FAMILY SAVINGS", None),
        ("Three: the floorboards in Jason's bedroom. Cash stashed there survives death and arrest.",
         "CLIP:trailer_2_00188", "3. FLOORBOARD STASH", None),
        ("One catch: later story events can affect that stash.", "CLIP:trailer_2_00996", None, "short pause"),
        ("And big buys need the bank anyway. Anything over a thousand dollars has to come from BuckMe.",
         "CLIP:extended_look_04835", "OVER $1,000 = BUCKME", None),
        ("So: carry your cash and risk it, or bank every dollar? Which side are you on?",
         "CLIP:extended_look_10132", None, None),
    ],
    facts=[
        {"claim": "GamesFuze (Andrés, 19 Nov 2026, updated 22 Nov): 'In previous games in the series, you would only "
                  "lose a part of your money. However, in GTA 6, you lose everything you have on hand.' Stash: at "
                  "Jason's House, interact with 'the floorboards in the bedroom'; stashed money and items are kept on "
                  "death or arrest; 'Later story events can affect your stash.' BuckMe unlocks by completing the 'Buck "
                  "Me' mission, one of the first missions in Chapter 1; 'you cannot transfer funds between your on-hand "
                  "cash and BuckMe account within the app itself. You will need to go to ATMs every time'; on death or "
                  "arrest 'you'll still lose a small amount of your BuckMe money' as a small 'maintenance fee'; Family "
                  "Savings: 'You can no longer withdraw or lose money from Family Savings'; 'all purchases higher than "
                  "$1000 require BuckMe funds'.",
         "sources": ["https://gamesfuze.com/guides/gta-6-how-to-avoid-losing-money-when-you-die/"], "main": True},
        {"claim": "eGamers (George Tsagkarakis, 19 Nov 2026): 'Money in Family Savings is never lost, and meeting "
                  "savings goals raises your checking limit and unlocks discounts.'",
         "sources": ["https://egamers.io/gta-6-buckme-guide-how-family-savings-checking-limits-and-perks-work/"],
         "main": False},
        {"claim": "TweakTown (Derek Strickland, 31 Aug 2026): 'Making cash isn't optional though--you'll need to make "
                  "enough money to progress the story, Rockstar confirms.'",
         "sources": ["https://www.tweaktown.com/news/113368/gta-6s-illicit-criminal-economy-robberies-and-money-explained-by-rockstar/index.html"],
         "main": True},
    ],
    description="In GTA 6 you lose all the cash you carry when you die. Keep it in BuckMe (ATMs only), Family "
                "Savings (can't be lost) or the floorboard stash in Jason's bedroom.\nSources: GamesFuze, eGamers, "
                "TweakTown.",
    hashtags=["#GTA6", "#GTA6Tips", "#GTA6Money"],
)

S["gta6-lucia-svu"] = dict(
    title="GTA 6's Lucia actress played a boxer on Law & Order",
    thumb_text="LUCIA'S ACTRESS",
    hook_card="SHE PLAYED A BOXER",
    cover_lines=["LUCIA'S ACTRESS", "WAS ON LAW & ORDER?", "HER BIG BREAK"],
    cover_frame={"image": "img2", "zone": "lower"},   # 27 Nov fix: Lucia in boxing gloves (official still), face clear above the logo (10387 put her face under it)
    experiment="E4-lucia",
    beats=[
        ("Lucia's actress played a boxer on Law and Order, years before GTA 6.", "CLIP:extended_look_10132", None,
         "excited"),
        ("Her name is Manni L. Perez. In a twenty-twenty episode of Special Victims Unit, she played Esperanza "
         "Morales.", "OFFICIAL:vi_Lucia_Caminos_09", "MANNI L. PEREZ", None),
        ("Esperanza is a young boxer who ends up facing a murder charge.", "CLIP:extended_look_10387",
         "SVU: A YOUNG BOXER", None),
        ("Perez says of that part: I basically just played myself, but a bit less animated.",
         "OFFICIAL:vi_Lucia_Caminos_10", None, "amused"),
        ("She calls it her big break, and says it won her an Imagen Award for Best Supporting Actress.",
         "OFFICIAL:vi_Lucia_Caminos_02", "IMAGEN AWARD", None),
        ("After that came Chicago P.D., The Blacklist, Blindspot and Jessica Jones.", "OFFICIAL:vi_Lucia_Caminos_03",
         "4 MORE TV SHOWS", None),
        ("And in GTA 6, her Lucia starts out in prison.", "OFFICIAL:vi_Lucia_Caminos_05", None, None),
        ("Now that role has her nominated for Best Performance at The Game Awards.", "OFFICIAL:vi_Lucia_Caminos_14",
         "GAME AWARDS NOMINEE", "excited"),
        ("So: should Lucia's actress win it? Yes or no, pick a side.", "OFFICIAL:vi_Jason_and_Lucia_01", None, None),
    ],
    facts=[
        {"claim": "TVLine (Michael Boyle, 23 Nov 2026), 'GTA 6's Lucia Actress Had A Role On Law & Order: Special "
                  "Victims Unit': Lucia Caminos is played by Manni L. Perez; she starred in the 2020 SVU episode "
                  "'Redemption in Her Corner' as Esperanza Morales, a young boxer who accidentally kills her coach and "
                  "faces murder charges; Perez: 'I basically just played myself, but a bit less animated'; she calls "
                  "the role her 'big break' that 'led me to win an Imagen Award ... for Best Supporting Actress in a "
                  "TV Series' (quoted from the Hollywood Times); later roles in 'Chicago P.D.', 'The Blacklist', "
                  "'Blindspot' and 'Jessica Jones'; her Lucia performance earned 'a nomination for Best Performance at "
                  "The Game Awards 2026'.",
         "sources": ["https://www.tvline.com/2325622/gta-6-lucia-actress-manni-l-perez-law-and-order-special-victims-unit-role/"],
         "main": True},
        {"claim": "Notebookcheck (Darryl Linington, 25 Nov 2026): the game opens with 'Lucia's prison prologue'.",
         "sources": ["https://www.notebookcheck.net/GTA-6-PC-ports-reach-gameplay-despite-Take-Two-s-GitHub-DMCA.1459752.0.html"],
         "main": False},
    ],
    description="Before GTA 6, Lucia's actress Manni L. Perez played a young boxer, Esperanza Morales, in a 2020 "
                "Law & Order: SVU episode - her 'big break'. Now she's nominated for Best Performance at The Game "
                "Awards.\nSources: TVLine, Notebookcheck.",
    hashtags=["#GTA6", "#LuciaCaminos", "#MannILPerez"],
)

S["gta6-cut-tennis"] = dict(
    title="GTA 6 cut tennis, a GTA 5 favourite. Rockstar says why",
    thumb_text="TENNIS WAS CUT",
    hook_card="WHAT ROCKSTAR CUT",
    cover_lines=["GTA 5 HAD TENNIS.", "WHY DID 6 CUT IT?", "ROCKSTAR EXPLAINS"],
    cover_frame={"shot": "extended_look_03869", "f": 0.5, "x": 0.32},   # Jason in a tank top (R3: face)
    experiment="E5-gta5-callback",
    beats=[
        ("GTA 5 had tennis.", "OFFICIAL:vi_Jason_Duval_02", None, "curious"),   # 27 Nov v3: the 03869 crop cut Jason's face off
        ("GTA 6 was going to have it too, until Rockstar cut it.", "CLIP:trailer_2_00188", None, None),
        ("Rob Nelson and Scott Mitchell from Rockstar North told the German magazine PC Games what didn't make it.",
         "CLIP:extended_look_12920", "PC GAMES INTERVIEW", None),
        ("Tennis was planned, but it didn't meet the studio's standards.", "OFFICIAL:v_24ba6644de",
         "CUT: TENNIS", None),
        ("Trips to the cinema and the theatre were cut too. They weren't interactive enough.",
         "CLIP:extended_look_04501", "CUT: CINEMA + THEATRE", None),
        ("So were home decorating and crafting.", "CLIP:extended_look_03826", "CUT: HOME DECORATING", None),
        ("Even crawling got cut.", "CLIP:extended_look_02968", "CUT: CRAWLING", "amused"),
        ("Those didn't fit the story or the gameplay well enough.", "OFFICIAL:vi_Jason_and_Lucia_07", None, None),
        ("But one game made it: mini golf.", "OFFICIAL:vi_Cal_Hampton_01", "KEPT: MINI GOLF", "excited"),
        ("And nothing in the interview says the cut features are coming back in an update.",
         "CLIP:extended_look_07501", None, None),
        ("So: which cut hurts more, tennis or home decorating? Pick a side.", "OFFICIAL:vi_Jason_and_Lucia_03",
         None, None),
    ],
    facts=[
        {"claim": "Dexerto (Dylan Horetski, 25 Nov 2026): in an interview with German outlet PC Games, Rockstar North's "
                  "Rob Nelson and design producer Scott Mitchell revealed cut features: tennis, cinema and theatre "
                  "visits, crawling, home decorating and crafting; tennis 'players could participate in throughout GTA "
                  "5'; Rockstar planned to bring it back for GTA 6 but its implementation failed to meet the "
                  "developer's standards; 'Cinema and theater visits were also removed, as Rockstar felt the activities "
                  "were not interactive enough'; mini golf 'made it into the finished game'.",
         "sources": ["https://www.dexerto.com/gta/gta-6-devs-reveal-major-gameplay-features-that-didnt-make-the-final-cut-3431334/"],
         "main": True},
        {"claim": "Rockstar Report (25 Nov 2026): 'a PC Games interview with Rockstar North development lead Rob Nelson "
                  "and design producer Scott Mitchell'; 'Rockstar North planned a full tennis minigame for Grand Theft "
                  "Auto VI, then removed it'; crafting, home furnishing and crawling were discarded when they did not "
                  "fit the story or gameplay well enough; the studio retained minigolf; the interview does not suggest "
                  "the cut features return in an update.",
         "sources": ["https://rockstarreport.com/news/rockstar-explains-gta-6-cut-tennis-cinemas"], "main": True},
    ],
    description="Rockstar North's Rob Nelson and Scott Mitchell told PC Games what GTA 6 cut: tennis (a GTA 5 "
                "activity), cinema and theatre trips, home decorating, crafting and crawling. Mini golf stayed.\n"
                "Sources: Dexerto, Rockstar Report.",
    hashtags=["#GTA6", "#GTA5", "#Rockstar"],
)

S["gta6-black-friday"] = dict(
    title="GTA 6 on Black Friday: where it's actually cheaper",
    thumb_text="BLACK FRIDAY",
    hook_card="NOT ON SALE?",
    cover_lines=["GTA ON SALE FOR", "BLACK FRIDAY?", "WHERE IT'S CHEAPER"],
    cover_frame={"shot": "trailer_1_00625", "f": 0.5, "x": 0.44},   # Lucia with cash in a car (R3: face; money)
    beats=[
        ("It's Black Friday. So is GTA 6 cheaper yet? Here's where to look.", "CLIP:extended_look_07899",
         None, "serious"),
        ("This week, GameRant and GamingHQ found no discount on the UK PlayStation or Xbox stores.",
         "CLIP:extended_look_09166", "NO STORE DISCOUNT", None),
        ("In the US, the normal price is seventy-nine ninety-nine, or ninety-nine ninety-nine for the Ultimate Edition.",
         "OFFICIAL:vi_ULTIMATE_EDITION_02", "$79.99 / $99.99", None),
        ("But in the UK, one shop is cheaper. Here's how to save.", "CLIP:extended_look_10699", None, "excited"),
        ("One: ShopTo sells the Xbox digital code for fifty-five eighty-five, instead of sixty-nine ninety-nine.",
         "CLIP:extended_look_09766", "1. XBOX: £55.85", None),
        ("Two: the Ultimate Edition on Xbox is sixty-nine eighty-five, about twenty-two percent off.",
         "OFFICIAL:vi_ULTIMATE_EDITION_SQUALO_03", "2. ULTIMATE: £69.85", None),
        ("Three: on PlayStation, buy seventy pounds of credit for sixty pounds eighty-five, then use it on the game.",
         "CLIP:extended_look_04835", "3. PS CREDIT: £60.85", None),
        ("Boxed codes are sixty-one eighty-five on both consoles.", "CLIP:extended_look_07238", "BOXED: £61.85", None),
        ("Deals change fast on Black Friday, so check the price before you pay.", "CLIP:extended_look_09432", None,
         None),
        ("So: buy GTA 6 now, or hold out for a real sale? Pick a side.", "OFFICIAL:vi_Jason_and_Lucia_14", None,
         None),
    ],
    facts=[
        {"claim": "GameRant (Dominik Bošnjak, 25 Nov 2026): 'Grand Theft Auto 6 is already available at discounts of "
                  "up to 22% as part of some early Black Friday offers'; 'The Standard and Ultimate Editions of GTA 6 "
                  "are regularly priced at $79.99 and $99.99, respectively. Their UK prices are £69.99 ... and "
                  "£89.99'; ShopTo: Standard (Digital) Xbox £55.85 (20%), Ultimate (Digital) Xbox £69.85 (22%), "
                  "Standard boxed code £61.85 on Xbox and PlayStation (12%); 'The retailer is currently offering £70 "
                  "gift cards for £60.85'; 'Neither Sony nor Microsoft is currently offering discounts on the game "
                  "through its respective UK digital storefront.'",
         "sources": ["https://gamerant.com/gta-6-black-friday-sale-deal/"], "main": True},
        {"claim": "GamingHQ (26 Nov 2026), 'GTA 6 Black Friday Deals Slash Prices by Up to 22%': ShopTo Xbox digital "
                  "Standard '£55.85, representing a discount of approximately 20%'; Ultimate '£69.85, offering savings "
                  "of around 22%'; boxed '£61.85 on both consoles'; '£70 worth of PlayStation wallet credit for "
                  "£60.85'; 'the official UK PlayStation and Xbox storefronts have yet to introduce comparable offers'.",
         "sources": ["https://gaminghq.eu/2026/11/26/gta-6-black-friday-deals/"], "main": True},
        {"claim": "Nacionale (16 Nov 2026): no Black Friday price cut announced; GTA VI 'costs $79.99 for the Standard "
                  "Edition and $99.99 for the Ultimate Edition in the US'; Best Buy: 'still $79.99 at checkout'.",
         "sources": ["https://www.nacionale.com/en/articles/will-gta-6-be-on-sale-black-friday-price-79-99-ultimate-edition-deals"],
         "main": False},
    ],
    description="GTA 6 on Black Friday: no discount on the PlayStation or Xbox stores this week ($79.99 / $99.99 in "
                "the US). In the UK, ShopTo had it for £55.85 on Xbox, £69.85 Ultimate, or £60.85 via PS credit. Check "
                "prices before you buy.\nSources: GameRant, GamingHQ, Nacionale.",
    hashtags=["#GTA6", "#BlackFriday", "#GTA6Deals"],
)

S["gta6-niko-cameo"] = dict(
    title="GTA 6 hides a GTA 4 legend near the end. Rockstar explains",
    thumb_text="SPOILER: GTA 4 LEGEND",
    hook_card="SPOILER WARNING",
    cover_lines=["SPOILER: A GTA 4", "LEGEND IS BACK?", "ROCKSTAR EXPLAINS"],
    cover_frame={"shot": "trailer_2_00795", "f": 0.5, "x": 0.31},   # Lucia + Jason with drinks at a bar (R3: faces)
    experiment="E5-gta5-callback",
    beats=[
        ("Spoiler warning: a GTA 4 legend is hiding in GTA 6.", "OFFICIAL:vi_Lucia_Caminos_10", None, "serious"),   # 27 Nov v3: the 00728 crop showed lamps, not faces
        ("It's Niko Bellic, the hero of GTA 4.", "CLIP:trailer_1_00300", "NIKO BELLIC", "excited"),
        ("Near the end, he turns up as a hitman for a Balkan cartel, sent to deal with a character called Giorgio.",
         "CLIP:extended_look_12920", None, None),
        ("Rockstar's Rob Nelson told Kotaku it just grew very organically.", "CLIP:trailer_2_00346",
         "QUOTE: ROCKSTAR", None),
        ("Even Niko's original voice actor came back for it.", "CLIP:extended_look_06719", None, None),
        ("And listen when that mission ends. The jingle is the one from GTA 4.", "CLIP:extended_look_10510",
         "GTA 4'S JINGLE", "amused"),
        ("Nelson called it a late addition. For a long time, it was a normal GTA 6 sound.",
         "CLIP:extended_look_07501", None, None),
        ("So is Niko gone for good? He's still kicking around, Nelson said. He's still in play.",
         "CLIP:extended_look_12327", None, "curious"),
        ("He also confirmed Niko goes back to Liberty City afterwards, but won't say which GTA 4 ending is the real "
         "one.", "CLIP:extended_look_04180", None, None),
        ("Nelson hoped the cameo would stay secret for a bit. Players posted it in under three days.",
         "CLIP:extended_look_12606", "POSTED IN < 3 DAYS", None),
        ("So: should Niko get a bigger part in GTA 6's future? Yes or no, pick a side.",
         "OFFICIAL:vi_Jason_and_Lucia_09", None, None),
    ],
    facts=[
        {"claim": "Kotaku (Zack Zwiezen, 25 Nov 2026), 'GTA 6 Boss Reveals How That Very Surprising Cameo Happened And "
                  "What It Means For The Character' (spoilers): near the end of the main story, Niko Bellic, GTA IV's "
                  "protagonist, appears as a Balkan cartel hitman sent to deal with Giorgio; Rockstar head of production "
                  "Rob Nelson: 'It just grew very organically', the Balkan-cartel storyline started early in "
                  "development; original voice actor returned for the role; the mission-complete jingle after the "
                  "cameo is from GTA IV, which Nelson called a 'late addition': 'For a long time it was like a normal "
                  "[GTA 6] stinger'; on Niko: 'He's still kicking around. He's still in play'; Nelson confirmed Niko "
                  "returns to Liberty City after these events but would not say which GTA IV ending is canon; Nelson "
                  "hoped the cameo 'stays secret for a bit'; many players posted videos of it less than three days "
                  "after launch.",
         "sources": ["https://kotaku.com/gta-6-boss-reveals-how-that-very-surprising-cameo-happened-and-what-it-means-for-the-character-2000758616"],
         "main": True},
    ],
    description="Spoilers: Niko Bellic, GTA 4's hero, appears near the end of GTA 6 as a Balkan cartel hitman. "
                "Rockstar's Rob Nelson told Kotaku how it happened, why the GTA 4 jingle plays, and that Niko is "
                "'still in play'.\nSources: Kotaku.",
    hashtags=["#GTA6", "#GTA4", "#NikoBellic"],
)

S["gta6-pc-port"] = dict(
    title="GTA 6 fan PC ports hit 5 fps. Take-Two shut one down",
    thumb_text="FAN PC PORTS",
    hook_card="NO PC VERSION YET",
    cover_lines=["FANS PUT IT ON PC?", "3,007 COPIES", "SHUT DOWN"],
    cover_frame={"image": "img3", "zone": "lower"},   # 27 Nov fix: hooded Jason close-up (official still; 00882 was a 23 Nov cover)
    beats=[
        ("Fans are trying to put GTA 6 on PC without Rockstar, and Take-Two is shutting them down.",
         "CLIP:extended_look_10081", None, "serious"),
        ("On November twenty-fourth, a takedown notice published by GitHub disabled the most prominent project, "
         "called Leonida.", "CLIP:extended_look_12920", "PROJECT: LEONIDA", None),
        ("It covered the project's whole network: three thousand and seven copies.", "OFFICIAL:vi_Jason_Duval_10",
         "3,007 REPOS DOWN", "surprised"),
        ("The notice argues it's built on stolen files from a leaked Xbox version, and breaks Rockstar's ban on "
         "reverse engineering.", "CLIP:extended_look_08201", None, None),
        ("Discord servers organising the work have gone offline too.", "CLIP:extended_look_02226", None, None),
        ("And here's the catch: the builds barely run.", "CLIP:extended_look_09166", None, "amused"),
        ("The fastest ones reported so far reach three to five frames a second.", "CLIP:extended_look_09766",
         "3-5 FPS", None),
        ("One clip runs Lucia's prison opening at one to three frames a second, on an RTX fifty seventy Ti.",
         "OFFICIAL:vi_Lucia_Caminos_05", "1-3 FPS", None),
        ("And Rockstar still hasn't announced a PC version.", "CLIP:extended_look_15698", None, None),
        ("So: wait for Rockstar's own PC version, or buy a console now? Pick a side.",
         "OFFICIAL:vi_Jason_and_Lucia_13", None, None),
    ],
    facts=[
        {"claim": "Notebookcheck (Darryl Linington, 25 Nov 2026), 'GTA 6 PC ports reach gameplay despite Take-Two's "
                  "GitHub DMCA': 'A DMCA notice published by GitHub on November 24 disabled Leonida, the most prominent "
                  "project working from the Xbox Series build leaked by Cyberleek earlier this month. GitHub says the "
                  "takedown covered the project's full network of 3,007 repositories.' The notice argues 'the project "
                  "is a derivative work built on stolen files and that it violates Rockstar's ban on reverse "
                  "engineering.' 'the fastest builds reported so far only reach 3 to 5 FPS'; one clip shows the "
                  "prologue 'at just 1 to 3 FPS on an RTX 5070 Ti'; builds have 'cleared Lucia's prison prologue'; "
                  "Discord coordination servers have gone offline; 'Rockstar has not announced a PC version.'",
         "sources": ["https://www.notebookcheck.net/GTA-6-PC-ports-reach-gameplay-despite-Take-Two-s-GitHub-DMCA.1459752.0.html"],
         "main": True},
        {"claim": "KitGuru (Matthew Wilson, 26 Nov 2026): 'DMCA notices began targeting GitHub repositories associated "
                  "with the projects'; Discord communities organising reverse-engineering efforts were shut down by "
                  "legal notices from Take-Two's legal team (per PC Gamer); clips show the game running 'at unplayable "
                  "frame rates'.",
         "sources": ["https://www.kitguru.net/gaming/matthew-wilson/rockstar-begins-taking-down-unofficial-gta-6-pc-port-efforts-on-github-and-discord/"],
         "main": False},
    ],
    description="Unofficial GTA 6 PC ports built from a leaked Xbox version: Take-Two's DMCA took down Leonida's 3,007 "
                "GitHub repositories, and the best builds run at 3-5 fps. Rockstar hasn't announced a PC version.\n"
                "Sources: Notebookcheck, KitGuru.",
    hashtags=["#GTA6", "#GTA6PC", "#PCGaming"],
)

S["gta6-ages"] = dict(
    title="GTA 6 fans found Jason and Lucia's ages. Lucia's twist",
    thumb_text="THEIR REAL AGES",
    hook_card="FANS FOUND THEIR IDS",
    cover_lines=["JASON 30, LUCIA 26?", "FANS FOUND THEIR IDS", "AND A BIRTHDAY TWIST"],
    cover_frame={"image": "img5", "zone": "lower"},   # Lucia_Caminos_07: Lucia close-up, face above the logo (27 Nov preview; E6 still cover)
    experiment="E5-older-gta+E6-still-cover",
    beats=[
        ("Fans just found Jason and Lucia's driver's licences in GTA 6.", "CLIP:extended_look_10196", None, "excited"),
        ("And the dates on them are making a lot of people feel old.", "OFFICIAL:vi_Jason_and_Lucia_01", None, "amused"),
        ("Jason was born on May the first, nineteen ninety-six. That makes him thirty.",
         "OFFICIAL:vi_Jason_Duval_02", "JASON: 30", None),
        ("His licence says he's six foot three, and he lives down in Key Lento.", "CLIP:trailer_2_00188",
         "6'3\", KEY LENTO", None),
        ("Lucia is twenty-six. She's a full foot shorter, at five foot three.", "OFFICIAL:vi_Lucia_Caminos_07",
         "LUCIA: 26, 5'3\"", None),
        ("And her licence wasn't issued in Leonida. It was issued in Liberty City, the city from GTA 4.",
         "OFFICIAL:vi_Lucia_Caminos_03", "ISSUED: LIBERTY CITY", "curious"),
        ("Now look at her birthday: November the twentieth, two thousand.", "OFFICIAL:vi_Lucia_Caminos_06",
         "BORN: 20 NOV 2000", None),
        ("GTA 6 came out on November the nineteenth. So Lucia turned twenty-six the very next day.",
         "CLIP:extended_look_12606", "LAUNCH: 19 NOV", "surprised"),
        ("Rockstar hasn't announced any of this. Fans read it off the licences in the game.",
         "OFFICIAL:vi_Jason_and_Lucia_17", None, None),
        ("So: Jason at thirty, Lucia at twenty-six. Who's really in charge? Pick a side.",
         "OFFICIAL:vi_Jason_and_Lucia_14", None, None),
    ],
    facts=[
        {"claim": "UNILAD (Callum Jones, 26 Nov 2026), 'GTA 6 fans have discovered Jason and Lucia's ages': from the "
                  "in-game driver's licenses, Jason Duval was born May 1, 1996, so he is 30, height 6 ft 3 in, resides "
                  "in Key Lento; Lucia Caminos is 26, date of birth November 20, 2000, height 5 ft 3 in, license issued "
                  "in Liberty City. A player discovery; the article does not say Rockstar confirmed the numbers.",
         "sources": ["https://www.unilad.com/technology/gta-6-players-discover-jason-lucia-ages-202979-20261126"],
         "main": True},
        {"claim": "LAFM (27 Nov 2026) and Pulptastic (27 Nov 2026): fans tracked down the in-game driver's licences; Jason "
                  "born 1 May 1996 (30), 6 ft 3 in, Key Lento; Lucia born 20 November 2000 (26), 5 ft 3 in, licence "
                  "issued in Liberty City; a fan post on 23 Nov said Lucia 'celebrated her 26th birthday just 3 days "
                  "ago'. TechWiser: Rockstar hasn't revealed their exact ages officially.",
         "sources": ["https://www.lafm.com.au/trending/gaming/gta-6-fans-just-found-jason-and-lucias-ages-and-now-everyone-feels-ancient/",
                     "https://pulptastic.com/gta-6-fans-have-discovered-jason-and-lucias-ages-and-its-making-them-feel-old/"],
         "main": True},
        {"claim": "Rockstar: GTA 6 releases at 'midnight local time on November 19, 2026, in all regions' (Forbes, 12 Nov "
                  "2026). Liberty City is the setting of Grand Theft Auto IV (Wikipedia).",
         "sources": ["https://www.forbes.com/sites/brianmazique/2026/11/12/gta-6-unlocks-at-midnight-on-november-19-but-millions-of-americans-can-start-playing-the-night-before/",
                     "https://en.wikipedia.org/wiki/Grand_Theft_Auto_IV"], "main": False},
    ],
    description="Fans found Jason and Lucia's in-game driver's licences: Jason, born 1 May 1996, is 30 and 6'3\"; "
                "Lucia, born 20 November 2000, is 26, 5'3\", with a licence from Liberty City. She turned 26 the day "
                "after GTA 6 came out. Rockstar hasn't announced these numbers.\nSources: UNILAD, LAFM, Pulptastic.",
    hashtags=["#GTA6", "#LuciaCaminos", "#JasonDuval"],
)

S["gta6-four-heroes"] = dict(
    title="GTA 6 nearly had four heroes. Rockstar explains why not",
    thumb_text="FOUR HEROES?",
    hook_card="4 HEROES, NOT 2?",
    cover_lines=["4 HEROES INSTEAD", "OF JASON + LUCIA?", "ROCKSTAR EXPLAINS"],
    cover_frame={"image": "img7", "zone": "lower"},   # Jason_Duval_02: Jason close-up (27 Nov preview; E6 still cover)
    experiment="E5-older-gta+E6-still-cover",
    beats=[
        ("Rockstar thought about giving GTA 6 four main characters, not two.", "OFFICIAL:vi_Lucia_Caminos_12", None,
         "curious"),
        ("Remember, GTA 5 let you switch between three: Michael, Franklin and Trevor.", "OFFICIAL:v_c670974867",
         "GTA 5: 3 HEROES", None),
        ("Rockstar North's Rob Nelson told IGN what they asked themselves after GTA 5.", "CLIP:trailer_2_00346",
         None, None),
        ("How do we follow up three characters? Is it four characters now?", "CLIP:extended_look_07446",
         "QUOTE: ROCKSTAR", None),
        ("But, he said, we worried about diluting the amount of player time with each, and therefore player "
         "connection with those characters.", "CLIP:extended_look_07501", "QUOTE: ROCKSTAR", "serious"),
        ("So, in his words, we decided to step in this direction of two characters in a relationship.",
         "OFFICIAL:vi_Jason_and_Lucia_13", "2 HEROES, 1 COUPLE", None),
        ("Then the question became: how do you make players feel like, I love them both?",
         "OFFICIAL:vi_Jason_Duval_02", None, None),
        ("Nelson admits chemistry is a notoriously hard thing to do in any sort of entertainment.",
         "OFFICIAL:vi_Lucia_Caminos_09", None, None),
        ("Either the characters and the actors that embody them have it, or they don't. His verdict? I think "
         "we've got it.", "OFFICIAL:vi_Jason_and_Lucia_09", None, "amused"),
        ("So: two heroes in love, or four to switch between? Which side are you on?",
         "OFFICIAL:vi_Jason_and_Lucia_01", None, None),
    ],
    facts=[
        {"claim": "Dexerto (Dylan Horetski, 27 Aug 2026), from an IGN interview with Rockstar North co-studio head Rob "
                  "Nelson: 'After doing GTA 5, we talked about different ideas of' 'How do we follow up three "
                  "characters? Is it four characters now?' 'But we worried about diluting the amount of player time "
                  "with each and therefore player connection with those characters.' 'So we decided to step in this "
                  "direction of two characters in a relationship.' 'But then the question became: how do you make "
                  "players feel like, 'I love them both?'' 'Chemistry is a notoriously hard thing to do in any sort of "
                  "entertainment.' 'Either the characters and the actors that embody them have it - or they don't.' "
                  "'I think we've got it.' GTA 5 let players switch between Michael, Franklin and Trevor.",
         "sources": ["https://www.dexerto.com/gta/gta-6-almost-had-four-playable-characters-instead-of-just-jason-and-lucia-3403255/"],
         "main": True},
        {"claim": "GamesRadar+ (Ashley Bardhan, 27 Aug 2026) and PC Gamer (29 Aug 2026): Rockstar considered giving "
                  "GTA 6 four protagonists; Nelson to IGN: 'How do we follow up three characters? Is it four characters "
                  "now?'; 'we worried about diluting the amount of player time with each'.",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/rockstar-considered-giving-gta-6-four-protagonists-before-deciding-it-would-suck-we-worried-about-diluting-the-amount-of-player-time-with-each/",
                     "https://www.pcgamer.com/games/grand-theft-auto/rockstar-considered-having-four-protagonists-in-grand-theft-auto-6-but-the-studio-worried-about-diluting-the-amount-of-player-time-with-each-character/"],
         "main": True},
    ],
    description="Rockstar North's Rob Nelson told IGN the team asked 'Is it four characters now?' after GTA 5's three, "
                "but worried about 'diluting the amount of player time with each' - so GTA 6 has two, Jason and Lucia, "
                "in a relationship.\nSources: Dexerto, GamesRadar+, PC Gamer (IGN interview).",
    hashtags=["#GTA6", "#GTA5", "#Rockstar"],
)

S["gta6-snap-gun"] = dict(
    title="GTA 6's snap gun opens locked doors quietly. Get it",
    thumb_text="THE SNAP GUN",
    hook_card="NO MORE KICKING DOORS",
    cover_lines=["OPEN LOCKED DOORS", "WITHOUT THE ALARM?", "THE TOOL YOU NEED"],
    cover_frame={"image": "img3", "zone": "lower"},   # Jason_Duval_08: Jason in a cap with a pistol (27 Nov preview; E6 still cover)
    experiment="E6-still-cover",
    beats=[
        ("Tired of kicking doors open in GTA 6? There's a quieter way.", "CLIP:extended_look_10132", None,
         "curious"),
        ("It's called the snap gun. It makes picking locks faster and quieter.", "CLIP:extended_look_07238",
         "THE SNAP GUN", None),
        ("Here's how to get it. One: play the story through to Chapter 3.", "OFFICIAL:vi_Jason_Duval_08",
         "1. REACH CHAPTER 3", None),
        ("Two: finish the jewelry heist in the mission Dubious Provenance. Yasmani gives you the snap gun.",
         "CLIP:extended_look_07057", "2. DUBIOUS PROVENANCE", None),
        ("Three: equip it, walk up to a locked door, and choose Use snap gun.", "CLIP:extended_look_06860",
         "3. USE SNAP GUN", None),
        ("Then find the sweet spot with the left stick, and press the right trigger until the meter fills.",
         "CLIP:extended_look_02968", "STICK, THEN TRIGGER", None),
        ("Now the catch: the alarm is still active. Kicking open other doors, breaking display cases, or a store "
         "employee can still set it off.", "CLIP:extended_look_09166", "ALARM STILL ON", "serious"),
        ("The pro move: use it on the back door, get to the office, and you can disable the alarm altogether.",
         "CLIP:trailer_2_00996", "BACK DOOR -> OFFICE", "excited"),
        ("So: snap gun and stay quiet, or kick the door in? Pick a side.", "OFFICIAL:vi_Jason_and_Lucia_02", None,
         None),
    ],
    facts=[
        {"claim": "PC Gamer (Andrea Shearon, 18 Nov 2026), 'How to get a snap gun in GTA 6': the snap gun is 'a handy "
                  "little device that makes picking locks faster and quieter'; 'You get the snap gun from Yasmani in "
                  "Chapter 3 after completing the jewelry heist in the Dubious Provenance mission.' 'Approach a locked "
                  "door with the tool equipped, and the \"Use snap gun\" option will appear.' 'Use the left analogue "
                  "stick to find the lock's sweet spot, then press the right trigger until the meter fills.' 'While "
                  "the snap gun circumvents alarms, the alarm itself is still active. It may still be set off by "
                  "kicking open other doors, breaking display cases, or by a store employee.' Using it on an "
                  "establishment's back door gives access to the office to 'completely disable the alarm altogether'.",
         "sources": ["https://www.pcgamer.com/games/grand-theft-auto/gta-6-snap-gun/"], "main": True},
    ],
    description="How to get GTA 6's snap gun: reach Chapter 3, finish the jewelry heist in Dubious Provenance and "
                "Yasmani gives it to you. Equip it at a locked door, find the sweet spot with the left stick, then "
                "hold the right trigger. The alarm is still active - use the back door to reach the office and turn "
                "it off.\nSource: PC Gamer.",
    hashtags=["#GTA6", "#GTA6Tips", "#GTAVI"],
)

S["gta6-break-up"] = dict(
    title="GTA 6: can Jason and Lucia break up? Rockstar answers",
    thumb_text="CAN THEY BREAK UP?",
    hook_card="CAN THEY BREAK UP?",
    cover_lines=["CAN JASON AND LUCIA", "BREAK UP?", "ROCKSTAR ANSWERS"],
    cover_frame={"image": "img1", "zone": "lower"},   # Lucia_Caminos_06 (also beat 1): Lucia at a party, face above the logo (27 Nov preview; E6 still cover)
    experiment="E6-still-cover",
    beats=[
        ("Can Jason and Lucia actually break up in GTA 6?", "OFFICIAL:vi_Lucia_Caminos_06", None, "curious"),
        ("Even the gaming press can't agree. One headline says yes. Another says no.",
         "OFFICIAL:vi_Jason_and_Lucia_06", None, "amused"),
        ("Rockstar's Rob Nelson told Edge magazine: we start them wanting to be together.",
         "CLIP:extended_look_07446", "QUOTE: ROCKSTAR", None),
        ("And then: it's yours to keep or yours to lose.", "CLIP:trailer_2_00346", "QUOTE: ROCKSTAR", "serious"),
        ("GamesRadar says if you ignore one too many late-night phone calls from your partner, things may go awry.",
         "CLIP:extended_look_03894", "IGNORE THE CALLS?", None),
        ("But here's the twist. Nelson also told IGN: they will remain partners in crime.",
         "CLIP:launch_trailer_00026", "QUOTE: ROCKSTAR", "excited"),
        ("Whether they're romantically close or not doesn't change that. They will still work together.",
         "OFFICIAL:vi_Jason_and_Lucia_08", None, None),
        ("And whether you've nurtured the relationship or not will definitely have a bearing on how their story "
         "plays out.", "CLIP:extended_look_07899", "IT CHANGES THE STORY", None),
        ("So the romance is yours to keep or lose. But they stay partners in crime.", "CLIP:extended_look_10833",
         None, None),
        ("Would you keep Jason and Lucia together, or let it fall apart? Pick a side.",
         "OFFICIAL:vi_Jason_and_Lucia_13", None, None),
    ],
    facts=[
        {"claim": "GamesRadar+ (Kaan Serin, 1 Nov 2026), 'GTA 6 lets you break up Jason and Lucia if you want': Rockstar "
                  "North's Rob Nelson told Edge Magazine 'We start them wanting to be together' and 'it's yours to keep "
                  "or yours to lose'; the writer: they 'can become a romantic couple and then break up entirely' and "
                  "'ignore one too many late-night phone calls from your partner and things may go awry'.",
         "sources": ["https://gamesradar.com/games/grand-theft-auto/gta-6-lets-you-break-up-jason-and-lucia-if-you-want-and-we-can-thank-red-dead-redemption-2s-arthur-morgan-for-the-choice"],
         "main": True},
        {"claim": "GamesRadar+ (Ashley Bardhan, 27 Aug 2026), 'GTA 6 won't let you break up Lucia and Jason': Nelson to "
                  "IGN: 'They will remain partners in crime,' 'You will always have the benefit of working together and "
                  "having each other's back' 'whether they're romantically close or not doesn't change that. They will "
                  "still work together.' 'Whether you've nurtured the relationship or not will definitely have a "
                  "bearing on how their story plays out.' The writer: 'There's no way for them to break up, Rockstar "
                  "says.' TechRadar (28 Aug 2026), same IGN interview: 'It's not something that we want to foist upon "
                  "players.'",
         "sources": ["https://www.gamesradar.com/games/grand-theft-auto/gta-6-wont-let-you-break-up-lucia-and-jason-no-matter-how-poorly-you-treat-them-they-will-remain-partners-in-crime/",
                     "https://www.techradar.com/gaming/rockstar-says-if-you-want-gta-6s-romance-between-jason-and-lucia-to-flourish-you-have-to-nurture-it-but-its-completely-optional-its-not-something-that-we-want-to-foist-upon-players"],
         "main": True},
    ],
    description="Can Jason and Lucia break up in GTA 6? Rob Nelson told Edge the romance is 'yours to keep or yours "
                "to lose', and told IGN 'They will remain partners in crime' - and that nurturing the relationship "
                "'will definitely have a bearing on how their story plays out'.\nSources: GamesRadar+, TechRadar.",
    hashtags=["#GTA6", "#JasonAndLucia", "#GTAVI"],
)

S["gta6-patch-fix"] = dict(
    title="GTA 6's first update fixed the cops you couldn't lose",
    thumb_text="THE UPDATE FIXED IT",
    hook_card="COULDN'T LOSE THE COPS?",
    cover_lines=["STUCK WITH COPS", "ON YOUR TAIL?", "THE UPDATE FIXED IT"],
    cover_frame={"image": "img1", "zone": "lower"},   # Jason_Duval_01 (also beat 1): Jason with a pistol under palms, face above the logo (27 Nov preview: 07 put his eyes under the logo; E6 still cover)
    experiment="E6-still-cover",
    beats=[
        ("Couldn't lose the cops in GTA 6?", "OFFICIAL:vi_Jason_Duval_01", None, "curious"),
        ("It wasn't just you. It was a bug.", "CLIP:extended_look_09432", None, "amused"),
        ("On November the twenty-third, Rockstar released an update for PS5 and Xbox.", "CLIP:trailer_2_00452",
         "UPDATE 1.002.002", None),
        ("Its notes list a fix for players being unable to lose their wanted level.", "CLIP:extended_look_09166",
         "FIXED: WANTED LEVEL", None),
        ("It also fixed the game not autosaving correctly.", "CLIP:extended_look_07501", "FIXED: AUTOSAVE", None),
        ("And partners not handing over bags, so you couldn't sell them to fences.", "CLIP:extended_look_09994",
         "FIXED: LOOT BAGS", None),
        ("Plus several crashes, and weather that didn't change for long stretches.", "CLIP:extended_look_07446",
         "FIXED: CRASHES, WEATHER", None),
        ("It even fixed the deadlift bar in the gym.", "CLIP:extended_look_10387", "FIXED: DEADLIFT BAR", "amused"),
        ("It's small: about six hundred megabytes on PS5, and about one point six gigabytes on Xbox.",
         "CLIP:extended_look_09766", "PS5 604MB / XBOX 1.6GB", None),
        ("Some players still report problems, so keep your game updated.", "CLIP:extended_look_10037", None, None),
        ("So: did the cop bug get you, or did it pass you by? Pick a side.", "OFFICIAL:vi_Jason_and_Lucia_19",
         None, None),
    ],
    facts=[
        {"claim": "Beebom (Sagnik Adhikary, GTA 6 patch notes tracker, updated 23 Nov 2026): version 01.002.002, "
                  "November 23, 2026, PS5 603.8 MB, Xbox Series X|S 1.6 GB; notes: 'Fixed several issues that caused "
                  "the game to crash', 'Fixed an issue that resulted in the weather not changing for extended periods', "
                  "'Fixed an issue that resulted in the game not autosaving correctly', 'Fixed an issue that resulted "
                  "in the players being unable to lose their Wanted Level', 'Fixed an issue that resulted in the player "
                  "being unable to use the deadlift bar in the Gym', partners 'not handing over bags so that players "
                  "could sell them to fences'.",
         "sources": ["https://beebom.com/gta-6-patch-notes-updates-tracker/"], "main": True},
        {"claim": "Timesaver (updated 26 Nov 2026): 'The latest GTA 6 update is 1.002.002 on PS5 (1.0.2.2 on Xbox), "
                  "released November 23, 2026', with the same fixes, quoted from Rockstar Support's 'Grand Theft Auto "
                  "VI Launch Updates'; PS5 603.8 MB, Xbox about 1.6 GB; players on r/GTA6 still report some problems "
                  "(weather, autosave, a PS5 crash).",
         "sources": ["https://timesaver.gg/blog/gta-6-update-patch-notes"], "main": True},
    ],
    description="GTA 6 update 1.002.002 (23 Nov 2026, PS5 and Xbox) fixed players being unable to lose their Wanted "
                "Level, autosave, partners not handing over bags for fences, crashes, stuck weather and the gym's "
                "deadlift bar. About 604 MB on PS5, 1.6 GB on Xbox.\nSources: Beebom, Timesaver (Rockstar Support notes).",
    hashtags=["#GTA6", "#GTA6Update", "#GTAVI"],
)

S["gta6-trailer-songs"] = dict(
    title="GTA 6's trailers brought two old songs back to life",
    thumb_text="TWO OLD SONGS",
    hook_card="TWO OLD SONGS",
    cover_lines=["TWO 80s SONGS", "EXPLODED ON SPOTIFY", "THANKS TO THE TRAILERS"],
    cover_frame={"shot": "trailer_1_00084", "f": 0.3, "x": 0.5},   # Lucia in prison (R3: face)
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
    cover_frame={"shot": "trailer_1_00728", "f": 0.5, "x": 0.3},   # Lucia leaning over Jason (23 Nov: 07899 went to real-cheetah) (R3: face)
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
    # 23 Nov 2026 (cost): 10 of 10 morning scripts on 22-23 Nov were held by the paid script check, mostly for one
    # word stronger than the source ("never" for "still hasn't", "the biggest hint", a year not in the sources).
    # Catch those here for free: an absolute word or a year in the narration that no fact claim contains.
    import re as _re
    _abs = ("never", "biggest", "only", "always", "every", "all-time", "highest", "most", "best", "record",
            "nobody", "no one", "confirmed", "official", "joke")      # "first"/"ever" were mostly harmless ordinals
    for t in todo & set(out):
        ftxt = " ".join(f["claim"] for f in out[t]["facts"]).lower()
        for sc in out[t]["scenes"]:
            low = sc["narration"].lower()
            for w in _abs:
                if _re.search(rf"\b{_re.escape(w)}\b", low) and not _re.search(rf"\b{_re.escape(w)}\b", ftxt):
                    print(f"  warning {t} {sc['id']}: '{w}' is not in any fact claim (make sure the source says it, or reword)")
            for y in _re.findall(r"\b(19\d\d|20\d\d)\b", sc["narration"]):
                if y not in ftxt:
                    print(f"  warning {t} {sc['id']}: year {y} is not in any fact claim")
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
