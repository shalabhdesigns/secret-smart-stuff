"""Official GTA VI video clips (owner, 16 Nov 2026: "re-use the clips like the reference Shorts do").

Source: Rockstar's own downloads page (https://www.rockstargames.com/VI/downloads), "All 9 Clips" zip:
launch trailer, extended look, pre-load video, cover-art animation and character clips.
Used as short excerpts under our own narration and captions (commentary), muted, credited to Rockstar.
Never AI-edited, never mirrored or disguised.

Like the screenshots, the files are NOT committed (public repo): `sync()` runs on a GitHub runner and the
workflows keep assets/official/clips/ in the Actions cache. `assets/official/shots.json` (committed) lists
every shot (clip, start, end) with what it shows, so the writer can pick one shot per beat.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets" / "official"
CLIPS = BASE / "clips"
ZIP_URL = "https://media-rockstargames-com.akamaized.net/VI/downloads/videos/GTAVI_Videos.zip"
CREDIT = "Footage and images: Rockstar Games (official Grand Theft Auto VI trailers and screenshots), used for commentary."


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", Path(name).stem.lower()).strip("_")[:40]


def _dur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


VIDEOS_BASE = "https://media-rockstargames-com.akamaized.net/VI/downloads/videos"
VIDEOS = {   # Rockstar's own direct downloads (rockstargames.com/VI/media/videos), 16 Nov 2026
    "trailer_1": "GTAVI_Trailer_1",
    "trailer_2": "GTAVI_Trailer_2",
    "launch_trailer": "GTAVI_Launch_Trailer",
    "extended_look": "GTAVI_An_Extended_Look",
    "preload_now": "GTAVI_Pre-Load_Now",
    "cover_art": "GTAVI_Official_Cover_Art_Landscape",
}


def discover() -> dict:
    """New official videos on Rockstar's GTA VI media page (checked daily; Rockstar adds launch and post-launch
    videos there). Returns {slug: file name} including the known ones."""
    import urllib.request
    found = dict(VIDEOS)
    try:
        req = urllib.request.Request("https://www.rockstargames.com/VI/media/videos",
                                     headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.rockstargames.com/"})
        html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
        for name in dict.fromkeys(re.findall(r"/VI/downloads/videos/([A-Za-z0-9_.-]+)/\1\.mp4", html)):
            if name not in found.values():
                found[_slug(name.replace("GTAVI_", ""))] = name
                print(f"  new official video: {name}")
    except Exception as e:  # noqa: BLE001
        print(f"  media page not read: {e}")
    return found


def sync() -> dict:
    """Stream each official video straight into a 1080p H.264 copy (no audio) in assets/official/clips/."""
    CLIPS.mkdir(parents=True, exist_ok=True)
    VIDEOS.update(discover())
    for slug, name in VIDEOS.items():
        dst = CLIPS / f"{slug}.mp4"
        if dst.exists() and _dur(dst) > 5:
            continue
        url = f"{VIDEOS_BASE}/{name}/{name}.mp4"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-user_agent", "Mozilla/5.0",
                            "-headers", "Referer: https://www.rockstargames.com/\r\n", "-i", url, "-an",
                            "-vf", "scale=-2:1080:flags=lanczos,fps=30", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "21", "-pix_fmt", "yuv420p", str(dst)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  {slug}: FAILED {r.stderr[-300:]}")
            dst.unlink(missing_ok=True)
            continue
        print(f"  {slug}: {_dur(dst):.1f} s")
    for old in CLIPS.glob("*_video_clip.mp4"):
        old.unlink()                       # the 1-second character clips from the zip are too short to use
    return {"count": len(list(CLIPS.glob("*.mp4")))}


def sync_zip() -> dict:
    """(Unused since 16 Nov 2026: the zip only holds 1-second character clips.)"""
    CLIPS.mkdir(parents=True, exist_ok=True)
    have = sorted(CLIPS.glob("*.mp4"))
    if len(have) >= 5:
        print(f"official clips already here: {len(have)}")
        return {"count": len(have)}
    z = CLIPS / "_videos.zip"
    if not z.exists():
        subprocess.run(["curl", "-sSL", "--retry", "3", "-A", "Mozilla/5.0", "-e", "https://www.rockstargames.com/",
                        "-o", str(z), ZIP_URL], check=True)
    print(f"zip: {z.stat().st_size / 1e6:.0f} MB")
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            if info.is_dir() or not re.search(r"\.(mp4|mov|m4v|webm)$", info.filename, re.I):
                continue
            src = CLIPS / ("_src_" + Path(info.filename).name)
            with zf.open(info) as fi, open(src, "wb") as fo:
                while chunk := fi.read(1 << 22):
                    fo.write(chunk)
            dst = CLIPS / f"{_slug(info.filename)}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-an",
                            "-vf", "scale=-2:1080:flags=lanczos,fps=30", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "19", "-pix_fmt", "yuv420p", str(dst)], check=True)
            src.unlink()
            print(f"  {dst.name}: {_dur(dst):.1f} s")
    z.unlink()
    return {"count": len(list(CLIPS.glob("*.mp4")))}


def detect_shots(min_len: float = 0.9) -> dict:
    """Cut points by scene change; returns {clip: [[start, end], ...]}."""
    shots = {}
    for p in sorted(CLIPS.glob("*.mp4")):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-vf", "select='gt(scene,0.30)',showinfo",
                            "-f", "null", "-"], capture_output=True, text=True)
        cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]
        d = _dur(p)
        pts = [0.0] + [c for c in cuts if 0 < c < d] + [d]
        out, s = [], pts[0]
        for e in pts[1:]:
            if e - s >= min_len:
                out.append([round(s, 2), round(e, 2)])
                s = e
        shots[p.stem] = out
    return shots


def contact_sheets(shots: dict, out: Path, per: int = 20) -> list[Path]:
    """Middle frame of every shot, labelled clip@start-end, for describing the shots."""
    from PIL import Image, ImageDraw
    out.mkdir(parents=True, exist_ok=True)
    items = [(c, s, e) for c, lst in shots.items() for s, e in lst]
    tmp = out / "_f.jpg"
    sheets = []
    for n in range(0, len(items), per):
        chunk = items[n:n + per]
        tw, th = 384, 216
        sheet = Image.new("RGB", (tw * 4, (th + 24) * ((len(chunk) + 3) // 4)), "white")
        d = ImageDraw.Draw(sheet)
        for i, (c, s, e) in enumerate(chunk):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{(s + e) / 2:.2f}", "-i",
                            str(CLIPS / f"{c}.mp4"), "-frames:v", "1", "-vf", f"scale={tw}:{th}", str(tmp)], check=True)
            x, y = (i % 4) * tw, (i // 4) * (th + 24)
            sheet.paste(Image.open(tmp), (x, y))
            d.rectangle([x, y + th, x + tw, y + th + 24], fill="yellow")
            d.text((x + 4, y + th + 6), f"{c}@{s:.1f}-{e:.1f}", fill="black")
        f = out / f"shots_{n // per:02d}.jpg"
        sheet.save(f, quality=82)
        sheets.append(f)
    tmp.unlink(missing_ok=True)
    return sheets


DESCRIBE = """These {n} numbered frames are shots from Rockstar's official GTA VI trailers (one frame per shot).
For EACH number say in 6-14 plain words what the shot shows (who/what, place, action, time of day), so a video
editor can pick it to match a line like "the box has no disc" or "Vice City at night". Name Jason or Lucia only if
clearly them (Jason: man with short dark hair and beard; Lucia: woman with long dark hair).
Mark "avoid" with a short reason when the shot is: a title card, logo, credits or mostly on-screen text; gun pointed
at a person, shooting, blood or killing; nudity or sexual dancing; a black/blank or very blurry frame.
Return JSON only: {{"shots": [{{"n": 1, "shows": "...", "avoid": ""}}, ...]}}. Never use double quotes inside the
text values (write 'like this' instead)."""


def describe(shots: dict, per: int = 8, have: dict | None = None) -> dict:
    """Describe every shot with Claude (vision) so the writer can choose footage by meaning. Shots already in
    `have` are skipped (16 Nov 2026: 8 of 18 batches of 16 came back as broken JSON; batches are now 8)."""
    import io
    import os
    from PIL import Image, ImageDraw
    from shorts.config import load
    from shorts.providers.llm import AnthropicLLM
    cfg = load()
    llm = AnthropicLLM(os.environ["ANTHROPIC_API_KEY"], cfg.pipeline["providers"]["llm"])
    have = have or {}
    items = [(c, s, e) for c, lst in shots.items() for s, e in lst
             if f"{c}_{int(s * 10):05d}" not in have and c in VIDEOS]
    out: dict[str, dict] = dict(have)
    tmp = CLIPS / "_f.jpg"
    usd = 0.0
    for n in range(0, len(items), per):
        chunk = items[n:n + per]
        tw, th = 480, 270
        sheet = Image.new("RGB", (tw * 4, th * ((len(chunk) + 3) // 4)), "black")
        d = ImageDraw.Draw(sheet)
        for i, (c, s, e) in enumerate(chunk):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{(s + e) / 2:.2f}", "-i",
                            str(CLIPS / f"{c}.mp4"), "-frames:v", "1", "-vf", f"scale={tw}:{th}", str(tmp)], check=True)
            x, y = (i % 4) * tw, (i // 4) * th
            sheet.paste(Image.open(tmp), (x, y))
            d.rectangle([x, y, x + 34, y + 26], fill="yellow")
            d.text((x + 6, y + 6), str(i + 1), fill="black")
        buf = io.BytesIO()
        sheet.save(buf, "JPEG", quality=80)
        try:
            r = llm.ask(DESCRIBE.format(n=len(chunk)), images=[buf.getvalue()], max_tokens=2500,
                        model=cfg.pipeline["providers"]["llm"]["model_script"])
            usd += r.usd
            got = {int(x["n"]): x for x in (r.data or {}).get("shots", [])}
        except Exception as ex:  # noqa: BLE001
            print(f"  describe batch {n // per}: {ex}")
            got = {}
        for i, (c, s, e) in enumerate(chunk):
            g = got.get(i + 1) or {}
            if not g.get("shows"):
                continue
            sid = f"{c}_{int(s * 10):05d}"
            out[sid] = {"clip": c, "start": s, "end": e, "shows": g["shows"].strip()}
            if g.get("avoid"):
                out[sid]["avoid"] = g["avoid"].strip()
    tmp.unlink(missing_ok=True)
    print(f"described {len(out)} of {len(items)} shots for ${usd:.2f}")
    return out


def shots_catalogue() -> dict:
    f = BASE / "shots.json"
    return json.loads(f.read_text()).get("shots", {}) if f.exists() else {}


def shots_text() -> str:
    """One line per usable shot, for the writer: `id | seconds | what it shows`."""
    return "\n".join(f"{k} | {v['end'] - v['start']:.1f}s | {v['shows']}"
                     for k, v in shots_catalogue().items() if not v.get("avoid"))


def best_match(text: str, exclude: set | None = None) -> str | None:
    """The usable shot whose description shares the most words with `text`."""
    words = {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}
    best, best_s = None, -1
    for sid, it in shots_catalogue().items():
        if it.get("avoid") or (exclude and sid in exclude) or it["end"] - it["start"] < 1.2:
            continue
        sc = len(words & set(re.findall(r"[a-z0-9]+", it["shows"].lower())))
        if sc > best_s:
            best, best_s = sid, sc
    return best


def _letterbox(src: Path, t: float) -> str:
    """Crop filter that removes cinema black bars (trailers are 2.39:1 inside 16:9), or '' if none."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{t:.2f}", "-i", str(src), "-t", "1.5",
                        "-vf", "cropdetect=24:2:0", "-f", "null", "-"], capture_output=True, text=True)
    found = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not found:
        return ""
    w, h, x, y = map(int, found[-1])
    return f"crop={w}:{h}:{x}:{y}," if 300 < h < 1040 else ""


