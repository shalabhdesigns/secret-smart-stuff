"""GTA 6 launch week, footage edition (owner, 16 Nov 2026): 5 videos a day, Rockstar's own trailer footage,
story-first scripts. Built into config/daily_queue.json."""
import json
from pathlib import Path
import sys

sys.path.insert(0, "/home/claude/shorts-system")

RULES = (
    "GTA 6 SERIES RULES (owner, 16 Nov 2026 - these win over everything else):\n"
    "STORY FIRST. The narrative is the most important thing. Structure: (1) HOOK in the first second - a "
    "surprising claim, a mystery or a 'wait, what?' moment, never a slow intro; (2) STAKES - why the viewer should "
    "care; (3) BUILD - 2-3 escalating reveals, each one more surprising; (4) PAYOFF - the satisfying answer or twist "
    "that makes people say 'wow'; (5) one short comment question people WANT to answer; (6) a last line that flows "
    "straight back into the first (loop). Every line must earn its place: no filler, no 'using official data'. 1-2 "
    "light witty lines. Speak like a friend telling a great story, not a news report.\n"
    "FOOTAGE: every beat shows Rockstar's OFFICIAL GTA VI footage. In \"images\", each value is exactly "
    "'CLIP:<shot_id>' from the SHOT LIST below (real trailer footage, full screen). Use 'OFFICIAL:<id>' (screenshot "
    "catalogue) only for GTA 5 (the cover v_c670974867, Los Santos v_24ba6644de / v_fdac18d437 / v_07edb091bb, "
    "the map v_3360902d78) or when no shot fits, and then ONLY for one short beat (max 2 s, 3-5 words). NEVER open on a "
    "still: beat 1 AND the last beat must be the same striking CLIP footage (the loop). No generated pictures. Pick the shot that matches what each line "
    "says. Beat 1 = the most striking, high-action or most beautiful shot that fits the hook. Use 8-11 different "
    "shots: a new shot every beat (1.5-3 s each), never the same shot twice in a row. Shots may be reused from "
    "earlier videos, but each video must feel entirely different.\n"
    "HOW FOOTAGE MATCHES WORDS (like the best GTA Shorts): a line about a person shows that person (Jason, Lucia), "
    "a line about a place shows that place, an action shows that action. Abstract lines (prices, sizes, dates, "
    "percentages) are carried by a short on-screen 'callout' over striking, on-mood footage (Vice City, action, "
    "the leads) - that is correct here, not a mismatch.\n"
    "FOR THE REVIEWERS: the game IS the topic, so Rockstar's official footage, characters and GTA V cover art are "
    "the approved pictures here (commentary on the game), not 'a brand or logo as the subject'.\n"
    "FACTS: every number, date and claim comes from the sources; rumours and leaks are never stated as fact "
    "('reportedly', 'Rockstar hasn't said'). Say WHO claims a thing ('fans spotted', 'PC Gamer reported') when "
    "Rockstar hasn't confirmed it. If no source gives a reason, say so plainly and make the payoff a surprising "
    "SOURCED FACT instead - never imply a link or reason the sources don't make. The TITLE must not assert "
    "anything unconfirmed (a question or 'fans say' is fine). No story spoilers beyond what Rockstar's trailers show. Never "
    "pretend the footage is our gameplay.\n"
    "Say 'GTA 6' in beat 1 or 2 and in the title. No markers or arrows. Numbers go in 'callout' (short).\n"
    "Length 30-38 seconds: 56-66 words, 10-12 beats of 4-7 words; beat 1 is at most 7 words (spoken prices count long: '$79.99' takes 2 s).\n"
    "LOOP: the last line is a lead-in that flows back into beat 1; never 'So next time someone asks you'.\n"
    "VERIFIED BRIEF: the angle below was researched and checked by Claude before writing (16 Nov 2026): use ITS "
    "facts, ITS cautious wording and ITS sources first; add nothing you cannot source.\n"
    "LOOK AND FEEL: every video in this series must feel different - follow this video's own FORMAT (structure, "
    "pace, opening style) and choose FRESH shots; never copy another video's structure or opening.\n"
    "SHOT-WORD MATCH: try hard to make every shot show what that line says (a person, place, object or action named "
    "in the line should be on screen). Search the SHOT LIST descriptions for the best match before settling.\n"
    "PRE-FLIGHT CHECK - before you answer, test your own script against what the reviewers will check, and fix it "
    "first: (1) beat 1 is a question or shock in <=7 words over striking CLIP footage; (2) no line repeats an earlier "
    "line's point; (3) the payoff answers the hook with a SOURCED fact; (4) every claim Rockstar hasn't confirmed "
    "says who claims it; (5) each person/place/action line's shot shows that person/place/action (read the SHOT "
    "LIST description); (6) no shot is used in two beats in a row, and no 'avoid' shot is used; (7) 56-66 words; "
    "(8) the last line + beat 1 read as one sentence; (9) the title asserts nothing unconfirmed.\n")
CRITIC = ("\nGTA 6 series: the footage is OFFICIAL Rockstar GTA VI trailer footage (and GTA V screenshots) and that is "
          "required: never mark it down as game art, logos or 'not a real photo'. Judge the STORY hardest: BLOCKING if "
          "the first second has no hook, if the middle has filler, if there is no payoff, if a person/place/action "
          "line shows something clearly different (abstract lines like prices or sizes are carried by the callout "
          "over on-mood footage: that is fine, never BLOCKING), if a rumour is stated as fact, or if a price, date or size is not in the sources.")
