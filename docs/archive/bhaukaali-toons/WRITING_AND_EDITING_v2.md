# Craft rules: writing and editing (research, 27 Oct 2026)

**Tags:**
- **[E]** = established. It comes from an expert or primary source.
- **[O]** = practitioner opinion. It is a default we can tune.

The writer prompt (`shorts/sketch/writer.py`) and the automatic editor (`shorts/sketch/director.py`) follow this page.

## Writer rules

1. **One game per sketch [E]** (UCB / Will Hines, GOLD Comedy, Chuffah).
   - State the unusual thing in one sentence before writing.
   - Never add a second premise.
2. **Base reality first, in 1–2 lines [E].**
   - Use a real, specific UP situation, built from observed incidents the way the Panchayat writers work.
   - Don't force-feed the audience.
3. **Heighten in three beats, each bigger [E].**
   - There are three levers: specifics, emotion and stakes.
   - Change the lever between beats.
4. **"If this is true, what else is true?" [E].**
   - Every line follows from the game.
5. **Status [E]** (Johnstone, *Impro*).
   - **Dev:** low status. He accepts every offer.
   - **Rocky:** high status. He never concedes.
   - **Meera:** relaxed high status. She speaks least and lowers others with one line.
   - The biggest laughs come from status reversals.
6. **Fixed comic filters [E]** (Vorhaus).
   - Each character sees every situation through the same lens.
   - The comedy is the clash between the lenses.
7. **Funny word last [E].**
   - Hindi is verb-final. Put the reveal noun after the verb, or in a separate tag line.
8. **Rule of three [E]:** pattern, pattern, break. The third item is short.
9. **Misdirection [E]:** at most once per sketch.
10. **One false victory or reversal in the middle [E].**
11. **Callback [E]** to the first 5 seconds. This also helps the loop.
12. **Button [E]** after the punch: one short extra laugh.
    - "Sab theek hai" can be that ironic button, at most once.
13. **Lines:** 3–10 words, 12 at most. People interrupt, trail off, and answer a question with a question. [O]
14. **Real code-switching:**
    - Office and tech words stay in English.
    - Feelings stay in Hindi.
    - No stage Hindi (kripya, parantu, atyant). [O]
15. **Dialect is seasoning:** at most one UP marker every 2–3 lines. [O]
16. **Nobody names the joke or the emotion.** No forced catchphrase. [O]
17. **Avoid LLM humour tells:**
    - generic "vibes" jokes;
    - exaggeration with no observation behind it;
    - jokes that sound like jokes but mean nothing;
    - a punchline that doesn't pay off its setup.
    - Test: would a real person in Kanpur say this and get it? [O]
18. **Dev's inner voice** tells the truth his outer voice hides.
    - At most 3 times per sketch, getting more panicked each time.
    - Never used for exposition.

### Structures that fit 35–45 s
- **A. Haan Ki Seedhi (the Yes Ladder):**
  - Dev says yes to a small ask, then to 3 bigger asks.
  - His outer voice gets calmer while his inner voice gets louder.
  - Punch: something absurd.
  - Button: he finally says "nahi"… to Meera's trivial request.
- **B. Galti Nahi, Style Hai (Doubling Down):**
  - Rocky's mistake gets grander and grander justifications.
  - The client starts believing him.
  - Meera's one fact collapses it.
- **C. Status Ka Jhoola (the Status See-saw):**
  - The high-status character humiliates the low one.
  - A small reveal flips it.
  - The former high one begs.
- **D. Ulta Pada (Misdirect and Reveal):**
  - The staging points to an obvious outcome.
  - The final reveal reframes it.
  - Meera treats it as normal.

### Timing skeleton for about 40 s [O]

| Time | Beat |
|---|---|
| 0–2 s | Hook |
| 2–7 s | Base reality |
| 7–30 s | Three beats |
| 30–36 s | Punch |
| 36–40 s | Button that loops back |

- Total: 85–110 spoken words.

### Writer self-check (the editor pass verifies each item)
- The game is stated in one sentence, and every beat serves it.
- The first line is 8 words or fewer, spoken at 0.0 s, and shows the conflict.
- There are three escalating beats on different levers.
- Each punchline ends on its funny word, and no line explains itself.
- There is a status shift or reversal.
- There is a button, and the last moment connects to the first.
- Meera has 3 lines or fewer. The inner voice appears 3 times or fewer.
- No stage Hindi and no line over 12 words.

