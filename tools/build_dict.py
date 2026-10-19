#!/usr/bin/env python3
"""Build rime/hk_pinyin.hk_terms.dict.yaml from tools/hk_terms.src."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "hk_terms.src"
OUT = ROOT / "rime" / "hk_pinyin.hk_terms.dict.yaml"
DEFAULT_WEIGHT = 40000
SYLLABLE = re.compile(r"^[a-z]+$")

HEADER = """# Rime dictionary
# encoding: utf-8
#
# 港式拼音 — Hong Kong vocabulary (generated from tools/hk_terms.src;
# edit that file and run tools/build_dict.py, do not edit by hand).

---
name: hk_pinyin.hk_terms
version: "1.0.0"
sort: by_weight
use_preset_vocabulary: false
...

"""


def main() -> int:
    rows, seen, errors = [], set(), []
    for n, line in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) not in (2, 3):
            errors.append(f"line {n}: expected 2 or 3 fields: {line}")
            continue
        word, code = parts[0], " ".join(parts[1].split())
        weight = int(parts[2]) if len(parts) == 3 and parts[2] else DEFAULT_WEIGHT
        sylls = code.split(" ")
        if len(sylls) != len(word):
            errors.append(f"line {n}: {word} has {len(word)} chars but {len(sylls)} syllables")
        if not all(SYLLABLE.match(s) for s in sylls):
            errors.append(f"line {n}: bad pinyin '{code}'")
        if (word, code) in seen:
            continue
        seen.add((word, code))
        rows.append(f"{word}\t{code}\t{weight}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    OUT.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} entries to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
