"""GTA 6 launch week, footage edition (owner, 16 Nov 2026): 5 videos a day, Rockstar's own trailer footage,
story-first scripts. Built into config/daily_queue.json."""
import json
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
}

# owner (16 Nov 2026): each video must look and feel different -> its own format, pace and opening style
FORMATS = {
 "gta6-ultimate-worth": "SHOPPING COUNTDOWN: 'Here's what $20 more gets you' - #3, #2, #1 extras, each with its price-tag style callout; ends on the verdict line.",
 "gta6-extended-look": "RAPID-FIRE LIST: four 'wait, you can do THAT?' features, fastest cuts of the week (1.5-2 s), energetic, each feature shown in action.",
 "gta6-13-years": "TIME MACHINE: a timeline told year by year (2013 -> 2018 -> 2023 -> 2025 -> 2026), each year as a big callout; nostalgic, slower pace.",
 "gta6-ps5-space": "PRACTICAL MATHS: a calm problem -> number reveal -> 'here's what to do' fix; friendly, useful, one witty line.",
 "gta6-lucia": "CHARACTER STORY: open on Lucia, slower emotional build, her journey in the trailers, the 29-year reveal as the twist.",
 "gta6-heat-vice-city": "NEWS FLASH: 'tonight' urgency, real-world-to-game reveal, upbeat.",
 "gta6-unlock-time": "COUNTDOWN CLOCK: the world map of times, fastest first, ending on the viewer's own time; urgent.",
 "gta6-vice-city-research": "BEHIND THE SCENES: documentary feel, 'in 2015 a team flew to Miami...', field-notes callouts (year, place), slow build to the reveal.",
 "gta6-no-disc": "UNBOXING MYSTERY: the empty box, the question, the CEO's answer as a quote card, then the twist line.",
 "gta6-almost-tokyo": "WHAT IF: alternate-history 'GTA Tokyo... GTA Rio... GTA Moscow' city-name callouts, then why it always comes home.",
 "gta6-biggest-launches": "RECORD BATTLE: GTA 5's records vs GTA 6's start, scoreboard style.",
 "gta6-real-florida": "TRAVEL GUIDE: real places, 'you can actually visit this', postcard feel.",
 "gta6-map-vs-florida": "WHAT'S MISSING: 'it has... it has... but it doesn't have...' checklist with ticks and one big cross.",
 "gta6-india-price": "PRICE TAG FLIP: two price tags side by side (2013 vs 2026), the doubling reveal, then the dollar twist.",
 "gta6-leak-war": "HEIST THRILLER: tense, the leak as a crime story, then Rockstar's response.",
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
 ("2026-11-19", "2026-11-19T14:00:00Z", "gta6-biggest-launches"),
 ("2026-11-19", "2026-11-19T17:00:00Z", "gta6-india-price"),
 ("2026-11-19", "2026-11-19T20:00:00Z", "gta6-leak-war"),
 ("2026-11-19", "2026-11-19T23:00:00Z", "gta6-almost-tokyo"),
 ("2026-11-19", "2026-11-20T02:00:00Z", "gta6-real-florida"),
]


def build():
    from shorts.official import catalogue_text
    from shorts.official_clips import shots_text
    tail = ("\nSHOT LIST (CLIP:<id> | length | what it shows):\n@@SHOT_LIST@@"
            + "\n\nSCREENSHOT CATALOGUE (OFFICIAL:<id> | game | what it shows; mainly for GTA 5):\n"
            + catalogue_text(("GTA V",)))
    q = []
    for day, at, tid in PLAN:
        title, angle = V[tid]
        if tid in FORMATS:
            angle += " FORMAT FOR THIS VIDEO (its own look and feel): " + FORMATS[tid]
        notes = {"object": "official GTA 6 footage", "question": title, "angle": angle,
                 "format_rules": RULES_STORY + tail, "critic_rules": CRITIC_STORY, "official_images": "required",
                 "open_hook": True, "words": [110, 170], "cover_rule": COVER, "style": "story",
                 "publish_at": at, "batch": "gta6-launch-footage",
                 # 17 Nov 2026: GTA videos went out as Education (27) with generic tags; Gaming (20) + GTA search terms
                 "seo": {"category_id": "20", "hashtags": ["#GTA6", "#GTAVI", "#GrandTheftAuto6"],
                         "tags": ["GTA 6", "GTA VI", "Grand Theft Auto 6", "Grand Theft Auto VI", "GTA 6 news",
                                  "GTA 6 trailer", "Rockstar Games", "Vice City", "Jason and Lucia", "Leonida"]}}
        q.append({"action": "produce", "topic": tid, "fresh": True, "nonce": f"gta-footage-{tid}", "day": day,
                  "topic_def": {"id": tid, "title": title, "pillar": "gta6", "notes": notes}})
    return q


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/shorts-system/config/daily_queue.json"
    q = build()
    json.dump({"note": "GTA 6 launch week, footage edition (owner, 16 Nov 2026): 5 a day, Rockstar footage. "
               "Built by scripts/gta_queue.py.", "queue": q}, open(out, "w"), indent=1, ensure_ascii=False)
    print(len(q), sorted({x['day'] for x in q}))