# 18 Nov 2026 (owner): "the voiceovers feel unnatural, the sentence construction is bad, the script is confusing,
# the dialogues do not convey what they want to say ... do not shy away from making the videos longer."
# Story format: natural spoken sentences, 45-70 s, no loop lead-in (shorts/prompts.py STORY_*).
RULES_STORY = (
    "GTA 6 SERIES - STORY FORMAT (owner, 18 Nov 2026; these win over everything else):\n"
    "The owner's verdict on the old scripts: unnatural, badly built sentences, confusing, lines that don't say what "
    "they mean, no burning curiosity. So: tell it like a real person telling a friend the most interesting thing "
    "they heard today. Natural complete sentences, clear on one listen, real personality, a hook that makes people "
    "NEED the answer, reveals that escalate, a payoff that makes them say 'wow', then a comment question.\n"
    "BAD (never write like this): 'Game Boy Color GTA 2 added two.' / 'Power Up Gaming: first fully written, voiced "
    "lead.' / 'Twenty-nine years. Quite the loading screen.' / 'Now you know the answer to...'\n"
    "GOOD (style examples only - every video needs its OWN opening; never copy these): 'Go back to 1997, the very first Grand Theft Auto. At the start, you picked who to play as, and four of "
    "them were women.' / 'So what's actually new about Lucia? She's the first woman who leads a GTA story.'\n"
    "FOOTAGE: every beat shows Rockstar's OFFICIAL GTA VI footage: in \"images\", each value is exactly "
    "'CLIP:<shot_id>' from the SHOT LIST below. Use 'OFFICIAL:<id>' (screenshot catalogue) only for GTA 5 (the cover "
    "v_c670974867, Los Santos v_24ba6644de / v_fdac18d437 / v_07edb091bb, the map v_3360902d78) when the line is about "
    "GTA 5, for one beat. Open on striking footage that fits the hook. A NEW shot every beat (10-20 different "
    "shots); a shot may come back only as a deliberate callback. Never use a shot marked avoid.\n"
    "SHOTS MATCH WORDS: a line about a person shows that person (Jason, Lucia), a place shows that place, an action "
    "shows that action. Read the SHOT LIST descriptions and pick the closest. Abstract lines (prices, dates, sizes) "
    "show on-mood footage with the number as a short callout.\n"
    "REAL PEOPLE: when the brief quotes a Rockstar or Take-Two person, use their exact words, say who they are, put "
    "'QUOTE: <NAME>, <COMPANY>' in that beat's callout, and show a PLACE on that beat (never a character's face, so "
    "no one thinks the character is the real person). Never invent or reword a quote.\n"
    "FOR THE REVIEWERS: the game IS the topic, so Rockstar's official footage and characters are the approved "
    "pictures (commentary on the game), not 'a brand or logo as the subject'.\n"
    "FACTS: every number, date and claim comes from the verified brief or your sources. Rumours are never facts: say "
    "plainly who claims it ('fans think', 'one report says'). If a fact needs heavy hedging, drop it. The TITLE "
    "asserts nothing unconfirmed. No story spoilers beyond Rockstar's trailers. Never pretend the footage is our "
    "gameplay.\n"
    "LENGTH: 110-170 words (about 45-70 seconds); as long as the story needs, never padded.\n"
    "VERIFIED BRIEF: the angle below was researched and checked: use ITS facts, ITS wording and ITS sources first.\n"
    "LOOK AND FEEL: follow this video's own FORMAT (structure, pace, opening style); each video must feel different.\n")
CRITIC_STORY = ("\nGTA 6 series: the footage is OFFICIAL Rockstar GTA VI trailer footage (and GTA V screenshots) and "
                "that is required: never mark it down as game art or logos. Judge the SCRIPT hardest: BLOCKING if any "
                "sentence is unclear, unnatural or a fragment, if the hook creates no real curiosity, if the build "
                "doesn't escalate or the payoff doesn't land, if a person/place/action line shows something clearly "
                "different, or if a rumour is stated as fact.")

COVER = ("The words are the QUESTION or the mystery only, 2-5 words, and never give away the answer. Keep them off "
         "faces.")

