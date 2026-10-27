# Content Strategy — Hidden Design of Everyday Things

Date: 24 Oct 2026 · Status: **draft for owner review** (naming and voice still to pick)

Everything here is a starting hypothesis. The pilot (section 10) decides what stays.

---

## 1. Positioning

| | |
|---|---|
| **One-line promise** | "Every everyday object has a reason. We show you the reason in under a minute." |
| **Audience** | Curious adults and older teens (16–40). English speakers in the US, UK, Canada, Australia and India. Not made for kids. |
| **What viewers get, every time** | One surprising reason, shown clearly with a diagram, that they can repeat to a friend. |
| **Different from the leaders** | Leaders mostly *tell* the history. We *show why the shape works* with an animated blueprint, and we cover objects from everywhere, not only Western ones. |
| **Never** | Fake facts, rage bait, logos as the subject, "you won't believe" clickbait, politics, religion, health claims. |

## 2. Identity

**Name direction** (owner picks; handle availability is checked when the channel is created):

| Option | Feel |
|---|---|
| **Hidden by Design** | Clear promise, design-led |
| **The Reason Shape** | Short, unusual, memorable |
| **Everyday Blueprint** | Matches the visual style directly |
| **Made That Way** | Plain and friendly |

**Visual style — "living blueprint":**
- An object image (AI-generated, clean studio or real-life setting) is the hero shot.
- Blueprint-style line callouts are drawn on top by code: arrows, measurements, cutaways, exploded views.
- Palette: warm paper white, ink navy, one accent colour (signal orange) for the "aha" detail.
- Captions: bold sans-serif, 2–3 words at a time, with the spoken word highlighted, in the safe middle band of the screen.
- Variety rule: layout, object setting, motion and diagram type change every video, so the channel never looks like one template.

**Voice:** one calm, curious, slightly warm narrator. Speaks like a friend who just noticed something cool, not like an announcer. Short sentences. No shouting.

## 3. Content pillars

| Pillar | Example | Share at start |
|---|---|---|
| **Why does X have Y?** (a design detail and its reason) | Why do jeans have a tiny pocket? | 40% |
| **You walk past this every day** (infrastructure) | Why are there stones beside railway tracks? | 20% |
| **Same thing, different country** | How kettles, plugs or brooms differ around the world, and why | 15% |
| **The first version** (how an object started and changed) | What the first toothbrush looked like | 15% |
| **From India and Asia, for the world** | Why a pressure-cooker whistle works the way it does | 10% (also mixed into the others) |

## 4. Formats, length and pacing

- **Length:** start at 25–40 seconds. Test 45–55 seconds for richer stories. (Shorts can run to 3 minutes, but long Shorts are not the starting bet.)
- **Structure:**
  1. **0–2 s — Hook:** the question, plus the object on screen with a callout on the odd detail.
  2. **2–8 s — Stakes:** why it's odd, or the wrong guess most people make.
  3. **8–30 s — Reveal:** the reason, shown step by step with the diagram. A new visual every 2–3 seconds.
  4. **Last 3–5 s — Payoff + loop:** a one-line "so next time you see X…", written to flow back into the first line.
- **Pacing:** a cut, zoom or new callout at least every 3 seconds. Visual change must match the words being spoken.
- **Weekly long-form:** an 8–12 minute compilation of the week's Shorts, re-edited with transitions. This builds watch hours for the long-form route to the Partner Program.

## 5. Hook rules

- Open on the **object and the question at the same time**. No intro, no channel name, no "did you know".
- Name the **specific detail** ("that tiny pocket", "those stones"), never a vague "this object".
- Every hook is scored with `hookscore.py` (from the YouTube agent skill). Write five, keep the best two, and use the winner. The score is a warning light, not a prediction.
- On-screen text in the first 2 seconds uses **different words** from the spoken line.
- Hook types to rotate: the odd detail · the wrong guess · the "you've used this 1,000 times" · the "different country" contrast · the "this was invented for something else" twist.

## 6. Retention and storytelling