## Editor rules

- **Cut priority [E]** (Murch): emotion > story > rhythm > eye-trace > screen direction > 3D space.
- **Shot lengths [O]:**
  - Dialogue shots: 1.5–4 s, median about 2.5 s.
  - Hard maximum: 5 s. A wide physical gag can run 6 s.
  - Minimum: 0.8 s.
- **Visual change:** something changes visually at least every 3 s.
- **Shot sizes:**
  - No more than 2 consecutive shots of the same size.
  - When cutting on the same character, change size by at least one step [E: 30° rule].
  - Show the wide/establishing shot for 1.5 s or more within the first 7 s.
- **Reactions:**
  - Reaction shots run 0.6–1.2 s. On the punch, 1.0–2.0 s [E].
  - Never cut away before the punch line ends [E].
- **Pauses:**
  - Before the main punch and the button only: 0.25–0.5 s.
  - Other gaps between lines: 0.05–0.2 s ("the enemy of comedy is the unnecessary pause") [E/O].
  - After the punch: hold 0.8–1.5 s, then the button.
  - No dead air after the button.
- **Special shots:**
  - Inner-voice close-ups: 1.0–2.5 s, at most 3.
  - Black beat: 0.4–0.8 s, at most 1. Never in the first 3 s, and never as the last shot.
- **180° rule [E]:**
  - Keep each character on a fixed screen side within a scene.
  - Eyelines must match.
  - Use wides for physical and spatial gags, close-ups for reactions and punches.
- **Hook:**
  - Frame 1 shows a character mid-expression, and speech starts by 0.3 s.
  - No title card and no fade-in.
- **Loop:** no freeze or fade at the end. The last 3 s plus the first 3 s should play as continuous.
- **Audio [O]:**
  - Master: −14 LUFS, true peak −1 dBTP.
  - Music: 18–24 dB under dialogue, ducked a further 3–6 dB during speech.
  - Drop the music 0.3–0.5 s before the main punch. Music is optional.
- **SFX [O]:**
  - 2–5 per video, each motivated by a visible action.
  - At most 1 comedic stinger.
  - No meaningless dings or rings, no whoosh on every cut, no record scratch or vine boom.
- **Captions:**
  - 1–2 lines, 32–42 characters or fewer.
  - Shown 0.0–0.1 s before the audio.
  - Never show the punch word before it is spoken.
  - Centre, about 55–70% down the frame, never covering a face.
  - One colour per character. The inner voice is italic.

## Sources
- https://willhines.substack.com/p/teaching-game-2-heighten-and-explore
- https://www.thefreeassociation.co.uk/blog/easy-ways-to-heighten-game
- https://goldcomedy.com/resources/how-to-write-a-comedy-sketch/
- https://chuffah.substack.com/p/the-basics-1-sketch-and-game
- https://jamesclear.com/book-summaries/impro
- https://nofilmschool.com/john-vorhaus-comedy-writing-tools
- https://funnyhow.substack.com/p/the-rule-of-three
- https://www.toastmasters.org/magazine/magazine-issues/2018/july2018/humor
- https://swampruby.substack.com/p/chatgpt-humour-a-dissection
- https://www.degruyterbrill.com/document/doi/10.1515/HUMR.2011.015/pdf
- https://escholarship.org/uc/item/58t1w6r7
- https://www.india-seminar.com/2023/763/763-13%20Interview-Chandan-Sweksha.htm
- https://theprint.in/ground-reports/youtube-favourite-to-ott-darling-tvfs-success-has-even-bollywood-calling/1876714/
- https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch
- https://cinemontage.org/?p=58217
- https://www.moviemaker.com/edgar-wright-visual-comedy-video/
- https://filmdaft.com/the-l-cut-and-j-cut-how-film-editors-use-audio-to-control-time/
- https://www.studiobinder.com/blog/storyboard-rules
- https://blog.youtube/creator-and-artist-stories/youtube-shorts-deep-dive/
- https://www.overseeros.com/blog/background-music-volume-under-voiceover
- https://clevercast.com/bbc-subtitling-guidelines
- https://www.opus.pro/blog/youtube-shorts-caption-subtitle-best-practices
- https://reap.video/blog/short-form-video-safe-zones