# id, title, story angle (facts to use; the writer still sources every claim)
V = {
 "gta6-cheaper-than-gta5": ("Is GTA 6 at $80 really cheaper than GTA 5?",
  "HOOK: 'Everyone's angry GTA 6 costs $80. But it might be the cheapest GTA ever.' Facts: GTA 6 standard $79.99 "
  "(Rockstar/Fortune, Jun 2026); GTA V launched at $59.99 in Sept 2013; adjusted for US inflation (BLS CPI) "
  "$59.99 in 2013 is about $82-85 today, so GTA 6 costs about the same or less in real money. Build: GTA 5 money "
  "shot (official GTA 5 cover OFFICIAL:v_c670974867 when its 2013 price is said), then the inflation reveal. "
  "Payoff: the price only feels higher. Witty line allowed. CTA: 'Fair price or too much?' Compare ONLY GTA 6 "
  "and GTA 5."),
 "gta6-trailer-record": ("The GTA 6 trailer that broke YouTube",
  "HOOK: 'One video game trailer did something no movie trailer, music video or game had ever done.' Facts: GTA "
  "6's first trailer (Dec 2023) got about 90 million YouTube views in 24 hours, the most-viewed non-music video "
  "debut in that time, and earned Guinness World Records (Push Square, PC Gamer, Guinness). Build: it was "
  "released early because it leaked; Tom Petty's 'Love Is a Long Road' in it shot back up the charts (only if "
  "sourced). Payoff: the hype is bigger than any film. CTA: 'How many times did you watch it?'"),
 "gta6-not-on-pc": ("Why GTA 6 isn't on PC yet",
  "VERIFIED. HOOK: 'GTA 6 launches Thursday - but not on PC.' Facts: launches 19 Nov 2026 on PS5 and Xbox Series X|S only, no PC date announced (Rockstar). Take-Two CEO Strauss Zelnick told Bloomberg (May 2026): 'Rockstar always starts on console' because 'you're judged by serving the core' - the core must be 'served first and best' (FRVR, 5 May 2026, https://frvr.com/blog/news/gta-6-boss-defends-late-pc-release-console-must-be-served-first-and-best/). History: GTA V console Sept 2013 -> PC April 2015 (~19 months); Red Dead Redemption 2 console Oct 2018 -> PC Nov 2019 (~13 months). Payoff: if history repeats, PC players could wait a year or more - that is a pattern, NOT an announcement: say 'if history repeats'. CTA: 'Would you wait for PC?' Shots: Jason driving, Vice City night, a waiting/frustrated person."),
 "gta6-florida-man": ("Fans found the real videos behind GTA 6's craziest scenes",
  "HOOK: 'Some of GTA 6's craziest moments look a lot like real Florida videos.' Facts: outlets (PC Gamer, Know "
  "Your Meme, Miami New Times, Creative Bloq) and fans matched scenes in GTA 6's first trailer (Dec 2023) to real "
  "viral Florida clips - e.g. the alligator walking into a convenience store, the woman dancing on a car roof, "
  "the man pulling an alligator out of a backyard pool. ALWAYS say 'fans matched' / 'outlets spotted' - Rockstar "
  "hasn't confirmed which clips inspired it. Use ONLY examples the sources list, and show the matching trailer "
  "shot for each (the store alligator CCTV shot, the car-roof dancer, the pool alligator post). Payoff: Leonida is "
  "Rockstar's Florida, and real life keeps writing its jokes. CTA: 'Craziest Florida story you know?'"),
 "gta6-13-years": ("GTA 6 took 13 years. Here's what happened",
  "VERIFIED. HOOK: 'GTA 5 came out in 2013. GTA 6? Thursday.' Facts: GTA V launched 17 Sept 2013. GTA 6 was first targeted for 2025 (trailer 1, Dec 2023), delayed to 26 May 2026 (Rockstar, May 2025), then to 19 Nov 2026 (Rockstar, 6 Nov 2025) to 'finish the game with the level of polish you have come to expect' (Tom's Guide). In between: Red Dead Redemption 2 (Oct 2018) and years of GTA Online updates (only as sources state). Never use any budget figure. Payoff (arithmetic, fine to say): a 10-year-old who played GTA 5 at launch is 23 now. CTA: 'How old were you when GTA 5 came out?'"),
 "gta6-ps5-space": ("Will GTA 6 even fit on your PS5?",
  "VERIFIED. HOOK: 'Your PS5 might not have room for GTA 6.' Facts: Rockstar confirmed GTA 6 is 212 GB and opened pre-loading early for digital orders (GamesRadar, https://gamesradar.com/games/grand-theft-auto/rockstar-confirms-gta-6-is-212gb-pre-loading-opens-earlier-than-previously-announced-for-digital-orders). The original 825 GB PS5 has about 667 GB usable (GamesRadar). Maths (fine to say): 212 GB is about a third of that. Do NOT quote a PS5 Slim figure (sources disagree). Payoff + advice: check free space now; delete old games or add an M.2 SSD (general advice). Witty line allowed. CTA: 'What are you deleting?'"),
 "gta6-lucia": ("Lucia is the GTA hero we waited 29 years for",
  "VERIFIED - CAREFUL WORDING. HOOK: 'The first GTA let you play as a woman. Then it took 29 years.' Facts: GTA 1 (1997) let you pick from four female characters (Power Up Gaming, 30 Jun 2026, https://powerupgaming.co.uk/2026/06/30/a-brief-history-of-female-protagonists-in-grand-theft-auto/); every main GTA story since then starred a man (GTA Online characters are custom and silent). Lucia Caminos is one of GTA 6's two leads with Jason Duval (Rockstar); Power Up Gaming calls her the first female character to get the same depth as the male leads. NEVER say she is 'the first female protagonist' (that's wrong). Trailer story only: Lucia in prison in trailer 1, the couple as partners in crime. Payoff: GTA's first real duo story. CTA: 'Jason or Lucia - who are you playing first?' Use Lucia shots (prison jumpsuit, prison yard, car, Jason and Lucia). Use at least 7 different shots across the beats (17 Nov: a draft used 5 shots for 10 beats and felt repetitive)."),
 "gta6-ultimate-worth": ("Is the $100 GTA 6 Ultimate Edition worth it?",
  "VERIFIED. HOOK: 'Rockstar wants $20 more for GTA 6. Here's what it buys.' Facts (PC Gamer, https://pcgamer.com/games/grand-theft-auto/gta-6-pre-order-editions-standard-ultimate/): Standard $79.99, Ultimate $99.99. Ultimate adds cars and boats (the '95 Grotti Cheetah, a Shitzu Squalo boat, a '67 Vapid Dominator buggy and garage, Jason's safehouse vehicles), revolvers and weapon variants, outfits, and extra shops and activities (a tattoo parlour, a hair salon, Rideout Customs, a classic car collection). The Vintage Vice City pre-order pack (outfits, a '55 Vapid Stanier, a weapon pattern) comes with BOTH editions. Build: list the best 3 extras, escalating. Payoff (opinion, label it): it's all extras - none of it is extra story. Do NOT say when, where or how the extras unlock in the game (no source says) - only WHAT is in the pack. Neutral, no buying advice. CTA: 'Standard or Ultimate? Tell me why.' Shots: cars, boat, Vice City streets, Jason and Lucia; OFFICIAL Ultimate Edition screenshots (Cheetah, Squalo, tattoo parlour) are allowed for 1 beat each (max 2 s)."),
 "gta6-extended-look": ("27 minutes of GTA 6 gameplay: what nobody noticed",
  "VERIFIED. HOOK: 'Rockstar premiered 27 minutes of GTA 6 on Netflix.' Facts: 'An Extended Look' premiered on Netflix on 27 Aug 2026 (GTA Boom, Esquire India). Details reported by GamingBolt (29 Aug 2026, https://gamingbolt.com/gta-6-25-details-hidden-in-the-27-minute-gameplay-showcase): a six-star wanted system whose icons show what police know (how many suspects, clothes, car); you can switch from Jason driving to Lucia shooting mid-chase; scuba diving with fish and manta rays; shooting a cop car's tires can flip it; torching the wanted car and escaping in a plain van; a working TV in the apartment. Pick the 3-4 most surprising, escalating to the best. Show the matching Extended Look shots (police chase, car swap, underwater, apartment). CTA: 'Which one are you trying first?'"),
 "gta6-leak-war": ("Rockstar's war on GTA 6 leakers",
  "VERIFIED - CAREFUL WORDING. HOOK: 'Someone stole GTA 6 three years before it came out.' Facts: in Sept 2022 a hacker leaked early development footage of GTA 6; in Dec 2023 a UK court gave the teenager behind it an indefinite hospital order (TechRadar, https://www.techradar.com/gaming/gta-6-hacker-who-intended-to-return-to-cyber-crime-as-soon-as-possible-sentenced-to-an-indefinite-hospital-order) - NO names, say 'the hacker was caught'. Dec 2023: trailer 1 leaked online, so Rockstar released it early (VGC, https://www.videogameschronicle.com/news/the-gta-6-trailer-has-allegedly-leaked-online/). Aug 2026: new GTA 6 clips leaked; Take-Two won court orders telling Microsoft (owner of GitHub) and Discord to help identify the accounts (AFP via Khaleej Times, 23 Aug 2026, https://www.khaleejtimes.com/entertainment/gaming/gta-6-publisher-subpoenas-bid-to-unmask-leaks). NEVER show or describe leaked footage; never say why the leaker did it. Payoff: from a stolen build to court orders, right up to launch day. CTA: 'Did you watch the leaks?' Shots: night, police, tense chase shots; no weapons pointed at people."),
 "gta6-unlock-time": ("GTA 6 is already unlocked in these countries",
  "VERIFIED. Publishes 18 Nov 17:00 UTC. HOOK: 'Right now, people in New Zealand are already playing GTA 6.' Facts: Rockstar says GTA 6 releases at 'midnight local time on November 19, 2026, in all regions' (Forbes, 12 Nov 2026, https://www.forbes.com/sites/brianmazique/2026/11/12/gta-6-unlocks-at-midnight-on-november-19-but-millions-of-americans-can-start-playing-the-night-before/). PlayStation Store times (GTA Boom, https://www.gtaboom.com/gta-6-release-times-when-it-unlocks-in-your-region-and-how-to-play-early-da2c): New Zealand first (11:00 UTC 18 Nov), then Sydney (13:00 UTC), Japan (15:00 UTC), India midnight IST (18:30 UTC 18 Nov), UK midnight (00:00 UTC 19 Nov), US Eastern midnight - and US Pacific gets it at 9 pm on 18 Nov (Forbes). Say 'on PlayStation' for the country list (Xbox hasn't published a country schedule). Payoff: the US West Coast plays the night before. CTA: 'Comment your time zone.'"),
 "gta6-heat-vice-city": ("Why an NBA team becomes 'Vice City' tonight",
  "VERIFIED. Publishes 18 Nov 14:00 UTC (morning in the US). HOOK: 'Tonight a real NBA team stops being Miami.' Facts: on 18 Nov 2026, the night before GTA 6 launches, the Miami HEAT host the Milwaukee Bucks at Kaseya Center as 'Vice City' - 'A Night in Vice City', tip-off 7 pm ET, with Rockstar (GTA Boom, 4 Oct 2026, https://www.gtaboom.com/gta-6s-miami-heat-vice-city-night-now-has-a-tip-time-a-trailer-and-a-giannis-twist-841d; GamingBolt). A special Vice City court. Uniforms by Travis Scott's Cactus Jack, Nike and GTA VI: black jersey, 'Vice City' in pink script, and a row of six pink stars that Hypebeast says likely nods to the six-star wanted level (Hypebeast, 8 Nov 2026, https://hypebeast.com/?post=6812970). No player names or faces. Payoff: a real city wears the game's colours. CTA: 'Would you buy the jersey?' Shots: Vice City night, neon, beach, skyline."),
 "gta6-vice-city-research": ("Rockstar spent 11 years studying Miami for GTA 6",
  "VERIFIED. HOOK: 'Rockstar started studying Miami for GTA 6 in 2015.' Facts (The Guardian, 11 Nov 2026, as reported by GTA Boom https://www.gtaboom.com/how-rockstar-spent-a-decade-and-almost-5000-people-to-create-vice-city-for-gta-6-cd18 and Notebookcheck https://www.notebookcheck.net/GTA-6-Guardian-preview-offers-a-look-at-the-making-of-Vice-City.1448174.0.html): the first research trips to Miami were in 2015; Rockstar North's Rob Nelson rode along with police through South Beach; the team went to bars in the Florida Keys and nightclubs; Nelson: 'We're always semi-undercover'; the team is almost 5,000 people (say 'reportedly'). Rockstar's method: the place comes first, then the story and characters grow from it. Payoff: every street in Vice City started as a real night out. CTA: 'Which real place should Rockstar study next?' Shots: South Beach, police cars, Keys/boats, nightclub neon."),
 "gta6-no-disc": ("Why the GTA 6 box has no disc inside",
  "VERIFIED - CAREFUL WORDING. HOOK: 'You buy GTA 6 in a shop, open the box... no disc.' Facts: the physical box holds a download code, not a disc (Fortune, 25 Jun 2026). Take-Two CEO Strauss Zelnick: 'Our business is well over 90% digitally distributed'; discs 'don't really make sense for the consumer' in some cases, 'especially if it's a big game' (Aug 2026 investor Q&A, Outlook Respawn https://respawn.outlookindia.com/gaming/gaming-news/gta-6-digital-only-launch-take-two-ceo-defends-no-physical-disc; Analytics Insight). Take-Two's digital channels made 98% of revenue last quarter (same source). The game is 212 GB (Rockstar, GamesRadar). Zelnick later said any disc decision is up to Rockstar (Beebom, 10 Nov 2026). Do NOT say it's to stop leaks; do NOT invent disc-capacity reasons. Payoff: the box is basically a very expensive key. CTA: 'Disc or digital - which do you buy?'"),
 "gta6-map-vs-florida": ("GTA 6 rebuilt Florida - without Disney World",
  "VERIFIED - CAREFUL WORDING. HOOK: 'GTA 6 rebuilt Florida... but it's missing Disney World.' Facts: Leonida is Rockstar's Florida, Vice City its Miami (Rockstar). Rockstar North's Rob Nelson said Vice City is 'twice the size of Los Santos' (Trois Couleurs, via Beebom 23 Sept 2026, https://beebom.com/gta-6-vice-city-is-two-times-bigger-than-gta-5-los-santos/amp/). Asked about Orlando's theme parks and the Space Coast, Rockstar's Paul MacPherson told Game Informer: 'While we may not have those exact locations, everything we have is geared to getting that full Florida experience' (GTA Boom 30 Sept 2026, https://www.gtaboom.com/these-are-the-famous-florida-landmarks-gta-6-is-leaving-out-8a8d; Kotaku). So: say Rockstar suggested there's no Disney World, Universal, SeaWorld or NASA launch site - never 'confirmed'. No square-km figures for Leonida. Payoff: games keep a place's feeling, not every landmark. CTA: 'Which Florida spot should be in it?' Show GTA 5 Los Santos (OFFICIAL GTA V image) when it is compared."),
 "gta6-biggest-launches": ("Can GTA 6 beat the biggest launch ever?",
  "VERIFIED. Publishes launch day. HOOK: 'GTA 5 made 815 million dollars in one day. GTA 6 starts today.' Facts (Guinness World Records, Oct 2013, https://www.guinnessworldrecords.com/news/2013/10/confirmed-grand-theft--auto-breaks-six-sales-world-records-51900): GTA V made $815.7 million in its first 24 hours, sold 11.21 million copies in 24 hours, and reached $1 billion in three days - the fastest entertainment product ever to do it. Take-Two, Nov 2026: GTA 6 pre-orders are 'tracking far above our initial expectations' (Shacknews, 9 Nov 2026, https://shacknews.com/article/151308/grand-theft-auto-6-pre-orders-q2-fy27). No predictions as fact; no pre-order numbers (none published). FORMAT scoreboard. Payoff: the three records GTA 6 has to beat. CTA: 'Will GTA 6 beat it?' Show GTA 5 (OFFICIAL GTA V image) when its records are said."),
 "gta6-real-florida": ("The real Florida places hidden in GTA 6",
  "VERIFIED - CAREFUL WORDING. HOOK: 'You can visit GTA 6's map - in real life.' Facts: Leonida is Rockstar's Florida and Vice City is inspired by Miami. Rockstar's own descriptions: the Leonida Keys have 'some of the most beautiful and dangerous waters in all of America'; Grassrivers has 'deadlier predators and weirder discoveries'; Mount Kalaga 'offers prime hunting, fishing, and off-road trails' (Rockstar, via PC Gamer, https://www.pcgamer.com/games/grand-theft-auto/gta6-map). Outlets compare the Leonida Keys to the Florida Keys and Grassrivers to the Everglades - say 'looks a lot like' / 'widely compared to'; Rockstar hasn't named real places. Vice Beach's Art Deco look only if a source says so. Do NOT repeat the research-trips story (another video). Payoff: Rockstar's own descriptions of each region, set against the real place it is compared to (only sourced comparisons; no travel prices, no claims about wildlife). CTA: 'Which one would you visit?'"),
 "gta6-almost-tokyo": ("GTA almost left America",
  "VERIFIED. HOOK: 'GTA almost went to Tokyo.' Facts: former Rockstar North technical director Obbe Vermeij said GTA: Tokyo 'almost actually happened', and Rio, Moscow and Istanbul were also considered (GamesHub, via Hitmarker 27 Dec 2025, https://hitmarker.net/news/rockstar-reportedly-considered-grand-theft-auto-games-set-in-tokyo-rio-moscow-and-istanbul-former-developer-claims-1606106). Rockstar co-founder Dan Houser said other countries 'may have great cities, but they're not American cities', and the series needs guns and larger-than-life characters (Lex Fridman interview, via PC Gamer 4 Nov 2025, https://www.pcgamer.com/games/action/rockstar-co-founder-dan-houser-says-theres-a-reason-the-grand-theft-auto-games-are-always-set-in-us-cities-guns). Vermeij: a new country now is 'just not realistic' 'when there's a GTA every 12 years'. Payoff: GTA 6 returns to Vice City because GTA is a story about America. Show the city names as big callouts over GTA 6 city footage; no foreign-city pictures needed. CTA: 'Which city should GTA do next?'"),
 "gta6-india-price": ("GTA 6 costs exactly double GTA 5 in India",
  "VERIFIED. HOOK: 'In India, GTA 6 costs exactly double what GTA 5 did.' Facts: GTA 5 launched in India at Rs 2,999 in 2013 (distributor E-xpress Interactive, MCV, 10 Sept 2013, https://www.mcvuk.com/update-grand-theft-auto-5-price-to-remain-rs-2999/). GTA 6: Rs 5,999 standard, Rs 7,499 Ultimate (MySmartPrice, https://www.mysmartprice.com/gear/gaming/gaming-news/gta-6-pre-orders-go-live-in-india-standard-edition-costs-rs-5999-ultimate-edition-priced-at-rs-7499/). US: GTA 5 $59.99 -> GTA 6 $79.99 (a third more). MySmartPrice puts $80 at about Rs 6,900. Twist: in rupees the price doubled, yet India still pays less than America. No inflation or income claims. CTA: 'What does it cost where you live?'"),
  "gta6-review-scores": ("GTA 6 tied the highest Metacritic score ever",
  "VERIFIED 19 Nov 2026. Publishes 20 Nov 20:00 UTC. HOOK: 'GTA 6's reviews are in, and the number is almost perfect.' Facts: Metacritic 99 (PS5, 147 critic reviews; Xbox 99 from 14) and OpenCritic Top Critic Average 99, 100% recommend (Endgame Tools, 18 Nov 2026, https://endgametools.com/en/gta-6/news/gta-6-reviews); 99 is 'tied with Ocarina of Time for the highest score the site has ever recorded', zero mixed or negative reviews (Output Lag, 18 Nov 2026, https://outputlag.com/featured-slider/gta-6-review-roundup/). IGN, GameSpot, Eurogamer, The Guardian: 100 (Endgame Tools). IGN: 'the single most impressive video game I have ever played' (Endgame Tools). Criticism (Output Lag): 30fps cap with no performance mode; pacing sags in places. Praise: Leonida's density, 'the most reactive city Rockstar has built' (Output Lag's words). CTA: 'Is 99 too high?'"),
 "gta6-cast-one-liners": ("GTA 6's characters in Rockstar's own words",
  "VERIFIED 19 Nov 2026 - CAREFUL WORDING. HOOK: 'Rockstar sums up every GTA 6 character in one sentence.' Rockstar's character descriptions, word for word as GTA BOOM prints them (https://www.gtaboom.com/every-gta-6-character-confirmed-so-far-156f; Cal's phrase also in GamesRadar https://www.gamesradar.com/games/grand-theft-auto/gta-6-characters): 'Jason wants an easy life, but things just keep getting harder.' / 'Lucia's father taught her to fight as soon as she could walk.' / 'Brian's a classic drug runner from the golden age of smuggling in the Keys.' (Jason's landlord, runs a boat yard) / 'Boobie's all smiles until it's time to talk business.' (property, a club, a recording studio) / Raul: a seasoned bank robber always on the hunt for talent / 'Cal is at the low tide of America and happy there.' (Jason's friend). Quote beats show places, never faces. Payoff: Cal's line. CTA: 'Which character are you most excited to meet?'"),
 "gta6-trailer2-record": ("GTA 6 Trailer 2: 475 million views in a day?",
  "VERIFIED 19 Nov 2026. Publishes 21 Nov 02:00 UTC. HOOK: 'In May 2025, GTA 6 fans got really bad news.' Facts: days after a delay to 2026, trailer 2 dropped 'completely unannounced' on 'a random Tuesday' (TheGamer via OpenCritic, 8 May 2025, https://opencritic.com/news/16087/rockstar-claims-gta-6s-second-trailer-was-the-biggest-video-launch-of-all-time-with-nearly-half-a-billion-views-in-one-day). Rockstar told The Hollywood Reporter it got 475 million views across all platforms in 24 hours, the biggest video launch ever by its count; the previous record, the Deadpool & Wolverine trailer, had 365 million 'with the help of a Super Bowl airing'; trailer 1 got about 93 million on YouTube in its first day (TechRadar, https://www.techradar.com/gaming/the-latest-grand-theft-auto-6-trailer-has-set-a-major-record-by-racking-up-475-million-views-in-just-24-hours; TweakTown, https://www.tweaktown.com/news/105135/grand-theft-auto-6-trailer-2-hits-475-million-views-blowing-away-deadpool-wolverines-record/index.html). Say these are Rockstar's own numbers. CTA: 'Where were you when trailer 2 dropped?'"),
  "gta6-stream-record": ("GTA 6 launch: 7.9 million people watching at once",
  "VERIFIED 20 Nov 2026. Publishes 21 Nov 14:00 UTC. Script in gta_scripts.py. Streams Charts (preliminary): peak over 7.91M concurrent viewers, biggest game launch ever; Twitch 3.31M, beating League of Legends' Worlds 2022 final (3.11M); 36M Twitch hours in one day; ~4.6x Valorant's 2020 closed beta (1.74M); La Velada 2025 boxing still Twitch's overall record (9.68M) (https://streamscharts.com/news/gta-6-streaming-records; https://maketecheasier.com/gta-6-concurrent-viewer-record-streams-charts/). DE-CIX record 33.03 Tbps (Variety via Yahoo, https://uk.news.yahoo.com/gta-6-launch-breaks-internet-150958798.html). CTA: playing or watching?"),
  "gta6-dexter-apartment": ("GTA 6 fans found Dexter's apartment in Vice City",
  "VERIFIED 20 Nov 2026 - CAREFUL WORDING. Publishes 21 Nov 17:00 UTC. Script in gta_scripts.py. Players found Trinity Apartments (nod to the Trinity Killer), can't go inside; rooftop knife, tape, rope, syringe; a boat that resembles Slice of Life; Rockstar hasn't identified it as Dexter's home; fans flagged the building in August (Dexerto, https://www.dexerto.com/gta/gta-6-players-find-dexters-apartment-serial-killer-kit-and-can-even-steal-his-boat-3429888/; TheWrap, https://www.thewrap.com/culture-lifestyle/culture/gta-6-dexter-morgan-apartment-easter-egg/). Always 'fans/players say'. CTA: which TV show next?"),
  "gta6-story-length": ("GTA 6 is about 50 hours long, one review says",
  "VERIFIED 20 Nov 2026. Publishes 21 Nov 20:00 UTC. Script in gta_scripts.py. ScreenRant (https://screenrant.com/gta-6-main-story-length-completion/): main story roughly 50 hours across five chapters; its reviewer finished at 50h42m with some side content; GTA main stories ~30 hours since San Andreas; map roughly twice GTA 5; 100% could hit triple digits. $59.99 -> $79.99 (HotHardware). Arithmetic: ~$1.60 an hour. CTA: hours played?"),
  "gta6-sales-estimate": ("GTA 6 sold 19 million copies? Here's the catch",
  "VERIFIED 20 Nov 2026 - CAREFUL WORDING. Publishes 21 Nov 23:00 UTC. Script in gta_scripts.py. Sensor Tower ESTIMATE: 19.1M copies, ~$1.84B by the morning of release; Netflix Extended Look helped drive a sixfold jump in pre-orders; Take-Two has confirmed no numbers; Zelnick: 'we still aren't ready to declare victory' (Reuters via Yahoo, https://finance.yahoo.com/media-advertising/articles/two-set-shatter-sales-records-162847652.html; Men's Journal). GTA V 11.21M / $815.7M in 24 h (Guinness). Never state the estimate as fact. CTA: bought it day one?"),
  "gta6-first-look-2021": ("GTA 6 fans think we saw it back in 2021",
  "VERIFIED 20 Nov 2026 - FAN THEORY. Publishes 22 Nov 02:00 UTC. Script in gta_scripts.py. A Belville house in GTA 6 matches a house image exclusive to GTA: San Andreas - Definitive Edition (2021), speculated to come from GTA 6 development; 'line up to the smallest details, like the placement of plants and trees'; VGC: 'may have been our first look' (https://www.videogameschronicle.com/news/gta-6-players-discover-our-real-first-look-at-the-game-was-likely-hidden-in-a-2021-remaster/). Trailer 1: Dec 2023. No fan names. CTA: other clues?"),
  "gta6-official-sales": ("GTA 6 made $3.79 billion on day one, Rockstar says",
  "VERIFIED 21 Nov 2026. REMAKE of tonight's sales-estimate video (Rockstar published official numbers on 20 Nov, so 'Take-Two has confirmed no numbers' was no longer true). Publishes 21 Nov 23:00 UTC. Script in gta_scripts.py. Rockstar/Take-Two release (SEC 8-K ex. 99.1): $3.79B day one retail sales (company estimates to end of 19 Nov, worldwide), 32.5M units pre-release, 'the biggest entertainment launch in history'. Variety: pre-order and first-day sales. Avatar $2.923B all-time (Wikipedia). GTA V $815.7M in 24 h (Guinness). CTA: day one or wait?"),
  "gta6-console-best": ("GTA 6 runs best on one console. Here's which",
  "VERIFIED 21 Nov 2026. Publishes 22 Nov 12:00 UTC. Script in gta_scripts.py. Digital Foundry via GTA BOOM / AltChar / Endgame Tools: 30 fps on all, PS5 Pro best (PSSR near-4K, RT shadows), PS5 + Series X 1440p, PS5 dips to 23, Series X slightly lower with VRR, Series S 720p ~20 fps. Rockstar (Kotaku): hardware not powerful enough for higher frame rates. CTA: PlayStation or Xbox?"),
  "gta6-dating-lucia": ("Is dating Lucia in GTA 6 cheating? Couples disagree",
  "VERIFIED 21 Nov 2026 - NO STORY SPOILERS. Publishes 22 Nov 14:00 UTC. Script in gta_scripts.py. Output Lag (relationship tasks, heart pop-up, no other romance, no break-up), Vice (hold hands, 'robbing a bank together counts as quality time', goodnight text), Unilad (TikTok/X/Reddit cheating debate, quotes, 10-day contracts to 29 Nov). CTA: cheating, yes or no?"),
  "gta6-kodak-radio": ("GTA 6 has a secret Kodak Black radio station",
  "VERIFIED 21 Nov 2026. Publishes 22 Nov 17:00 UTC. Script in gta_scripts.py. Vice: The Sniper of La Perle, four posters (Aunt Zola's Soul Food, TWA Ponya Tattoo, Drip Drops in La Perle; Jack of Hearts club upstairs in Crosstown), 22 songs, needed for 100%. Kotaku: Weird Al '80s station. CTA: Kodak or Weird Al?"),
  "gta6-weird-secrets": ("GTA 6's weirdest secrets players found in week one",
  "VERIFIED 21 Nov 2026. Publishes 22 Nov 20:00 UTC. Script in gta_scripts.py. Kotaku list (Bigfoot, UFOs, crab monster, 62 birds, Tony from San Andreas, scooter); Parade (jet-ski dog rescue, island of dogs, $1,200+ treasure, fans link it to Loosy, unconfirmed). CTA: Bigfoot or the jet ski dog?"),
  "gta6-true-fat-jason": ("GTA 6 players are trying to make Jason fat",
  "VERIFIED 21 Nov 2026. Publishes 23 Nov 02:00 UTC. Script in gta_scripts.py. GamesRadar ('True Fat Jason', fan method, not as big as Arthur Morgan), LADbible (San Andreas weight/muscle system returns). CTA: gym Jason or True Fat Jason?"),
  "gta6-lucia-actor": ("GTA 6's Lucia actress was in GTA 5 all along",
  "VERIFIED 22 Nov 2026. Publishes 23 Nov 12:00 UTC. Script in gta_scripts.py. LADbible/Yahoo/ScreenRant (19 Nov): Manni L. Perez plays Lucia (Game Awards Best Performance nomination; first credit Clubber 2 in GTA V; unnamed blackjack dealer in a 2019 GTA Online update; Jessica Jones, The Blacklist, Law & Order; Muay Thai, BJJ, MMA; 2018 Paz quote). Dylan Rourke posted that he played Jason (his video game debut; Station 19, Modern Family; 'See y'all in Leonida.'). CTA: Lucia or Jason?"),
  "gta6-map-size": ("GTA 6's map vs GTA 5: how big is it really?",
  "VERIFIED 22 Nov 2026. Publishes 23 Nov 14:00 UTC. Script in gta_scripts.py. No official square-mile figure (GTA Zone); about twice GTA 5 per Rockstar (Forbes); 3x RDR2 per TGG (SlashGear); six regions; 170+ animal species (Game Informer via Forbes); ~35 min to drive across (estimate, SlashGear). CTA: bigger map or more detail?"),
  "gta6-online-when": ("GTA 6 has no online mode. When is it coming?",
  "VERIFIED 22 Nov 2026 (status as of 21 Nov). Publishes 23 Nov 17:00 UTC. Script in gta_scripts.py. Single-player only (store pages; Leonipedia, GameVerse); GTA Online came 1 Oct 2013, two weeks after GTA V; no announced online mode or date; Twitch CEO Clancy to Bloomberg ('next year when they launch multiplayer'); Schreier: expected 2027; Take-Two keeps supporting GTA Online. CTA: story first or online first?"),
  "gta6-zelda-score": ("GTA 6's Metacritic fight just dragged in Zelda",
  "VERIFIED 22 Nov 2026 - CAREFUL WORDING (scores change; dated 21 Nov). Publishes 23 Nov 20:00 UTC. Script in gta_scripts.py. GTABase/Notebookcheck/CBR/Push Square: critics 99 (ties Ocarina), PS5 user score 5.6 on 21 Nov, ~30K negative ratings, complaints (30 fps, bugs, slow start, no disc); Ocarina user score 9.6 -> 8.7 in under a day; Push Square: looks like GTA 6 fans hitting back. CTA: critics or players?"),
  "gta6-egg-tower": ("GTA 6 hid a real Easter egg at the top of a tower",
  "VERIFIED 22 Nov 2026. Publishes 24 Nov 02:00 UTC. Script in gta_scripts.py. ComicBook (20 Nov): egg nest on a radio tower in South Vice-Dale County, throw one for a windshield cutscene; Port Gellhorn alien abduction after 2am, Jason's rescue (code 2-3-4-1 at a military airfield), a living alien, achievement 'The Truth is Out There'. CTA: egg tower or alien rescue?"),
  "gta6-trailer-songs": ("GTA 6's trailers brought two old songs back to life",
  "RESERVE (evergreen), VERIFIED 20 Nov 2026. Script in gta_scripts.py. Tom Petty 'Love Is A Long Road' (1989) +36,979% Spotify after trailer 1 (IGN/GameSpot); The Pointer Sisters 'Hot Together' (1986) +182,000% in two hours after trailer 2 (TechRadar). CTA: which song on GTA 6's radio?"),
  "gta6-vice-city-1986": ("GTA 6 isn't our first trip to Vice City",
  "RESERVE (evergreen), VERIFIED 20 Nov 2026. Script in gta_scripts.py. GTA Vice City: PS2, Oct 2002, set in 1986, Miami-based, Tommy Vercetti voiced by Ray Liotta, 17.5M+ copies (Wikipedia). GTA 6: Leonida inspired by Florida, leads Jason Duval and Lucia Caminos (Destructoid). CTA: played the original?"),
}