- **One question per Short.** Don't answer two.
- **Delay the answer a little.** First show the wrong guess, then the real reason.
- **Show, then say.** The diagram appears just before the narrator explains it.
- **End on a real payoff.** Never "follow for part 2" unless part 2 exists and is scheduled.
- **Loop.** The last line leads naturally back into the first.

## 7. Trends without depending on them

| Share | Type | Source |
|---|---|---|
| 80% | **Evergreen objects** | Object inventory (household, street, transport, tools, clothing, kitchen) |
| 15% | **Calendar-timed** | Seasons and events (Diwali lamps in Oct/Nov, back-to-school stationery, monsoon umbrellas, winter heaters) |
| 5% | **Moment-driven** | An everyday object suddenly in the conversation (a viral product, a search spike). Only if it is non-political and not news. |

A trend only enters the backlog if it also passes the normal topic score. Trend momentum is one input, not a reason on its own.

## 8. Getting original ideas (not copying competitors)

1. **Object inventory first.** A growing list of everyday objects, tagged by place (home, street, travel) and region.
2. **Angle matrix.** Each object × each pillar gives several candidate angles.
3. **Question mining.** Real questions from search suggestions, Reddit "why is…" threads and our own comments.
4. **Competitors are a duplicate check only.** Their outliers tell us which objects people care about. If they have covered an object, we either take a clearly different angle or skip it. We never reuse their scripts or structure.
5. **Sources before scripts.** An idea goes forward only if at least two credible sources support the reason. Otherwise it's dropped or framed honestly ("one popular theory is…").

## 9. Quality bar (nothing below this gets published)

A Short must pass **all hard gates** and score **≥ 7/10 on the review score**.

**Hard gates (automatic):**
- Every factual claim is linked to at least one source in the fact sheet. The main claim needs two.
- The media checks pass: 1080×1920, 30 fps, loudness about −14 LUFS, no clipping, no silence over 1.2 s, no black frames.
- Captions match the voiceover word timings and sit inside the safe area.
- No logos, trademarks as the subject, real people's faces, or copyrighted music.
- Not a duplicate: the topic or angle is not too similar to anything already published.
- The title and description match what the video actually says.

**Review score (separate AI review, then the owner):**
- Hook clarity (0–2), payoff delivered (0–2), visuals match narration (0–2), accuracy confidence (0–2), originality versus our own past videos and competitors (0–2).

**Plus the owner's approval** before upload, during the first phase.

## 10. Pilot testing plan

- **Pilot size:** 30 Shorts, published about 1 per day.
- **What we vary:**
  - Pillar (all five used).
  - Length: around 30 s vs around 50 s.
  - Hook type: odd detail vs wrong guess.
- **What we keep fixed:** voice, visual style, posting slot. This isolates what matters.
- **How we judge:**
  - Compare each Short with the channel's own median, at the same age (7 days).
  - Look at "viewed vs swiped away" in Studio, average percentage viewed, and subscribers gained per 1,000 views.
  - No conclusions from fewer than about 1,000 views per video.
- **After 30:** double down on the top two formats, drop the bottom one, and test one new idea each week.
- **Kill or pivot rule:** see section 10 of the niche report.

## 11. Risks to watch

| Risk | Warning sign | What we do |
|---|---|---|
| **Creative fatigue** (it starts to feel samey) | Average % viewed drops for 2 weeks in a row | Rotate the pillar mix; add a new format |
| **Audience mismatch** (Indian objects don't land globally) | India-pillar Shorts trail the median by more than 40% | Frame them as "the world does it differently" contrasts, or reduce the share |
| **Trend dependence** | More than 20% of views come from moment-driven topics | Pull back to evergreen |
| **Looking like competitors** | Comments say "copy of…" | Change the visual style and the angle selection |
| **Views without subscribers** (common for fact channels) | Under 1 subscriber per 1,000 views | Add series hooks ("part of our kitchen series") and the weekly compilation |
| **Views without money** | Feb 2027 thresholds out of reach | Lean on Shopping or affiliates (from 500 subs), sponsors and long-form |
