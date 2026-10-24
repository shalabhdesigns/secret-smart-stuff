"""Build burned-in captions (ASS) from word timings.

Word timings come from the TTS provider's alignment data, so captions follow
the real voiceover rather than an estimate.

Layout follows the Shorts "safe area": the bottom ~22% (title, channel, music
line) and the right ~14% (like/comment/share buttons) are covered by the
player UI on phones, so captions sit in the middle band.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

W, H = 1080, 1920


@dataclass
class Word:
    text: str
    start: float  # seconds
    end: float


def chunk_words(words: list[Word], max_words: int = 3, max_chars: int = 18,
                max_gap: float = 0.35) -> list[list[Word]]:
    """Group words into short caption chunks (2-3 words reads best on Shorts)."""
    chunks: list[list[Word]] = []
    cur: list[Word] = []
    for w in words:
        too_long = len(" ".join(x.text for x in cur + [w])) > max_chars
        gap = cur and (w.start - cur[-1].end) > max_gap
        ends_sentence = cur and cur[-1].text[-1:] in ".?!"
        if cur and (len(cur) >= max_words or too_long or gap or ends_sentence):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def write_ass(words: list[Word], out: Path, font: str = "Inter", font_size: int = 86,
              primary: str = "&H00FFFFFF", highlight: str = "&H0000E5FF",
              y_center: int = 1180, uppercase: bool = True,
              overlays: list[tuple[float, float, str]] | None = None) -> Path:
    """Write an .ass subtitle file.

    The word being spoken is highlighted (karaoke style) - a common retention
    aid on Shorts. `overlays` are optional (start, end, text) headline cards
    shown near the top (e.g. the first-2-seconds hook text).
    """
    style_main = (
        f"Style: Main,{font},{font_size},{primary},{primary},&H00000000,&H80000000,"
        "-1,0,0,0,100,100,0,0,1,6,2,5,100,160,0,1"
    )
    style_top = (
        f"Style: Top,{font},{int(font_size * 0.8)},{primary},{primary},&H00000000,&HA0000000,"
        "-1,0,0,0,100,100,0,0,3,4,0,8,90,150,260,1"
    )
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {W}",
        f"PlayResY: {H}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        style_main,
        style_top,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    pos = f"{{\\an5\\pos({(W - 60) // 2},{y_center})}}"
    for chunk in chunk_words(words):
        start, end = chunk[0].start, max(chunk[-1].end, chunk[0].start + 0.25)
        # one event per word so the active word can be highlighted
        for i, w in enumerate(chunk):
            w_end = chunk[i + 1].start if i + 1 < len(chunk) else end
            parts = []
            for j, x in enumerate(chunk):
                t = _esc(x.text.upper() if uppercase else x.text)
                parts.append(f"{{\\c{highlight}}}{t}{{\\c{primary}}}" if j == i else t)
            lines.append(
                f"Dialogue: 0,{_ts(w.start)},{_ts(w_end)},Main,,0,0,0,,{pos}{' '.join(parts)}"
            )
    for (s, e, text) in overlays or []:
        lines.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},Top,,0,0,0,,{_esc(text)}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def words_from_char_alignment(chars: list[str], starts: list[float], ends: list[float]) -> list[Word]:
    """Convert ElevenLabs-style character alignment into word timings."""
    words: list[Word] = []
    buf, ws, we = "", None, None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if buf:
                words.append(Word(buf, ws, we))  # type: ignore[arg-type]
            buf, ws, we = "", None, None
            continue
        if ws is None:
            ws = s
        buf += c
        we = e
    if buf:
        words.append(Word(buf, ws, we))  # type: ignore[arg-type]
    return words
