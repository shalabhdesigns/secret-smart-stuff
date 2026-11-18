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
    beats=[
        ("In India, GTA 6 costs exactly twice what GTA 5 did.", "CLIP:trailer_2_00416", "2X", "surprised"),
        ("When GTA 5 launched here in 2013, it cost 2,999 rupees.", "OFFICIAL:v_c670974867", "₹2,999 IN 2013", None),
        ("GTA 6's standard edition is 5,999.", "CLIP:trailer_2_00232", "₹5,999", None),
        ("And the Ultimate Edition goes all the way up to 7,499.", "CLIP:extended_look_15485", "₹7,499 ULTIMATE",
         None),
        ("That sounds brutal, until you look at America.", "CLIP:trailer_2_00346", None, None),
        ("Over there, GTA 5 cost sixty dollars, and GTA 6 costs eighty.", "CLIP:trailer_1_00325",
         "$59.99 → $79.99", None),
        ("That's only about a third more, not double.", "CLIP:extended_look_09166", "+33%", None),
        ("So India's price really did jump much more than America's.", "CLIP:extended_look_10833", None, None),
        ("But here's the twist: eighty dollars is roughly 6,900 rupees.", "CLIP:extended_look_12327",
         "$80 ≈ ₹6,900", "curious"),
        ("So even after doubling, Indian players still pay about 900 rupees less than Americans.",
         "CLIP:extended_look_15698", None, None),
        ("Would you pay 5,999 on day one, or wait for a sale?", "CLIP:trailer_2_00795", None, None),
    ],
    facts=[
        {"claim": "GTA V launched in India at Rs 2,999 in 2013 (distributor E-xpress Interactive).",
         "sources": ["https://www.mcvuk.com/update-grand-theft-auto-5-price-to-remain-rs-2999/"], "main": True},
        {"claim": "GTA 6 in India: Rs 5,999 standard, Rs 7,499 Ultimate; US $79.99; $80 is about Rs 6,900.",
         "sources": ["https://www.mysmartprice.com/gear/gaming/gaming-news/gta-6-pre-orders-go-live-in-india-standard-edition-costs-rs-5999-ultimate-edition-priced-at-rs-7499/"],
         "main": True},
        {"claim": "GTA V launched at $59.99 in the US; GTA 6 is $79.99.",
         "sources": ["https://hothardware.com/news/gta-6-launch-80-single-player-title-rockstar-reveals"], "main": False},
    ],
    description="GTA 5 was Rs 2,999 in 2013. GTA 6 is Rs 5,999. In dollars, India still pays less than America.\n"
                "Sources: MCV (2013), MySmartPrice (2026).",
    hashtags=["#GTA6", "#GTA6India", "#GrandTheftAuto"],
)