# owner (16 Nov 2026): each video must look and feel different -> its own format, pace and opening style
# 18 Nov 2026 (cost): scripts written and verified by Claude in session (scripts/gta_scripts.py)
_SF = Path(__file__).resolve().parent.parent / "config" / "gta_scripts.json"
SCRIPTS = json.loads(_SF.read_text()) if _SF.exists() else {}

FORMATS = {
 # 18 Nov 2026: the old formats were gimmicks (checklists, countdowns, "Check." running gags) that produced fragments
 # the story reviewer rightly rejects. Now each is a story SHAPE and a tone, told in natural sentences.
 "gta6-ultimate-worth": "Tone: a friend helping you decide. Shape: the $20 question -> the three best extras, building to the best one -> an honest take.",
 "gta6-extended-look": "Tone: excited. Shape: one jaw-dropping feature after another, each bigger than the last.",
 "gta6-13-years": "Tone: nostalgic. Shape: a journey through the years, ending on the moment it finally arrives.",
 "gta6-ps5-space": "Tone: calm and practical. Shape: the problem -> the real number -> what to do about it.",
 "gta6-lucia": "Tone: warm, character-focused. Shape: the common belief -> the surprising history -> what really makes her a first.",
 "gta6-heat-vice-city": "Tone: upbeat news. Shape: the surprising real-world event -> the details -> the clever game reference.",
 "gta6-unlock-time": "Tone: urgent. Shape: who is already playing -> the times around the world -> the twist for the viewer.",
 "gta6-vice-city-research": "Tone: documentary. Shape: how it started -> what they did -> what it means for the game.",
 "gta6-no-disc": "Tone: curious. Shape: the empty box -> what the CEO actually said -> the bigger picture.",
 "gta6-almost-tokyo": "Tone: 'what if'. Shape: the cities GTA almost went to -> why they never happened -> why it always comes back to America.",
 "gta6-biggest-launches": "Tone: big-stakes sports commentary. Shape: the records GTA 5 set -> what GTA 6 is up against -> the question.",
 "gta6-real-florida": "Tone: travel story. Shape: each region in Rockstar's words -> the real place it is compared to.",
 "gta6-map-vs-florida": "Tone: playful. Shape: what Leonida captures -> the famous places Rockstar suggests it leaves out -> why (Rockstar's own words).",
 "gta6-india-price": "Tone: surprised. Shape: the 2013 price -> the 2026 price -> the twist in dollars.",
 "gta6-review-scores": "Tone: a big verdict being read out. Shape: the score -> the record it ties -> the perfect scores -> the honest criticism -> what everyone agrees on.",
 "gta6-cast-one-liners": "Tone: playful roll call. Shape: one character at a time, each with Rockstar's own one-liner, saving the funniest line for last.",
 "gta6-trailer2-record": "Tone: comeback story. Shape: the bad news -> the surprise drop -> the number -> the movie it beat -> the payoff.",
 "gta6-leak-war": "Tone: tense thriller. Shape: the 2022 break-in -> the leaked trailer -> the 2026 court fight.",
 "gta6-stream-record": "Tone: breathless live-sports record call. Shape: the crowd -> records falling one by one -> the one record left standing.",
 "gta6-dexter-apartment": "Tone: hushed, spooky true-crime. Shape: the discovery -> the building -> the creepy roof -> the boat -> not confirmed.",
 "gta6-story-length": "Tone: practical, a friend doing the maths. Shape: the question -> the hours -> the comparison -> the price per hour.",
 "gta6-sales-estimate": "Tone: sceptical business reporter. Shape: the huge number -> the catch -> the GTA 5 benchmark -> what Take-Two says.",
 "gta6-first-look-2021": "Tone: detective. Shape: the clue in 2021 -> the match in 2026 -> the details -> a fan theory, clearly labelled.",
 "gta6-official-sales": "Tone: big-number reveal, delighted. Shape: the movie-beating claim -> the official number -> the estimate it crushed -> GTA 5 -> the biggest film ever -> the verdict.",
 "gta6-console-best": "Tone: a friend who read the tests for you, practical. Shape: the scary number -> the rule for all -> last place -> the middle -> the winner.",
 "gta6-dating-lucia": "Tone: amused gossip. Shape: real couples arguing -> what the game asks of you -> the internet's two sides -> the twist inside the game.",
 "gta6-kodak-radio": "Tone: insider tip, quick and clear. Shape: the secret -> who hosts it -> the four posters, one by one -> the reward.",
 "gta6-weird-secrets": "Tone: amazed, escalating. Shape: Bigfoot -> stranger and stranger finds -> the real Florida dog -> an old friend from San Andreas.",
 "gta6-true-fat-jason": "Tone: playful. Shape: the silly mission -> the system -> the fan's recipe -> the anticlimax twist.",
 "gta6-lucia-actor": "Tone: fan-detective, warm. Shape: the hidden cameo -> who she is -> the tiny GTA 5 role -> the Online role -> who she is off screen -> Jason's actor.",
 "gta6-map-size": "Tone: practical myth-buster, quick. Shape: the question -> no official number -> what Rockstar has said -> what's reported -> how long it takes to cross.",
 "gta6-online-when": "Tone: a friend answering a worried player, calm. Shape: the bad news -> GTA 5 did the same -> no date -> a hint -> what's confirmed.",
 "gta6-zelda-score": "Tone: gossip about an internet war, amused. Shape: the two numbers -> why players are angry -> the twist (Zelda) -> the revenge.",
 "gta6-egg-tower": "Tone: insider tip turning spooky. Shape: the climb -> the egg nest -> the cutscene -> the light in the sky -> the alien rescue -> the joke achievement.",
 "gta6-trailer-songs": "Tone: music nerd, delighted. Shape: the claim -> song one + number -> Florida link -> song two, bigger -> comparison.",
 "gta6-vice-city-1986": "Tone: nostalgic friend. Shape: not the first trip -> 2002 game facts -> the hit -> the new Vice City -> the new leads.",
}

