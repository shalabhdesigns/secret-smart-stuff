# Facial expression and acting rules (research, 27 Oct 2026)

These rules are implemented in `scripts/puppet/face.py` (the face recipes) and in `Actor.state` in `scripts/puppet/puppet.py` (timing). They are built from:
- Ekman/FACS
- Preston Blair
- Richard Williams
- Thomas & Johnston
- AnimSchool
- School of Motion
- Bloop Animation
- Animation Mentor
- Brian LeMay
- Cohn & Foulsham (2022)

The numbers are practitioner starting values, so tune them by eye.

## Why the first version failed
- **One half-closed eye reads as an injury.** In FACS the only one-sided emotion is contempt, and it shows in the **mouth corner**, not the eye.
- **Mixed signals read as nothing.** Eyes rolled up + blush + open mouth is three ideas at once. Faces whose signals agree are understood faster (Cohn & Foulsham). Disney's staging rule says the same: one idea, unmistakably clear.
- **An eye twitch is too small and too mechanical to read on a phone.**

## Face rules
- **One idea per face.** Brows, lids and mouth must agree.
- **Eyes stay symmetric.** Asymmetry is allowed only in:
  - brows (skeptical, confused, thinking);
  - mouth corners (smirk, annoyed, disgust).
  - An eye may differ from the other only when its own brow differs, and by no more than 0.3.
- **A genuine smile** = mouth corners up AND lower lids pushed up (AU6+12).
- **The forced smile** (Dev's signature) = smiling mouth + worried brows + no lower-lid push.
- **Phone-size readability:**
  - Brow changes of 0.3 units or more, or none at all.
  - No eye twitch, no ear redness, no worry lines.
  - One symbol per face.
- **Symbols that read for Indian viewers** (Doraemon/Shinchan dubs, emoji):
  - one sweat drop: awkward, nervous;
  - blush: sharam / shy;
  - red face rising from the chin: gussa (anger);
  - sparkle eyes: excited;
  - gloom: defeated.
  - The anger vein was dropped: at small size it can read as a bad symbol.
  - A symbol appears on the accent frame and fades after about 1.5 s.

## Timing
- **The take** (big changes: shock, scared, panic, excited, laugh, angry):
  - Anticipation: 5 frames, slightly the opposite way, with an eye squeeze and a head dip.
  - Accent: 3 frames, at 125% of the target.
  - Settle: 9 frames down to 100%.
  - Hold: at least 24–45 frames.
- **Small changes:** a 6-frame ease with a blink.
- **Holds:**
  - At least 10 frames for a small change.
  - 15–24 frames for a new expression to read.
  - 30–60 frames for a punchline reaction.
  - Never jitter during a hold.
- **Expression changes:**
  - One change per change of thought, roughly every 2–4 s.
  - Never closer together than 0.45 s.
  - Listeners change less often than speakers.
- **Accents:**
  - Brows lift +0.3 on 1–2 stressed words per sentence, peaking within 4 frames.
  - The brows lead the sound by about 3 frames, with a small nod.
  - No continuous head bobbing while talking.
- **Blinks:**
  - Speed: 3 frames close, 1 hold, 4 open. Long blinks (thought change, deadpan): 4 / 2 / 5.
  - When: on a thought change, a head move or before an emotion change. A sparse fallback blink every 3.5–5.5 s.
  - Never during angry or shocked stares.
- **Eye darts (nervous):** a new spot every 7 frames, moving over 3 frames.
- **Lip sync:**
  - Mouth shapes lead the audio by 2 frames.
  - Each shape stays at least 3 frames.
  - Stressed vowels open about 1.3× wider.
  - The emotion's mouth corners stay on while talking.
  - The listener's mouth stays still.
- **Gestures:**
  - Nod: about 0.4 s.
  - Shake: 3 cycles.
  - Recoil: 5–10° back.
  - Double take: look → look away → beat (about 10 frames) → snap back + shock take.

## Sources
- https://schoolofmotion.com/blog/how-to-animate-character-takes
- https://www.bloopanimation.com/blinking-animation/
- https://newsletters.animationmentor.com/newsletter/1105/feature_tiptricks.html
- https://newsletters.animationmentor.com/newsletter/0609/feature_geek.html
- https://blog.animschool.edu/tag/animating-eyebrows/
- https://brianlemay.com/Pages/animationschool/animation/lipsyncbook/lipsync.html
- https://www.pluralsight.com/resources/blog/software-development/proven-tips-animating-believable-lip-sync
- https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation
- https://www.paulekman.com/emotions/surprise/
- https://www.paulekman.com/universal-emotions/what-is-contempt/
- https://www.paulekman.com/blog/fake-smile-or-genuine-smile/
- https://www.realeye.io/features/facial-action-coding-system-facs
- https://www.visuallanguagelab.com/2022/03/new-paper-meaning-above-and-in-the-head.html
- https://en.wikipedia.org/wiki/Manga_iconography
- https://www.cartoonbrew.com/tv/the-dos-and-donts-of-storyboarding-10-tips-from-cartoon-network-artists-193400.html
- https://indiantelevision.com/news-headline/hungama-tv-clocks-its-highest-ratings-doraemon-shinchan-key-drivers-0-060911/