S["gta6-leak-war"] = dict(
    title="GTA 6: Rockstar's war on the leakers",
    thumb_text="STOLEN GAME",
    hook_card="STOLEN IN 2022",
    beats=[
        ("Someone stole GTA 6 years before it came out.", "CLIP:trailer_2_00996", None, "serious"),
        ("In September 2022, a hacker posted early development footage of the game online.",
         "CLIP:extended_look_02226", "SEPT 2022", None),
        ("It was a huge leak, and the hacker was caught.",
         "CLIP:trailer_2_00452", None, None),
        ("In 2023, a UK court ordered the teenager behind it to be held in a secure hospital, with no end date.",
         "CLIP:trailer_2_00498", "UK COURT, 2023", None),
        ("But the leaks didn't stop there.", "CLIP:trailer_2_01188", None, "short pause"),
        ("In December 2023, GTA 6's very first trailer leaked online before its premiere.",
         "CLIP:trailer_1_00300", "DEC 2023", None),
        ("So Rockstar just released it early, hours ahead of plan.", "CLIP:trailer_1_00026", None, None),
        ("Then this August, new clips started showing up online.", "CLIP:extended_look_02502", "AUG 2026", None),
        ("This time, Take-Two went to court.", "CLIP:extended_look_12920", None, "serious"),
        ("It won orders telling Microsoft, which owns GitHub, and Discord to help identify who posted them.",
         "CLIP:extended_look_12327", "MICROSOFT + DISCORD", None),
        ("From a stolen build to court orders, Rockstar has been fighting leakers right up to launch day.",
         "CLIP:launch_trailer_00685", None, None),
        ("Did you watch the leaks, or did you wait for the real thing?", "CLIP:trailer_2_00961", None, None),
    ],
    facts=[
        {"claim": "Sept 2022: a hacker leaked early GTA 6 development footage; in Dec 2023 a UK court gave the teenager "
                  "behind it an indefinite hospital order.",
         "sources": ["https://www.techradar.com/gaming/gta-6-hacker-who-intended-to-return-to-cyber-crime-as-soon-as-possible-sentenced-to-an-indefinite-hospital-order"],
         "main": True},
        {"claim": "Dec 2023: GTA 6 trailer 1 leaked online, so Rockstar released it early.",
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
    thumb_text="GTA TOKYO?",
    hook_card="GTA TOKYO?",
    beats=[
        ("GTA almost left America, and one city came really close.", "CLIP:trailer_1_00325", None, "curious"),
        ("Obbe Vermeij, a former technical director at Rockstar North, says a GTA set in Tokyo \"almost actually "
         "happened.\"", "CLIP:extended_look_12327", "QUOTE: OBBE VERMEIJ", None),
        ("And Tokyo wasn't the only city on the table.", "CLIP:trailer_1_00300", None, None),
        ("He says Rio, Moscow and Istanbul were considered too.", "CLIP:extended_look_15698",
         "RIO, MOSCOW, ISTANBUL", None),
        ("So why does every numbered GTA still end up in America?", "CLIP:trailer_2_00346", None, None),
        ("Rockstar co-founder Dan Houser has a simple answer.", "CLIP:extended_look_07446", None, None),
        ("He says other countries may have great cities, \"but they're not American cities.\"",
         "CLIP:trailer_1_00026", "QUOTE: DAN HOUSER", None),
        ("For him, GTA needs America's guns and its larger-than-life characters.", "CLIP:trailer_1_00248", None,
         None),
        ("There's a practical problem too.", "CLIP:extended_look_12920", None, None),
        ("Vermeij says a whole new country is \"just not realistic\" when there's only a GTA every twelve years.",
         "CLIP:trailer_1_00398", "QUOTE: OBBE VERMEIJ", None),
        ("So after thirteen years, GTA 6 is going back to a city fans already know and love: Vice City.",
         "CLIP:extended_look_10450", None, None),
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
    thumb_text="REAL PLACES",
    hook_card="VISIT GTA 6?",
    beats=[
        ("You can actually visit the places GTA 6 is based on.", "CLIP:trailer_1_00356", None, "excited"),
        ("The game is set in Leonida, Rockstar's version of Florida.", "CLIP:trailer_1_00217", None, None),
        ("And its big city, Vice City, is inspired by Miami.", "CLIP:extended_look_07446", None, None),
        ("Rockstar says the Leonida Keys have \"some of the most beautiful and dangerous waters in all of "
         "America.\"", "CLIP:trailer_2_00188", "QUOTE: ROCKSTAR", None),
        ("Most outlets compare them to the real Florida Keys, the chain of islands south of Miami.",
         "CLIP:launch_trailer_00026", "FLORIDA KEYS", None),
        ("Then there's Grassrivers, where Rockstar promises \"deadlier predators and weirder discoveries.\"",
         "CLIP:trailer_1_00183", "QUOTE: ROCKSTAR", None),
        ("It looks a lot like the Everglades, the huge wetland where real airboats skim across the grass.",
         "CLIP:extended_look_10298", "EVERGLADES", None),
        ("And Mount Kalaga, Rockstar says, offers \"prime hunting, fishing, and off-road trails.\"",
         "CLIP:extended_look_04645", "QUOTE: ROCKSTAR", None),
        ("Florida doesn't really have mountains, so that one is more Rockstar than reality.",
         "CLIP:extended_look_11148", None, "laughs softly"),
        ("Rockstar hasn't named the real places itself, but the resemblance is hard to miss.",
         "CLIP:trailer_2_00081", None, None),
        ("Which one would you visit first: the Keys, the Everglades, or Miami?", "CLIP:extended_look_10489", None,
         None),
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


def build(topic: str, v: dict) -> dict:
    images, scenes = {}, []
    for i, (text, shot, callout, delivery) in enumerate(v["beats"], 1):
        key = next((k for k, s in images.items() if s == shot), None) or f"img{len(images) + 1}"
        images[key] = shot
        scenes.append({"id": f"b{i}", "narration": text, "image": key, "delivery": delivery, "focus": None,
                       "motion": "push" if i % 3 else "drift", "transition": "cut", "callout": callout, "pop": None,
                       "arrow": None, "card_text": None, "tone": "normal", "markers": None})
    return {"viable": True, "title": v["title"], "thumb_text": v["thumb_text"], "hook_card": v["hook_card"],
            "hooks": [v["beats"][0][0]], "chosen_hook": 0, "images": images, "scenes": scenes,
            "facts": v["facts"], "description": v["description"], "hashtags": v["hashtags"],
            "affiliate_product": None, "written_by": "Claude in session (verified)"}


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
