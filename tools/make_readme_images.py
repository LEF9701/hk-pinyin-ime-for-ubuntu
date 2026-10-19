#!/usr/bin/env python3
"""Draw the explanation images used by README.md and docs/GUIDE.md.

Writes SVG + PNG into docs/img/:
  how-it-works   what happens between a key press and the text you get
  hk-style       the four Hong Kong conventions (glyphs, words, punctuation, dates)
  keys           keyboard cheat sheet

Needs: rsvg-convert (librsvg2-bin), fonts-inter, fonts-noto-cjk
Run:   python3 tools/make_readme_images.py
"""
import pathlib
import subprocess
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"

FONT = "Inter, 'Noto Sans CJK HK', sans-serif"
MONO = "'DejaVu Sans Mono', 'Noto Sans CJK HK', monospace"
INK, MUTED, RULE, PANEL, BG = "#1d1d1f", "#6e6e73", "#d2d2d7", "#f5f5f7", "#ffffff"
ACCENT, ACCENT_BG = "#007aff", "#eaf3ff"
GREEN, GREEN_BG = "#248a3d", "#e8f6ec"
ORANGE, ORANGE_BG = "#c75300", "#fff1e5"
PURPLE, PURPLE_BG = "#8944ab", "#f5ecfa"


def t(x, y, s, size=16, fill=INK, weight=400, anchor="start", font=FONT, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" xml:space="preserve" {extra}>{escape(s)}</text>')


def box(x, y, w, h, fill=PANEL, stroke=RULE, r=14, sw=1.2, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def arrow(x1, y1, x2, y2, color=MUTED):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="2" marker-end="url(#ah)"/>')


def svg(w, h, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/>
  </marker>
  <filter id="sh" x="-10%" y="-30%" width="120%" height="170%">
    <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.16"/>
  </filter>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
{body}
</svg>'''


def candidate_bar(x, y, items, hi=0, dark=False):
    """A macOS-style candidate window."""
    bg, fg = ("#2c2c2f", "#f2f2f7") if dark else ("#fbfbfd", INK)
    parts, cx = [], x + 10
    widths = []
    for i, s in enumerate(items):
        label = f"{i + 1} {s}"
        w = 22 + 19 * len(s) + 8
        widths.append((cx, w, label))
        cx += w + 4
    total = cx - x + 6
    parts.append(box(x, y, total, 46, fill=bg, stroke="#00000022", r=11, extra='filter="url(#sh)"'))
    for i, (bx, w, label) in enumerate(widths):
        if i == hi:
            parts.append(box(bx, y + 6, w, 34, fill=ACCENT, stroke="none", r=7))
        parts.append(t(bx + w / 2, y + 30, label, 17, "#fff" if i == hi else fg, anchor="middle"))
    return "\n".join(parts), total


# ── 1. how it works ─────────────────────────────────────────────────
def how_it_works():
    W, H = 1240, 640
    b = []
    b.append(t(40, 52, "How 港式拼音 turns pinyin into Hong Kong Chinese", 26, weight=700))
    b.append(t(40, 82, "Example: you type  bingxiang  (fridge)", 16, MUTED))

    # stage boxes along the top row
    stages = [
        ("1  You type", "bingxiang", "keyboard", PANEL, RULE, INK),
        ("2  Speller", "bing · xiang", "splits into syllables,\nallows initials (bx)", PANEL, RULE, INK),
        ("3  Dictionary", "冰箱  並向  病象 …", "luna_pinyin + 376 HK\nwords + your words", ACCENT_BG, ACCENT, ACCENT),
    ]
    x = 40
    for i, (title, val, note, fill, stroke, tc) in enumerate(stages):
        b.append(box(x, 110, 360, 150, fill, stroke))
        b.append(t(x + 20, 142, title, 15, tc, 700))
        b.append(t(x + 20, 190, val, 26, INK, 600, font=MONO if i < 2 else FONT))
        for j, line in enumerate(note.split("\n")):
            b.append(t(x + 20, 222 + j * 20, line, 14, MUTED))
        if i < 2:
            b.append(arrow(x + 362, 185, x + 398, 185))
        x += 400

    # down arrow to filters
    b.append(arrow(1060, 262, 1060, 300))

    # filters row (right to left)
    b.append(box(640, 302, 560, 150, GREEN_BG, GREEN))
    b.append(t(660, 334, "4  Hong Kong vocabulary filter", 15, GREEN, 700))
    b.append(t(660, 380, "冰箱  →  雪櫃  |  冰箱", 26, INK, 600))
    b.append(t(660, 414, "HK term goes first, the original stays right after it.", 14, MUTED))
    b.append(t(660, 434, "軟體→軟件 · 網路→網絡 · 計程車→的士 · 什麼→甚麼", 14, MUTED))

    b.append(arrow(638, 377, 602, 377))
    b.append(box(40, 302, 560, 150, ORANGE_BG, ORANGE))
    b.append(t(60, 334, "5  Hong Kong character filter", 15, ORANGE, 700))
    b.append(t(60, 380, "爲 → 為  ·  衛 → 衞  ·  綫 → 線", 26, INK, 600))
    b.append(t(60, 414, "Inherited forms become the forms used in Hong Kong.", 14, MUTED))
    b.append(t(60, 434, "Keeps Big5 code points 戶 說 稅, like HK websites.", 14, MUTED))

    b.append(arrow(320, 454, 320, 492))

    # result
    b.append(t(40, 520, "6  macOS-style candidate window", 15, INK, 700))
    bar, _ = candidate_bar(40, 540, ["雪櫃", "冰箱", "並向", "病象", "兵餉"])
    b.append(bar)
    b.append(t(560, 570, "Space → 雪櫃      2 → 冰箱", 18, INK, 600, font=FONT))
    b.append(t(560, 596, "Rime remembers what you choose and ranks it higher next time.", 14, MUTED))
    return svg(W, H, "\n".join(b))


# ── 2. Hong Kong conventions ────────────────────────────────────────
def hk_style():
    W, H = 1240, 600
    b = [t(40, 52, "What makes it Hong Kong style", 26, weight=700),
         t(40, 82, "Same Hanyu Pinyin input; the output follows Hong Kong practice.", 16, MUTED)]
    cards = [
        ("字形  Characters", ORANGE, ORANGE_BG,
         [("爲", "為"), ("衛生", "衞生"), ("綫", "線"), ("檯", "枱"), ("啓", "啟")],
         "As in HK schools, papers, gov.hk"),
        ("詞彙  Vocabulary", GREEN, GREEN_BG,
         [("軟體", "軟件"), ("網路", "網絡"), ("計程車", "的士"), ("冰箱", "雪櫃"), ("什麼", "甚麼")],
         "+ 嘅 咗 佢哋 唔該 · 港鐵 · 旺角"),
        ("標點  Punctuation", ACCENT, ACCENT_BG,
         [("[  ]", "「  」"), ("{  }", "『  』"), ("\\", "、"), ("^", "……"), ("_", "——")],
         "\" and ' pair up: 「…」 『…』"),
        ("日期  Dates", PURPLE, PURPLE_BG,
         [("rq", "2026年10月19日"), ("rq", "19/10/2026"), ("sj", "下午3:05"), ("xq", "星期一"), ("dt", "日期＋時間")],
         "Day/month/year · 上午 / 下午"),
    ]
    cw, gap = 278, 16
    for i, (title, col, bg, rows, foot) in enumerate(cards):
        x = 40 + i * (cw + gap)
        b.append(box(x, 110, cw, 450, BG, RULE))
        b.append(f'<path d="M{x},{124} a14,14 0 0 1 14,-14 h{cw - 28} a14,14 0 0 1 14,14 v44 h-{cw} z" fill="{bg}"/>')
        b.append(t(x + 20, 148, title, 18, col, 700))
        b.append(t(x + 20, 196, ["other IMEs  →  港式拼音", "other IMEs  →  港式拼音", "key  →  gives", "type  →  gives"][i], 12.5, MUTED))
        for j, (a, z) in enumerate(rows):
            y = 220 + j * 58
            left = a
            b.append(t(x + 20, y + 22, left, 20 if i != 3 else 18, MUTED,
                       font=MONO if i >= 2 else FONT, extra='text-decoration="line-through"' if i < 2 else ""))
            b.append(t(x + 112 if i != 3 else x + 70, y + 22, "→", 18, MUTED))
            b.append(t(x + 140 if i != 3 else x + 96, y + 22, z, 22 if i != 3 else 19, INK, 600))
            if j < len(rows) - 1:
                b.append(f'<line x1="{x + 20}" y1="{y + 40}" x2="{x + cw - 20}" y2="{y + 40}" stroke="{RULE}" stroke-width="1"/>')
        b.append(t(x + 20, 540, foot, 12.5, MUTED))
    return svg(W, H, "\n".join(b))


# ── 3. keys ─────────────────────────────────────────────────────────
def keycap(x, y, label, w=None, fill="#fff"):
    w = w or max(46, 14 + 10 * len(label))
    return (box(x, y, w, 42, fill, "#c7c7cc", r=8, sw=1.2, extra='filter="url(#sh)"')
            + t(x + w / 2, y + 27, label, 15, INK, 600, "middle", MONO)), w


def keys():
    W, H = 1240, 470
    b = [t(40, 52, "Keys (same habits as macOS)", 26, weight=700)]
    rows = [
        (["Ctrl", "Space"], "Switch English ⇄ 港式拼音", "like macOS"),
        (["Shift"], "Toggle English while typing; typed letters go in as English", ""),
        (["Space", "1", "…", "9"], "Choose a candidate", ""),
        (["-", "=", "Tab"], "Previous / next page of candidates", ""),
        (["Ctrl", "`"], "Options: 香港字形 · 香港詞彙 · 全形 · 標點", "or F4"),
        (["Enter"], "Enter the letters as typed (for English words)", ""),
    ]
    y = 90
    for ks, desc, note in rows:
        x = 40
        for k in ks:
            if k == "…":
                b.append(t(x + 6, y + 28, "…", 18, MUTED)); x += 30; continue
            cap, w = keycap(x, y, k)
            b.append(cap); x += w + 10
        b.append(t(330, y + 28, desc, 17, INK))
        if note:
            b.append(t(1200, y + 28, note, 14, MUTED, anchor="end"))
        y += 60
    return svg(W, H, "\n".join(b))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("how-it-works", how_it_works), ("hk-style", hk_style), ("keys", keys)):
        s = OUT / f"{name}.svg"
        s.write_text(fn(), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-z", "2", "-o", str(OUT / f"{name}.png"), str(s)], check=True)
        print("wrote", s.relative_to(ROOT), "and .png")


if __name__ == "__main__":
    main()