# publish times (UTC); 5 a day, every 3 h over the US day (owner, 16 Nov: 5 a day)
PLAN = [
 ("2026-11-16", "2026-11-16T20:00:00Z", "gta6-cheaper-than-gta5"),
 ("2026-11-16", "2026-11-16T23:00:00Z", "gta6-florida-man"),
 ("2026-11-16", "2026-11-17T02:00:00Z", "gta6-trailer-record"),
 ("2026-11-16", "2026-11-16T17:00:00Z", "gta6-not-on-pc"),
 ("2026-11-17", "2026-11-18T11:00:00Z", "gta6-ultimate-worth"),
 ("2026-11-17", "2026-11-17T17:00:00Z", "gta6-extended-look"),
 ("2026-11-17", "2026-11-17T20:00:00Z", "gta6-13-years"),
 ("2026-11-17", "2026-11-17T23:00:00Z", "gta6-ps5-space"),
 ("2026-11-17", "2026-11-18T02:00:00Z", "gta6-lucia"),
 ("2026-11-17", "2026-11-18T14:00:00Z", "gta6-heat-vice-city"),   # made 17 Nov as the approved story-format sample
 ("2026-11-17", "2026-11-18T17:00:00Z", "gta6-unlock-time"),   # started by hand 18 Nov 07:35Z (the 00:17Z daily run was held)
 # 18 Nov 2026: gta6-vice-city-research dropped twice at the script check (its payoff and quote were not verifiable first-hand); slot left empty
 ("2026-11-17", "2026-11-18T23:00:00Z", "gta6-no-disc"),   # started by hand 18 Nov 07:35Z (the 00:17Z daily run was held)
 ("2026-11-17", "2026-11-19T02:00:00Z", "gta6-map-vs-florida"),   # started by hand 18 Nov 07:35Z (the 00:17Z daily run was held)
 ("2026-11-18", "2026-11-19T14:00:00Z", "gta6-biggest-launches"),   # made 18 Nov as the first test of pre-written scripts
 ("2026-11-20", "2026-11-20T12:00:00Z", "gta6-india-price"),   # 19 Nov 17:00 slot missed (held); v2 at 17:30 IST
 ("2026-11-19", "2026-11-19T20:00:00Z", "gta6-leak-war"),
 ("2026-11-19", "2026-11-19T23:00:00Z", "gta6-almost-tokyo"),
 ("2026-11-19", "2026-11-20T02:00:00Z", "gta6-real-florida"),
 ("2026-11-20", "2026-11-20T14:00:00Z", "gta6-florida-man"),   # remake in the new style (16 Nov version: 21 views at 48 h)
 ("2026-11-20", "2026-11-20T17:00:00Z", "gta6-not-on-pc"),     # remake in the new style (16 Nov version: 6 views at 48 h)
 ("2026-11-20", "2026-11-20T20:00:00Z", "gta6-review-scores"),
 ("2026-11-20", "2026-11-20T23:00:00Z", "gta6-cast-one-liners"),
 ("2026-11-20", "2026-11-21T02:00:00Z", "gta6-trailer2-record"),
 ("2026-11-21", "2026-11-21T14:00:00Z", "gta6-stream-record"),
 ("2026-11-21", "2026-11-21T17:00:00Z", "gta6-dexter-apartment"),
 ("2026-11-21", "2026-11-21T20:00:00Z", "gta6-story-length"),
 ("2026-11-21", "2026-11-21T23:00:00Z", "gta6-sales-estimate"),
 ("2026-11-21", "2026-11-22T02:00:00Z", "gta6-first-look-2021"),
 ("2026-11-21", "2026-11-21T23:00:00Z", "gta6-official-sales"),   # 21 Nov remake: official numbers replaced the estimate (started by hand)
 ("2026-11-22", "2026-11-22T12:00:00Z", "gta6-console-best"),
 ("2026-11-22", "2026-11-22T14:00:00Z", "gta6-dating-lucia"),
 ("2026-11-22", "2026-11-22T17:00:00Z", "gta6-kodak-radio"),
 ("2026-11-22", "2026-11-22T20:00:00Z", "gta6-weird-secrets"),
 ("2026-11-22", "2026-11-23T02:00:00Z", "gta6-true-fat-jason"),
 ("2026-11-23", "2026-11-23T12:00:00Z", "gta6-lucia-actor"),
 ("2026-11-23", "2026-11-23T14:00:00Z", "gta6-map-size"),
 ("2026-11-23", "2026-11-23T17:00:00Z", "gta6-online-when"),
 ("2026-11-23", "2026-11-23T20:00:00Z", "gta6-zelda-score"),
 ("2026-11-23", "2026-11-24T02:00:00Z", "gta6-egg-tower"),
]


