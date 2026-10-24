"""Offline smoke test: build a Short from synthetic assets (no API calls, no credits).
Proves the deterministic half of the pipeline: motion, cuts, captions, mixing, QA."""
import sys, wave, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shorts.render.captions import Word, write_ass
from shorts.render import assemble as A
from shorts.qa.media import check_video

out = Path("build/smoke"); out.mkdir(parents=True, exist_ok=True)
SR = 48000
text = ("In 1518 hundreds of people in Strasbourg started dancing and could not stop. "
        "Nobody knows exactly why. This is a test of captions timing and motion.").split()
# fake word timings ~2.6 words/sec
words, t = [], 0.15
for w in text:
    d = 0.18 + 0.045 * len(w)
    words.append(Word(w, t, t + d)); t += d + 0.07
    if w.endswith('.'): t += 0.25
dur = t + 0.4

def tone_track(words, total):
    a = np.zeros(int(total * SR))
    for w in words:
        s, e = int(w.start * SR), int(w.end * SR)
        n = e - s; tt = np.arange(n) / SR
        env = np.sin(np.pi * np.arange(n) / n)
        a[s:e] += 0.35 * env * np.sin(2 * np.pi * (180 + 20 * len(w.text)) * tt)
    return a
def write_wav(p, a):
    a = np.clip(a, -1, 1); pcm = (a * 32767).astype('<i2')
    with wave.open(str(p), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(pcm.tobytes())
write_wav(out / "narration.wav", tone_track(words, dur))
tt = np.arange(int(dur * SR)) / SR
write_wav(out / "music.wav", 0.25 * (np.sin(2*np.pi*110*tt) + np.sin(2*np.pi*164.8*tt)) / 2)

font = ImageFont.truetype("assets/fonts/Inter-Black.otf", 110)
colors = [(40, 60, 120), (120, 50, 40), (30, 100, 70), (90, 40, 110)]
motions = ["zoom_in", "pan_left", "zoom_out", "pan_up"]
clips = []; scene_len = dur / 4
for i, c in enumerate(colors):
    img = Image.new("RGB", (1536, 2048), c); d = ImageDraw.Draw(img)
    for k in range(0, 2048, 128): d.line([(0, k), (1536, k + 400)], fill=tuple(min(255, x + 40) for x in c), width=10)
    d.text((140, 900), f"TEST SCENE {i+1}", font=font, fill=(255, 255, 255))
    p = out / f"img{i}.png"; img.save(p)
    clips.append(A.render_still(p, scene_len, motions[i], out / f"clip{i}.mp4"))
t0 = time.time()
video = A.concat(clips, out / "video.mp4")
audio = A.mix_audio(A.AudioPlan(out / "narration.wav", out / "music.wav"), dur, out / "mix.wav")
ass = write_ass(words, out / "captions.ass", overlays=[(0.0, 2.0, "THE DANCING PLAGUE")])
final = A.finalize(video, audio, ass, out / "final.mp4")
print(f"rendered in {time.time()-t0:.1f}s ->", final)
rep = check_video(final, expected_narration_s=words[-1].end)
for c in rep.checks: print(("PASS" if c.ok else ("FAIL" if c.hard else "WARN")), c.name, "-", c.detail)
print("OVERALL", "PASS" if rep.passed else "FAIL")
