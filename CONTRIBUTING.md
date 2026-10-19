# Contributing

Thank you for helping make 港式拼音 better for Hong Kong users.

## Suggest a word (no coding needed)

Open an issue with the **Word suggestion** template and tell us:

- the pinyin you typed (e.g. `chaguan`)
- what you got, and what Hong Kong people actually write (e.g. 差館)
- where it is used, if helpful (government, food, a district …)

## Add words yourself

1. Edit [`tools/hk_terms.src`](tools/hk_terms.src). One entry per line:

   ```
   詞語 | pin yin | weight
   ```

   - pinyin: no tones, one syllable per character, separated by spaces, `v` for ü
   - weight is optional (default 40000). Use 60000–90000 for words that should beat
     homophones, and 2000–10000 when a very common word shares the pinyin
     (e.g. 西環 `xi huan` must not beat 喜歡).

2. For "say it the Hong Kong way" replacements (軟體 → 軟件), add a line to
   [`rime/opencc/hk_terms.txt`](rime/opencc/hk_terms.txt): `from<Tab>to`.
   Be careful with short entries — they also match inside longer words.

3. Rebuild and test:

   ```bash
   python3 tools/build_dict.py
   tests/run_tests.sh
   ```

4. If your word matters, add a case to `CASES` in [`tests/run_tests.sh`](tests/run_tests.sh).

## Code changes

- Shell scripts must pass `shellcheck -S warning`.
- Keep `install.sh` safe to run twice and never overwrite a user's
  `hk_pinyin.user_terms.dict.yaml` or `hk_pinyin.custom.yaml` (except the documented no-Lua fallback).
- If you change images or themes, regenerate them with the scripts in `tools/` rather than
  editing the PNGs by hand.

## Pull requests

One topic per pull request, with a short description of what changes for the user.
The **Tests** workflow must pass.
