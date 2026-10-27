# Lessons learned (24–28 Oct 2026)

Everything we learned so far, kept in one place, so it is never lost.
It covers both formats we tried:
- **Secret Smart Stuff** (English explainers): the live format.
- **Bhaukaali Toons / Sab Theek Hai** (Hindi cartoon sketches): dropped on 28 Oct 2026.

How each item is marked:
- **[data]** we measured it on our own channel.
- **[owner]** the owner said it.
- **[research]** an outside source says it (see `docs/research/`).
- **[hypothesis]** our best guess, not yet tested.

## 1. What the results say

| Video | Channel | Views | Cost to make | What it tells us |
|---|---|---|---|---|
| Onigiri v9 (explainer, English, 36 s) | Secret Smart Stuff | 1,196 views and 34 likes in ~2.5 days | ~$1.00 for the final version ($5.38 including v1–v8) | The explainer format can find an audience. **[data]** |
| Ep 1 "Naai ko 'na'…" (sketch, Hindi, 46 s) | Bhaukaali Toons (new, 0 subscribers) | 4 views in the first ~4 h | ~$5+ per episode, plus many re-dos | A brand-new channel plus a calm opening got almost no test audience. **[data]** |

- **Comedy is expensive to make well.** Sketch scripts needed many judge rounds, new art and voice re-takes; four pilot
  runs cost $13. Several gate failures produced nothing. **[data]**
- **Explainers are cheap and repeatable.** A single-pass explainer costs about $0.45–1.00. **[data]**
- **One video is noise.** Judge a format on 10+ videos, against the channel's own median, never on one video's raw
  views. **[research: Salganik et al.; YouTube Help]**

## 2. Hook and retention (applies to every Short)

- The voice must speak in the first second, and frame 1 must show something specific and strange. Viewers decide in
  the first second or two. **[research; data: the Ep 1 calm opening got swiped]**
- No text card over the opening. It breaks the loop and measured worse. **[research: Emplifi; data: onigiri v8]**
- Check "viewed vs swiped away" in YouTube Studio at 48 h. If most people swiped, the opening is the problem.
  **[research: YouTube]**
- Every video loops: the last line leads into the first, there is no silent tail, and the music runs across the
  join. **[owner; data]**

## 3. Writing

- Story or explanation first, polish second. Simple premises pass the checks; complicated ones fail on logic.
  **[data: sketch pilots]**
- 1–2 light, kind, witty lines per explainer, with no new facts in them. The owner wants a lighter tone.
  **[owner]**
- Every fact needs a source. Use conservative wording ("one common explanation is…").
  **[playbook rule; protects trust]**
- Every picture must show exactly what the words say. **[owner, v2]**
- Titles: no loaded or sensitive words. The judge flagged "naai" as possibly caste-linked.
  **[hypothesis: hurts reach]**

## 4. Quality gates that worked

- **Check before spending.** Run deterministic checks (length, words, hook, sources, banned words) before paying for
  voice or images. **[data]**
- **Independent reviewer.**
  - Use a model separate from the writer.
  - Split problems into *blocking* vs *notes*.
  - Re-checks look only at changed lines.
  - Without this, the reviewer kept inventing new problems and nothing ever passed. **[data: sketch pilots 2–3]**
- **Calibrate the reviewer against the owner.** Its scores must rank the owner-approved work above the rejected
  work. LLM judges favour their own writing and the first option shown. **[research: Zheng 2023; Panickssery 2024]**
- **Owner fixes are minimal edits.** Change only what he asked. Unchanged pictures and voice are reused, so a fix
  costs cents. **[owner: "fix the same story, don't write a new one"]**
- **Claude's own check before anything reaches the owner:**
  - frames from every shot at full size;
  - a contact sheet;
  - first frame vs last frame (the loop);
  - loudness;
  - a 3× loop preview. **[owner; data: caught most defects]**

## 5. Audio

- **Never cut into the first word.** Keep about 0.12 s of lead-in before the aligned first word. A 0.05 s cut
  clipped first words; the owner flagged it 3 times. **[owner; data]**
- **Never speed up or clip lines to hit a length.** Cut a weaker line instead. **[owner]**
- Music sits well under the voice (about 10 LU below speech) and is cross-faded across the loop.
  **[research: AES/Torcoli 2019; data]**
- Mix in numpy with exact lengths. ffmpeg filter graphs dropped or hung the music. **[data: onigiri v8–v9]**
- Loudness about −14 LUFS, true peak below −1 dBFS. **[platform norm]**
- Only original music (licensed tracks cut revenue share). Sound effects must be sparse and fit the moment.
  **[owner; YouTube]**

## 6. Captions and on-screen text

- At most 42 characters per caption line and about 20 characters per second of reading speed.
  **[research: Netflix timed-text guide]**
- At most 3 pointers or circles per video, in varied styles, and mostly none. **[owner, v7]**
- Never ask the image model for text or numbers; code draws them. **[data]**

## 7. Costs and budget

- **Monthly cap $45** (variable AI spend; ElevenLabs plan separate).
  - October used about $39, mostly on the sketch show.
  - The cap resets on the 1st.
- **The stills format is the default.**
  - Real-motion AI clips add about $2.50–3.50 per video (escalator test: $3.49 in total).
  - They are only an experiment. **[data]**
- Weekly caps on new art stopped runaway spend in the sketch period. Keep caps on anything open-ended.
  **[data]**
- BFL image credits must be topped up before they run out; a top-up is a manual payment by the owner.
- Most money was wasted on work the owner didn't like. The cheapest saving is getting the brief right first time:
  owner notes go into the writer's prompt every run. **[data]**

## 8. Systems

- **The YouTube login must belong to the right channel.**
  - Uploads and analytics now refuse to run when the login is for any channel other than the one in
    `config/channel.yaml`.
  - Before this guard, a swapped login could have posted to the wrong channel.
- **The login is one tap.**
  - The owner sends `/ytlogin` to the studio bot, then taps Allow.
  - The token is stored encrypted in the studio Worker's store.
  - Nothing to copy or paste.
- **GitHub from Claude's sessions:**
  - GraphQL and the Actions secrets API are blocked, so use the REST API.
  - The dispatch token cannot write secrets.
- **GitHub releases** hold at most 1,000 files, so renders roll over to a new release.
- **Pronunciation check is not possible yet.** ElevenLabs speech-to-text needs a permission the current API key
  lacks. Explainers use the voice service's own word timings instead.
- **The built-in browser loses sign-ins** between devices. Google, GitHub, Vercel and Cloudflare all needed a
  fresh sign-in by the owner on 28 Oct.

## 9. Working with the owner

- Short sentences, simple words, points. Results, not process updates. **[owner]**
- Ask only for real decisions or access. Otherwise decide, do it, and say what was decided. **[owner]**
- Never send anything that wasn't checked frame by frame. Never claim something works before it has been tested.
  **[owner]**
- Flag cost and policy risks before spending. **[owner]**

## Where the old material lives

| What | Where |
|---|---|
| Sketch pipeline code (writers' room, judge, gates, puppet engine, art) | git branch `archive/bhaukaali-toons` |
| Sketch docs: template, rubric, show bible, audit, craft cards, comedy/screenwriting/animation research | `docs/archive/bhaukaali-toons/` |
| Retention, platform and LLM-judging research (still applies) | `docs/research/R2_*`, `docs/research/R4_*`, `docs/research/BIBLIOGRAPHY.md`, `research/` |
| Bhaukaali analytics, uploads and owner notes | `*_bhaukaali` tables in the state database |