# 20 Nov 2026 (owner away 21-27 Nov): evergreen scripts (no time words) that fill any GTA slot the script desk
# could not fill. Each needs a finished, fact-checked script in scripts/gta_scripts.py. The daily run uses them in
# this order and only once.
RESERVE = ["gta6-trailer-songs", "gta6-vice-city-1986"]


def build():
    from shorts.official import catalogue_text
    from shorts.official_clips import shots_text
    tail = ("\nSHOT LIST (CLIP:<id> | length | what it shows):\n@@SHOT_LIST@@"
            + "\n\nSCREENSHOT CATALOGUE (OFFICIAL:<id> | game | what it shows; mainly for GTA 5):\n"
            + catalogue_text(("GTA V",)))
    q = []
    for day, at, tid in PLAN + [(None, None, t) for t in RESERVE]:
        title, angle = V[tid]
        if tid in FORMATS:
            angle += " FORMAT FOR THIS VIDEO (its own look and feel): " + FORMATS[tid]
        notes = {"object": "official GTA 6 footage", "question": title, "angle": angle,
                 "format_rules": RULES_STORY + tail, "critic_rules": CRITIC_STORY, "official_images": "required",
                 "open_hook": True, "words": [110, 170], "cover_rule": COVER, "style": "story", "badge": "GTA 6", **({"script": SCRIPTS[tid]} if tid in SCRIPTS else {}),
                 "publish_at": at, "batch": "gta6-launch-footage",
                 # 17 Nov 2026: GTA videos went out as Education (27) with generic tags; Gaming (20) + GTA search terms
                 "seo": {"category_id": "20", "hashtags": ["#GTA6", "#GTAVI", "#GrandTheftAuto6"],
                         "tags": ["GTA 6", "GTA VI", "Grand Theft Auto 6", "Grand Theft Auto VI", "GTA 6 news",
                                  "GTA 6 trailer", "Rockstar Games", "Vice City", "Jason and Lucia", "Leonida"]}}
        # 20 Nov 2026: a remake of a topic on a later day needs its own nonce (the daily run skips used nonces)
        nonce = f"gta-footage-{tid}" if (day or "") <= "2026-11-20" else f"gta-footage-{tid}-{day}"
        q.append({"action": "produce", "topic": tid, "fresh": True, "nonce": nonce, "day": day,
                  "topic_def": {"id": tid, "title": title, "pillar": "gta6", "notes": notes}})
        if day is None:          # RESERVE: no day, no slot; the daily run gives it an empty slot
            q[-1].pop("day")
            q[-1]["reserve"] = True
            q[-1]["nonce"] = f"gta-reserve-{tid}"
    return q


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/shorts-system/config/daily_queue.json"
    q = build()
    json.dump({"note": "GTA 6 launch week, footage edition (owner, 16 Nov 2026): 5 a day, Rockstar footage. "
               "Built by scripts/gta_queue.py.", "queue": q}, open(out, "w"), indent=1, ensure_ascii=False)
    print(len(q), sorted({x['day'] for x in q if x.get('day')}), 'reserves:', sum(1 for x in q if x.get('reserve')))
