# Changelog

## 1.0.0 — 2026-10-19

First release.

- Rime schema `hk_pinyin` (港式拼音) on luna_pinyin, for fcitx5
- Hong Kong character forms (為 衞 線 枱 …), keeping Big5 code points 戶 說 稅
- 376 Hong Kong words: government, housing, transport, ~70 districts, food, written Cantonese
- Vocabulary filter: HK term first, original kept as next candidate (冰箱 → 雪櫃 | 冰箱)
- Hong Kong punctuation 「」『』、……——
- `rq` `sj` `xq` `dt` dates and times in Hong Kong formats
- macOS-style light and dark candidate windows
- Installer with backup, uninstaller, fallback for systems without librime-lua
- 26 automated typing tests, GitHub Actions workflow
- Guide (Markdown) and manual (PDF + LaTeX)
