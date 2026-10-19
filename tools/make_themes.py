#!/usr/bin/env python3
"""Generate the macOS-style fcitx5 themes (light and dark) into themes/.

Run:  python3 tools/make_themes.py      (needs python3-pil)
"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SS = 4                       # supersampling factor for smooth edges

SHADOW = 14                  # px of drop shadow around the panel
RADIUS = 11                  # panel corner radius
PANEL = 2 * (SHADOW + RADIUS) + 8
HL_RADIUS = 6
HL = 2 * HL_RADIUS + 8

THEMES = {
    "macos-light": dict(
        name="macOS Light (港式拼音)",
        panel=(251, 251, 253, 248), border=(0, 0, 0, 34), shadow=(0, 0, 0, 70),
        accent=(0, 122, 255, 255), text="#1d1d1f", hl_text="#ffffff",
        preedit_hl="#d6e6ff", preedit_hl_text="#0b3d91", arrow=(60, 60, 67, 150),
        menu_text="#1d1d1f", separator="#d9d9de",
    ),
    "macos-dark": dict(
        name="macOS Dark (港式拼音)",
        panel=(44, 44, 47, 248), border=(255, 255, 255, 38), shadow=(0, 0, 0, 140),
        accent=(10, 132, 255, 255), text="#f2f2f7", hl_text="#ffffff",
        preedit_hl="#1f3f6e", preedit_hl_text="#e6f0ff", arrow=(235, 235, 245, 150),
        menu_text="#f2f2f7", separator="#48484a",
    ),
}


def rounded(size, radius, fill, outline=None, inset=0):
    w, h = size
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = [inset * SS, inset * SS, (w - inset) * SS - 1, (h - inset) * SS - 1]
    d.rounded_rectangle(box, radius * SS, fill=fill,
                        outline=outline, width=SS if outline else 0)
    return img.resize((w, h), Image.LANCZOS)


def panel(t):
    size = (PANEL, PANEL)
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    # soft shadow, slightly offset downwards like macOS
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [SHADOW, SHADOW + 3, PANEL - SHADOW - 1, PANEL - SHADOW + 2],
        RADIUS, fill=t["shadow"])
    sh = sh.filter(ImageFilter.GaussianBlur(SHADOW / 2.6))
    base.alpha_composite(sh)
    base.alpha_composite(rounded(size, RADIUS, t["panel"], t["border"], inset=SHADOW))
    return base


def chevron(t, direction):
    s = 16
    img = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if direction == "next":
        pts = [(6, 3.5), (10.5, 8), (6, 12.5)]
    else:
        pts = [(10, 3.5), (5.5, 8), (10, 12.5)]
    d.line([(x * SS, y * SS) for x, y in pts], fill=t["arrow"], width=int(1.8 * SS), joint="curve")
    return img.resize((s, s), Image.LANCZOS)


def radio(t):
    s = 16
    img = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(3.5 * SS, 8.5 * SS), (6.8 * SS, 11.8 * SS), (12.5 * SS, 4.5 * SS)],
           fill=t["accent"], width=int(2 * SS), joint="curve")
    return img.resize((s, s), Image.LANCZOS)


def hexa(rgba):
    r, g, b, a = rgba
    return f"#{a:02x}{r:02x}{g:02x}{b:02x}"


CONF = """[Metadata]
Name={name}
Version=1
Author=hk-pinyin-ime
Description=macOS-style candidate window for 港式拼音
ScaleWithDPI=True

[InputPanel]
Font=Noto Sans CJK HK 13
NormalColor={text}
HighlightCandidateColor={hl_text}
HighlightColor={preedit_hl_text}
HighlightBackgroundColor={preedit_hl}
EnableBlur=True
Spacing=2
PageButtonAlignment=Last Candidate

[InputPanel/TextMargin]
Left=9
Right=9
Top=6
Bottom=6

[InputPanel/ContentMargin]
Left={cm}
Right={cm}
Top={cmt}
Bottom={cmb}

[InputPanel/ShadowMargin]
Left={sh}
Right={sh}
Top={sh}
Bottom={sh}

[InputPanel/BlurMargin]
Left={sh}
Right={sh}
Top={sh}
Bottom={sh}

[InputPanel/Background]
Image=panel.png

[InputPanel/Background/Margin]
Left={pm}
Right={pm}
Top={pm}
Bottom={pm}

[InputPanel/Highlight]
Image=highlight.png

[InputPanel/Highlight/Margin]
Left={hm}
Right={hm}
Top={hm}
Bottom={hm}

[InputPanel/Highlight/HighlightClickMargin]
Left=1
Right=1
Top=1
Bottom=1

[InputPanel/PrevPage]
Image=prev.png

[InputPanel/PrevPage/ClickMargin]
Left=4
Right=2
Top=4
Bottom=4

[InputPanel/NextPage]
Image=next.png

[InputPanel/NextPage/ClickMargin]
Left=2
Right=4
Top=4
Bottom=4

[Menu]
NormalColor={menu_text}
HighlightCandidateColor={hl_text}
Spacing=0

[Menu/Background]
Image=panel.png

[Menu/Background/Margin]
Left={pm}
Right={pm}
Top={pm}
Bottom={pm}

[Menu/ContentMargin]
Left={cm}
Right={cm}
Top={cmt}
Bottom={cmb}

[Menu/ShadowMargin]
Left={sh}
Right={sh}
Top={sh}
Bottom={sh}

[Menu/Highlight]
Image=highlight.png

[Menu/Highlight/Margin]
Left={hm}
Right={hm}
Top={hm}
Bottom={hm}

[Menu/Separator]
Color={separator}

[Menu/CheckBox]
Image=radio.png

[Menu/SubMenu]
Image=next.png

[Menu/TextMargin]
Left=8
Right=8
Top=6
Bottom=6
"""


def main():
    for tid, t in THEMES.items():
        out = ROOT / "themes" / tid
        out.mkdir(parents=True, exist_ok=True)
        panel(t).save(out / "panel.png")
        rounded((HL, HL), HL_RADIUS, t["accent"]).save(out / "highlight.png")
        chevron(t, "prev").save(out / "prev.png")
        chevron(t, "next").save(out / "next.png")
        radio(t).save(out / "radio.png")
        (out / "theme.conf").write_text(CONF.format(
            cm=SHADOW + 5, cmt=SHADOW + 5, cmb=SHADOW + 5, sh=SHADOW,
            pm=SHADOW + RADIUS, hm=HL_RADIUS + 1, **t), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