def _clean_range(src: Path, start: float, end: float, min_piece: float = 0.9) -> tuple[float, float]:
    """17 Nov 2026: detect_shots glues a cut piece shorter than 0.9 s onto the START of the next shot, so a 0.3 s
    flash of another scene (the same face) opened one city shot used in every GTA video, and YouTube picked that
    face as the thumbnail of 3 videos. Find the scene cuts inside [start, end] and keep the longest stretch made only
    of pieces at least `min_piece` long (a cut between two long pieces is a normal run-on into the next shot)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.2f}", "-t", f"{max(end - start, 0.1):.2f}",
                        "-i", str(src), "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    cuts = sorted(float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr))
    # 18 Nov 2026: a 2-frame flash in the LAST 0.05 s slipped through (it became the held last frame), so cuts right
    # at the edges count too
    pts = [0.0] + [c for c in cuts if 0.01 < c < end - start - 0.01] + [end - start]
    best, run_s, run_e = (0.0, 0.0), None, None
    for a, b in zip(pts, pts[1:]):
        if b - a >= min_piece:
            run_s = a if run_s is None else run_s
            run_e = b
            if run_e - run_s > best[1] - best[0]:
                best = (run_s, run_e)
        else:
            run_s = run_e = None
    if best[1] - best[0] <= 0:                     # nothing long enough: keep the whole range
        return start, end
    s0 = start + best[0] + (0.04 if best[0] > 0 else 0.0)
    e0 = start + best[1] - (0.04 if best[1] < end - start else 0.0)
    return s0, e0


def _hard_cuts(src: Path, start: float, end: float) -> list[float]:
    """Cuts inside [start, end] (seconds from start), found two ways: ffmpeg's scene score and a plain frame-difference
    test. 18 Nov 2026: the scene score missed a hard cut from a face to a night aerial (trailer_1 at 31.0 s), so a
    1-second shot of a stranger opened 'trailer_1_00300' in five videos."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.2f}", "-t", f"{max(end - start, 0.1):.2f}",
                        "-i", str(src), "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    cuts = {round(float(m), 2) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)}
    w, h, fps = 32, 18, 15
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{max(end - start, 0.1):.2f}",
                          "-i", str(src), "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    n = len(raw) // (w * h)
    prev = None
    for i in range(n):
        fr = raw[i * w * h:(i + 1) * w * h]
        if prev is not None:
            diff = sum(abs(a - b) for a, b in zip(fr, prev)) / (w * h)
            if diff > 28:
                t = round(i / fps, 2)
                if all(abs(t - c) > 0.12 for c in cuts):
                    cuts.add(t)
        prev = fr
    return sorted(cuts)


def _shot_piece(src: Path, start: float, end: float) -> tuple[float, float]:
    """The piece of a catalogued shot that its description is about: shots are described from their MIDDLE frame,
    so keep the stretch between the cuts around the middle (missed cuts merged a stranger's face into a city shot)."""
    cuts = [c for c in _hard_cuts(src, start, end) if 0.01 < c < end - start - 0.01]
    mid = (end - start) / 2
    a = max([0.0] + [c for c in cuts if c <= mid])
    b = min([end - start] + [c for c in cuts if c > mid])
    return start + a + (0.04 if a > 0 else 0.0), start + b - (0.04 if b < end - start else 0.0)


def segment(shot_id: str, out: Path, seconds: float) -> Path:
    """The shot as its own muted file, at least `seconds` long (runs on into the next shot if it is shorter).
    Black bars are cropped off so the vertical frame is all picture."""
    sh = shots_catalogue()[shot_id]
    src = CLIPS / f"{sh['clip']}.mp4"
    if not src.exists():
        raise FileNotFoundError(f"official clip {sh['clip']} is not on this runner (run the official sync)")
    length = max(seconds + 0.3, 1.0)
    start, own_end = _shot_piece(src, sh["start"], sh["end"])
    start += 0.02
    # 16 Nov 2026: a beat longer than its shot ran on into the next shots, once into a banned one. Now it may only
    # run on into the following shots that are described and allowed; then it slows down (max 1.6x); then holds.
    cat = shots_catalogue()
    same = sorted((v for v in cat.values() if v["clip"] == sh["clip"]), key=lambda v: v["start"])
    end = own_end
    for v in same:
        if own_end < sh["end"] - 0.1:
            break                         # the shot itself holds a hidden cut: never run on past it
        if end - start >= length:
            break
        if v["start"] < end - 0.05:
            continue
        if abs(v["start"] - end) > 0.2 or v.get("avoid"):
            break
        end = v["end"]
    start, end = _clean_range(src, start, end)
    avail = max(0.5, end - start - 0.05)
    vf = f"{_letterbox(src, start)}scale=-2:1080"
    take = min(avail, length)
    if avail < length:
        slow = min(length / avail, 1.6)
        vf += f",setpts={slow:.3f}*PTS"
        rest = length - avail * slow
        if rest > 0.05:
            vf += f",tpad=stop_mode=clone:stop_duration={rest:.2f}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{take:.2f}", "-i", str(src),
                    "-an", "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def still(shot_id: str, out: Path) -> Path:
    """A frame from the middle of the shot (for the cover, focus finding and the loop)."""
    sh = shots_catalogue()[shot_id]
    src = CLIPS / f"{sh['clip']}.mp4"
    t = (sh["start"] + sh["end"]) / 2
    crop = _letterbox(src, sh["start"] + 0.05)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
                    "-vf", f"{crop}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(out)],
                   check=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        sync()
        sh = detect_shots()
        (BASE / "shots_raw.json").write_text(json.dumps(sh, indent=1))
        print("shots:", {k: len(v) for k, v in sh.items()})
        have = shots_catalogue()
        desc = describe(sh, have=have)
        for sid, v in desc.items():      # keep the drug rule (16 Nov 2026)
            if not v.get("avoid") and any(w in v["shows"].lower() for w in ("drug", "meth", "cocaine", " lab")):
                v["avoid"] = "drugs"
        (BASE / "shots.json").write_text(json.dumps(
            {"note": "Shots of Rockstar's official GTA VI videos (rockstargames.com/VI/media/videos), described by "
                     "Claude from one frame each. 'avoid' = never use.", "shots": desc}, indent=1, ensure_ascii=False))
        if len(sys.argv) > 2:
            contact_sheets(sh, Path(sys.argv[2]))
